"""Atomic application-only replacement, rollback and bounded cleanup."""
import hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from update_install import prepare_install,apply_install,finish_install,wait_for_application


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.cache=self.root/'updates';self.cache.mkdir()
        self.stage=Path(tempfile.mkdtemp(prefix='update-',dir=self.cache));self.source=self.stage/'UniversalSaveEditor.exe'
        self.target=self.root/'Installed app.exe';self.target.write_bytes(b'original application')
        self.source.write_bytes(b'MZ'+b'new application'*100);self.digest=hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.scope=patch('update_install.update_root',return_value=self.cache);self.scope.start()
        self.manifest=prepare_install(self.source,self.digest,self.target,12345)
        self.waited=[];self.launched=[]
    def tearDown(self):self.scope.stop();self.temp.cleanup()
    def apply(self,launch=None):
        apply_install(self.manifest,wait=lambda pid,target:self.waited.append((pid,target)),
                      launch=launch or (lambda target,manifest:self.launched.append((target,manifest))),helper=self.source)

    def test_replaces_only_the_app_and_successful_restart_removes_known_cache(self):
        save=self.root/'save.sl2';save.write_bytes(b'personal save');settings=self.root/'settings.ini';settings.write_bytes(b'preferences')
        self.apply();self.assertEqual(self.target.read_bytes(),self.source.read_bytes())
        self.assertEqual(self.waited,[(12345,self.target)]);self.assertEqual(self.launched,[(self.target,self.manifest)])
        self.assertEqual((self.stage/'previous.exe').read_bytes(),b'original application')
        self.assertEqual(save.read_bytes(),b'personal save');self.assertEqual(settings.read_bytes(),b'preferences')
        finish_install(self.manifest,executable=self.target);self.assertFalse(self.stage.exists())
        self.assertFalse(list(self.root.glob('.UniversalSaveEditor-update-*')))

    def test_changed_download_or_target_is_rejected_before_replacement(self):
        for mode in ('source','target'):
            original=self.target.read_bytes()
            if mode=='source':self.source.write_bytes(b'MZchanged')
            else:
                self.source.write_bytes(b'MZ'+b'new application'*100);self.target.write_bytes(b'external update')
                original=self.target.read_bytes()
            with self.assertRaises(ValueError):self.apply()
            self.assertEqual(self.target.read_bytes(),original);self.assertFalse(self.launched)

    def test_failed_restart_restores_the_previous_executable(self):
        def fail(target,manifest):raise OSError('Cannot launch')
        with self.assertRaises(OSError):self.apply(fail)
        self.assertEqual(self.target.read_bytes(),b'original application')
        self.assertFalse(list(self.root.glob('.UniversalSaveEditor-update-*')))

    def test_manifest_cannot_select_a_save_file_or_an_unrelated_cache_directory(self):
        document=json.loads(self.manifest.read_text());save=self.root/'save.sl2';save.write_bytes(b'keep')
        document['target']=str(save);self.manifest.write_text(json.dumps(document))
        with self.assertRaises(ValueError):self.apply()
        self.assertEqual(save.read_bytes(),b'keep')
        other=self.root/'unrelated';other.mkdir();foreign=other/'update.json';foreign.write_text(json.dumps(document))
        with self.assertRaises(ValueError):apply_install(foreign,helper=self.source)

    def test_cleanup_refuses_foreign_files_and_destination_mismatch(self):
        foreign=self.stage/'personal.txt';foreign.write_bytes(b'keep')
        with self.assertRaises(ValueError):finish_install(self.manifest,executable=self.target)
        self.assertEqual(foreign.read_bytes(),b'keep');foreign.unlink()
        with self.assertRaises(ValueError):finish_install(self.manifest,executable=self.root/'wrong.exe')
        self.assertTrue(self.manifest.exists())

    def test_wait_failure_and_failed_copy_keep_the_old_app(self):
        def fail(pid,target):raise OSError('Process still running')
        with self.assertRaises(OSError):apply_install(self.manifest,wait=fail,helper=self.source)
        self.assertEqual(self.target.read_bytes(),b'original application')
        with patch('update_install.shutil.copyfile',side_effect=OSError('Disk full')):
            with self.assertRaises(OSError):self.apply()
        self.assertEqual(self.target.read_bytes(),b'original application')

    @unittest.skipUnless(sys.platform=='win32','Windows process identity API')
    def test_windows_wait_checks_identity_and_handles_a_real_exiting_process(self):
        process=subprocess.Popen([sys.executable,'-c','import time; time.sleep(0.5)'],creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            with self.assertRaises(ValueError):wait_for_application(process.pid,self.target)
            wait_for_application(process.pid,Path(sys.executable).resolve());process.wait(timeout=3)
        finally:
            if process.poll() is None:process.kill();process.wait()

    @unittest.skipUnless(sys.platform=='win32','Windows executable sharing')
    def test_transient_windows_file_lock_is_retried_without_overwriting_an_external_change(self):
        import ctypes,threading
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.CreateFileW.argtypes=(wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE)
        kernel.CreateFileW.restype=wintypes.HANDLE;kernel.CloseHandle.argtypes=(wintypes.HANDLE,)
        handle=kernel.CreateFileW(str(self.target),0x80000000,3,None,3,0,None)
        self.assertNotEqual(handle,ctypes.c_void_p(-1).value)
        timer=threading.Timer(0.2,lambda:kernel.CloseHandle(handle));timer.start()
        try:self.apply()
        finally:timer.join()
        self.assertEqual(self.target.read_bytes(),self.source.read_bytes())


if __name__=='__main__':unittest.main()
