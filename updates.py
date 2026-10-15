"""Official-release checks and bounded, asynchronous verified downloads.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import re
import tempfile
from PySide6.QtCore import QObject,QTimer,QUrl,Signal
from PySide6.QtNetwork import QNetworkAccessManager,QNetworkRequest,QNetworkReply

REPOSITORY='DanCarrillo11/UniversalSaveEditor'
RELEASES='https://github.com/'+REPOSITORY+'/releases'
LATEST_API='https://api.github.com/repos/'+REPOSITORY+'/releases/latest'
MAX_EXE=200*1024*1024
DOWNLOAD_HOSTS={'github.com','release-assets.githubusercontent.com','objects.githubusercontent.com'}


def version_parts(value):
    match=re.fullmatch(r'v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z.-]+)?',value)
    if not match:raise ValueError('Unrecognized release version.')
    major,minor,patch,pre=match.groups()
    identifiers=tuple((0,int(s)) if s.isdigit() else (1,s) for s in pre.split('.')) if pre else ()
    return int(major),int(minor),int(patch),int(pre is None),identifiers


def trusted_download(url):
    try:
        parsed=urlsplit(url)
        return (parsed.scheme=='https' and parsed.hostname in DOWNLOAD_HOSTS and
                parsed.port in (None,443) and not parsed.username and not parsed.password and not parsed.fragment)
    except ValueError:return False


@dataclass(frozen=True)
class Release:
    version:str
    page:str
    executable:str
    checksums:str
    size:int
    digest:str
    notes:str


def parse_release(payload):
    if not isinstance(payload,dict) or payload.get('draft') is not False or payload.get('prerelease') is not False:
        raise ValueError('No published release was found.')
    tag=payload.get('tag_name','');version_parts(tag)
    prefix=RELEASES+'/download/'+tag+'/'
    page=RELEASES+'/tag/'+tag
    if payload.get('html_url')!=page:raise ValueError('The release is not from the official repository.')
    assets=payload.get('assets')
    if not isinstance(assets,list) or len(assets)>100:raise ValueError('The release asset list is invalid.')
    selected={}
    for name in ('UniversalSaveEditor.exe','SHA256SUMS.txt'):
        found=[a for a in assets if isinstance(a,dict) and a.get('name')==name]
        if len(found)!=1:raise ValueError('The release does not contain the expected Windows download.')
        item=found[0]
        if item.get('state')!='uploaded' or item.get('browser_download_url')!=prefix+name:
            raise ValueError('The release download is not ready or is not official.')
        size=item.get('size')
        if type(size) is not int or not 0<size<=(MAX_EXE if name.endswith('.exe') else 16384):
            raise ValueError('The release download has an unsupported size.')
        selected[name]=item
    exe=selected['UniversalSaveEditor.exe'];digest=exe.get('digest') or ''
    if digest and not re.fullmatch('sha256:[0-9a-fA-F]{64}',digest):raise ValueError('Unsupported release digest.')
    return Release(tag.removeprefix('v'),page,exe['browser_download_url'],selected['SHA256SUMS.txt']['browser_download_url'],
                   exe['size'],digest.removeprefix('sha256:').lower(),str(payload.get('body') or '')[:20000])


def checksum_for_exe(data):
    if len(data)>16384:raise ValueError('The checksum file is too large.')
    try:lines=data.decode('ascii').splitlines()
    except UnicodeDecodeError:raise ValueError('The checksum file is invalid.') from None
    matches=[m[1].lower() for line in lines if (m:=re.fullmatch(r'([a-fA-F0-9]{64})[ \t]+\*?UniversalSaveEditor\.exe',line.strip()))]
    if len(matches)!=1:raise ValueError('The executable checksum is missing or ambiguous.')
    return matches[0]


def cache_root():return Path(tempfile.gettempdir())/'UniversalSaveEditor-updates'


class UpdateClient(QObject):
    changed=Signal()
    checked=Signal(object)
    def __init__(self,current,parent=None,manager=None):
        super().__init__(parent);self.current=current
        self.manager=manager or QNetworkAccessManager(self)
        self.reply=None;self.state='idle';self.message='Check the official release when you are ready.'
        self.release=None;self.received=0;self.expected=0;self.staging=None;self.downloaded=None
        self.buffer=bytearray();self.output=None;self.sha=None;self.checksum='';self.kind='';self.redirects=0
        self.deadline=QTimer(self);self.deadline.setSingleShot(True);self.deadline.timeout.connect(self._timeout)

    @property
    def busy(self):return self.reply is not None

    def check(self):
        if self.busy:return
        self._discard_download()
        self.state='checking';self.message='Checking the official GitHub release…';self.changed.emit()
        self._request(LATEST_API,'release')

    def download(self):
        if self.busy or self.release is None or version_parts(self.release.version)<=version_parts(self.current):return
        self._discard_download();self.state='downloading';self.message='Downloading the checksum…'
        self.received=0;self.expected=self.release.size;self.changed.emit();self._request(self.release.checksums,'checksum')

    def _request(self,url,kind,redirect=False):
        if url!=LATEST_API and not trusted_download(url):self._fail('The download redirected outside the approved GitHub hosts.');return
        if not redirect:self.redirects=0
        self.kind=kind;self.buffer=bytearray()
        request=QNetworkRequest(QUrl(url));request.setRawHeader(b'User-Agent',b'UniversalSaveEditor/'+self.current.encode('ascii'))
        request.setRawHeader(b'Accept',b'application/vnd.github+json' if kind=='release' else b'application/octet-stream')
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,QNetworkRequest.RedirectPolicy.ManualRedirectPolicy)
        request.setTransferTimeout(60000 if kind=='executable' else 15000)
        reply=self.manager.get(request);self.reply=reply;reply.setReadBufferSize(256*1024)
        reply.readyRead.connect(lambda:self._consume(reply));reply.finished.connect(lambda:self._finished(reply))
        self.deadline.start(600000 if kind=='executable' else 30000)

    def _consume(self,reply):
        if reply is not self.reply:return
        status=reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status in (301,302,303,307,308):reply.readAll();return
        data=bytes(reply.readAll())
        if self.kind=='executable':
            if self.received+len(data)>self.expected:self._fail('The download exceeded the release size.');return
            try:self.output.write(data)
            except OSError:self._fail('The update could not be written. Check the available disk space.');return
            self.sha.update(data);self.received+=len(data);self.changed.emit()
        else:
            self.buffer.extend(data)
            if len(self.buffer)>(1024*1024 if self.kind=='release' else 16384):self._fail('The update response exceeded the supported size.')

    def _finished(self,reply):
        if reply is not self.reply:reply.deleteLater();return
        self._consume(reply)
        if reply is not self.reply:reply.deleteLater();return
        self.deadline.stop();self.reply=None
        status=reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        redirect=reply.attribute(QNetworkRequest.Attribute.RedirectionTargetAttribute)
        error=reply.error();reply.deleteLater()
        if status in (301,302,303,307,308) and redirect:
            self.redirects+=1
            url=reply.url().resolved(redirect).toString()
            if self.redirects>5 or not trusted_download(url) or self.kind=='release':self._fail('The update redirected to an unsupported location.');return
            self._request(url,self.kind,True);return
        if error!=QNetworkReply.NetworkError.NoError or status!=200:
            self._fail('GitHub is temporarily limiting update checks. Try again later.' if status in (403,429) else 'Could not reach the official release. Check your connection and try again.');return
        try:
            if self.kind=='release':
                release=parse_release(json.loads(self.buffer));self.release=release
                newer=version_parts(release.version)>version_parts(self.current)
                self.state='available' if newer else 'current'
                self.message='Version '+release.version+' is available.' if newer else 'You are using the latest available version.'
                self.changed.emit();self.checked.emit(release if newer else None)
            elif self.kind=='checksum':
                self.checksum=checksum_for_exe(self.buffer)
                if self.release.digest and self.release.digest!=self.checksum:raise ValueError('The release checksum and asset digest disagree.')
                root=cache_root()
                if root.is_symlink():raise ValueError('The update cache is not a regular directory.')
                root.mkdir(parents=True,exist_ok=True)
                self.staging=Path(tempfile.mkdtemp(prefix='update-',dir=root));self.downloaded=self.staging/'UniversalSaveEditor.exe'
                self.output=self.downloaded.open('xb');self.sha=hashlib.sha256();self.received=0
                self.message='Downloading UniversalSaveEditor…';self.changed.emit();self._request(self.release.executable,'executable')
            else:
                output,self.output=self.output,None;output.close()
                if self.received!=self.expected or self.sha.hexdigest()!=self.checksum:raise ValueError('The download failed its integrity check. Try downloading again.')
                with self.downloaded.open('rb') as source:
                    if source.read(2)!=b'MZ':raise ValueError('The release download is not a Windows executable.')
                self.state='ready';self.message='Download verified. Ready to update.';self.changed.emit()
        except (ValueError,TypeError,KeyError,UnicodeError,OSError):
            self._fail('The official update could not be verified. Try again later or use the Releases page.')

    def _timeout(self):self._fail('The update request timed out. Check your connection and try again.')

    def _fail(self,message):
        self._abort();self._discard_download();self.state='error';self.message=message;self.changed.emit()

    def _abort(self):
        self.deadline.stop();reply=self.reply;self.reply=None
        if reply is not None:reply.abort();reply.deleteLater()

    def _discard_download(self):
        if self.output is not None:
            output,self.output=self.output,None
            try:output.close()
            except OSError:pass
        if self.staging is not None:
            try:
                if not self.staging.is_symlink() and not cache_root().is_symlink() and self.staging.parent.resolve()==cache_root().resolve():
                    for name in ('UniversalSaveEditor.exe','update.json','previous.exe'):(self.staging/name).unlink(missing_ok=True)
                    self.staging.rmdir()
            except OSError:pass
        self.staging=self.downloaded=None

    def cancel(self):
        self._abort();self._discard_download();self.state='idle';self.message='Update canceled. You can check again at any time.';self.changed.emit()
