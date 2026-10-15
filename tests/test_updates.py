"""Official-origin, version ordering, async failure and verified download checks."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QObject,Signal,QByteArray,QUrl
from PySide6.QtNetwork import QNetworkRequest,QNetworkReply
from PySide6.QtWidgets import QApplication
from updates import UpdateClient,parse_release,version_parts,trusted_download,checksum_for_exe,LATEST_API,RELEASES

PAYLOAD=b'MZ'+bytes(2046)
DIGEST=hashlib.sha256(PAYLOAD).hexdigest()


def release(version='0.34.0-alpha'):
    prefix=RELEASES+'/download/v'+version+'/'
    return {'tag_name':'v'+version,'draft':False,'prerelease':False,'html_url':RELEASES+'/tag/v'+version,'body':'New features <script>plain text</script>',
        'assets':[{'name':n,'size':size,'state':'uploaded','browser_download_url':prefix+n,**({'digest':'sha256:'+DIGEST} if n.endswith('.exe') else {})}
            for n,size in (('UniversalSaveEditor.exe',len(PAYLOAD)),('SHA256SUMS.txt',91))]}


class Reply(QObject):
    readyRead=Signal();finished=Signal()
    def __init__(self,url):
        super().__init__();self.address=url;self.data=b'';self.status=200;self.redirect=None;self.failure=QNetworkReply.NetworkError.NoError;self.aborted=False
    def setReadBufferSize(self,size):pass
    def readAll(self):data,self.data=self.data,b'';return QByteArray(data)
    def url(self):return self.address
    def error(self):return self.failure
    def attribute(self,attr):
        return self.status if attr==QNetworkRequest.Attribute.HttpStatusCodeAttribute else self.redirect
    def abort(self):self.aborted=True;self.finished.emit()
    def feed(self,data):self.data+=data;self.readyRead.emit()
    def finish(self,data=b''):self.feed(data);self.finished.emit()


class Manager:
    def __init__(self):self.replies=[];self.requests=[]
    def get(self,request):
        self.requests.append(request);reply=Reply(request.url());self.replies.append(reply);return reply


class UpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'updates'
        self.cache=patch('updates.cache_root',return_value=self.root);self.cache.start()
        self.manager=Manager();self.client=UpdateClient('0.33.0-alpha',manager=self.manager)
    def tearDown(self):self.client.cancel();self.cache.stop();self.temp.cleanup()
    def available(self):self.client.check();self.manager.replies[-1].finish(json.dumps(release()).encode())
    def checksum(self):self.client.download();self.manager.replies[-1].finish((DIGEST+'  UniversalSaveEditor.exe\n').encode())

    def test_semver_orders_numeric_components_prereleases_and_stable_versions(self):
        versions=['0.9.0-alpha','0.10.0-alpha','0.33.0-alpha.2','0.33.0-alpha.10','0.33.0-beta','0.33.0','1.0.0-alpha']
        self.assertEqual(sorted(reversed(versions),key=version_parts),versions)
        self.assertEqual(version_parts('v1.2.3+build.4'),version_parts('1.2.3'))
        for bad in ('nightly','v1.2','1.02.3','1.2.3/../../','1.2.3-alpha & shutdown'):
            with self.subTest(bad=bad),self.assertRaises(ValueError):version_parts(bad)

    def test_metadata_requires_exact_official_assets_and_uploaded_normal_release(self):
        self.assertEqual(parse_release(release()).size,len(PAYLOAD))
        cases=[]
        for key,value in (('draft',True),('prerelease',True),('html_url','https://evil.invalid/release')):
            data=release();data[key]=value;cases.append(data)
        for key,value in (('browser_download_url','https://github.com/other/app.exe'),('size',True),('size',300*1024*1024),('state','new'),('digest','md5:123')):
            data=release();data['assets'][0][key]=value;cases.append(data)
        data=release();data['assets'].append(data['assets'][0].copy());cases.append(data)
        for data in cases:
            with self.assertRaises(ValueError):parse_release(data)
        for url in ('http://github.com/a','https://github.com.evil.invalid/a','https://github.com:wrong/a','https://user@github.com/a','file:///app.exe'):
            self.assertFalse(trusted_download(url))

    def test_no_network_until_explicit_check_and_plain_metadata_can_be_retried(self):
        self.assertFalse(self.manager.requests);self.client.check()
        self.assertEqual(self.manager.requests[0].url().toString(),LATEST_API)
        self.manager.replies[-1].finish(b'not json');self.assertEqual(self.client.state,'error')
        self.available();self.assertEqual(self.client.state,'available');self.assertIn('0.34.0-alpha',self.client.message)
        self.assertIsNone(self.client.downloaded)

    def test_newer_download_stream_is_verified_before_becoming_ready(self):
        self.available();self.checksum();reply=self.manager.replies[-1]
        reply.feed(PAYLOAD[:100]);self.assertEqual(self.client.received,100);self.assertEqual(self.client.state,'downloading')
        reply.finish(PAYLOAD[100:]);self.assertEqual(self.client.state,'ready')
        self.assertEqual(self.client.downloaded.read_bytes(),PAYLOAD)
        self.assertEqual(self.client.sha.hexdigest(),DIGEST)
        folder=self.client.staging;self.client.cancel();self.assertFalse(folder.exists())

    def test_bad_checksum_digest_truncation_and_oversize_remove_partial_downloads(self):
        for mode in ('checksum','digest','short','large','corrupt'):
            self.client.cancel();self.available()
            if mode=='digest':self.client.release=type(self.client.release)(**{**self.client.release.__dict__,'digest':'0'*64})
            self.client.download();self.manager.replies[-1].finish((('0'*64 if mode=='checksum' else DIGEST)+'  UniversalSaveEditor.exe\n').encode())
            if self.client.state!='error':
                payload=PAYLOAD[:10] if mode=='short' else PAYLOAD+b'!' if mode=='large' else PAYLOAD[:-1]+b'!' if mode=='corrupt' else PAYLOAD
                self.manager.replies[-1].finish(payload)
            with self.subTest(mode=mode):
                self.assertEqual(self.client.state,'error');self.assertIsNone(self.client.downloaded)
                self.assertFalse(list(self.root.glob('update-*')))

    def test_redirects_are_limited_to_https_github_asset_hosts(self):
        self.available();self.checksum();reply=self.manager.replies[-1]
        reply.status=302;reply.redirect=QUrl('https://release-assets.githubusercontent.com/signed?token=example');reply.finish()
        self.manager.replies[-1].finish(PAYLOAD);self.assertEqual(self.client.state,'ready')
        self.client.cancel();self.available();self.checksum();reply=self.manager.replies[-1]
        reply.status=302;reply.redirect=QUrl('https://other.invalid/payload');reply.finish()
        self.assertEqual(self.client.state,'error');self.assertIsNone(self.client.downloaded)

    def test_timeout_cancellation_and_http_errors_do_not_trigger_installation(self):
        self.available();self.checksum();reply=self.manager.replies[-1];reply.feed(PAYLOAD[:10]);folder=self.client.staging
        self.client.cancel();self.assertTrue(reply.aborted);self.assertFalse(folder.exists());self.assertEqual(self.client.state,'idle')
        self.client.check();self.client._timeout();self.assertEqual(self.client.state,'error')
        self.client.check();reply=self.manager.replies[-1];reply.status=403;reply.finish()
        self.assertIn('limiting',self.client.message)

    def test_current_and_older_releases_never_download_and_checksum_must_be_unambiguous(self):
        for version in ('0.33.0-alpha','0.32.0-alpha'):
            self.client.check();self.manager.replies[-1].finish(json.dumps(release(version)).encode())
            count=len(self.manager.requests);self.client.download();self.assertEqual(len(self.manager.requests),count)
            self.assertEqual(self.client.state,'current')
        for data in (b'x'*17000,(DIGEST+'  Wrong.exe\n').encode(),((DIGEST+'  UniversalSaveEditor.exe\n')*2).encode()):
            with self.assertRaises(ValueError):checksum_for_exe(data)


if __name__=='__main__':unittest.main()
