"""Portable Windows update handoff; touches application files only.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from pathlib import Path
import ctypes
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time


def update_root():return Path(tempfile.gettempdir())/'UniversalSaveEditor-updates'


def stage_for(manifest):
    manifest=Path(manifest)
    if manifest.name!='update.json' or manifest.is_symlink() or manifest.parent.is_symlink():raise ValueError('Invalid update location.')
    stage=manifest.parent.resolve(strict=True);root=update_root()
    if root.is_symlink() or stage.parent!=root.resolve() or not re.fullmatch(r'update-[a-z0-9_]{8}',stage.name):
        raise ValueError('Invalid update location.')
    return stage


def file_digest(path):
    with Path(path).open('rb') as source:return hashlib.file_digest(source,'sha256').hexdigest()


def prepare_install(source,checksum,target,pid):
    source,target=Path(source),Path(target)
    manifest=source.parent/'update.json';stage=stage_for(manifest)
    if source.name!='UniversalSaveEditor.exe' or source.is_symlink() or source.parent.resolve()!=stage:
        raise ValueError('Invalid update executable.')
    if not re.fullmatch(r'[0-9a-f]{64}',checksum):raise ValueError('Invalid update checksum.')
    if target.is_symlink() or not target.is_file() or target.suffix.lower()!='.exe' or target.parent.resolve()==stage:
        raise ValueError('Invalid installed application path.')
    target=target.resolve();stat=target.stat()
    # Check ordinary write access before the running application closes.
    fd,probe=tempfile.mkstemp(prefix='.UniversalSaveEditor-update-',dir=target.parent)
    os.close(fd);Path(probe).unlink()
    document={'protocol':1,'source':str(source.resolve()),'target':str(target),'sha256':checksum,
              'pid':pid,'old_size':stat.st_size,'old_mtime':stat.st_mtime_ns}
    manifest.write_text(json.dumps(document),encoding='utf-8')
    return manifest


def launch_helper(source,manifest):
    return subprocess.Popen([str(source),'--apply-update',str(manifest)],close_fds=True,
                            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))


def wait_for_application(pid,target):
    """Wait only for the process belonging to the intended old executable."""
    from ctypes import wintypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes=(wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD))
    kernel.WaitForSingleObject.argtypes=(wintypes.HANDLE,wintypes.DWORD);kernel.WaitForSingleObject.restype=wintypes.DWORD
    kernel.CloseHandle.argtypes=(wintypes.HANDLE,)
    handle=kernel.OpenProcess(0x100000|0x1000,False,pid)
    if not handle:
        if ctypes.get_last_error()==87:return
        raise OSError('Could not wait for the running application.')
    try:
        buffer=ctypes.create_unicode_buffer(32768);length=wintypes.DWORD(len(buffer))
        if not kernel.QueryFullProcessImageNameW(handle,0,buffer,ctypes.byref(length)) or Path(buffer.value).resolve()!=target:
            raise ValueError('The running application does not match this update.')
        if kernel.WaitForSingleObject(handle,60000)!=0:raise OSError('The running application did not close.')
    finally:kernel.CloseHandle(handle)


def apply_install(manifest,wait=None,launch=None,helper=None):
    """Validate again in the helper, copy on target volume, then atomically replace."""
    stage=stage_for(manifest)
    if Path(manifest).stat().st_size>8192:raise ValueError('Invalid update manifest.')
    document=json.loads(Path(manifest).read_text(encoding='utf-8'))
    if not isinstance(document,dict) or document.get('protocol')!=1:raise ValueError('Unsupported update protocol.')
    source=stage/'UniversalSaveEditor.exe';target=Path(document.get('target',''))
    if source.is_symlink() or source.resolve()!=Path(document.get('source','')).resolve() or source.resolve()!=Path(helper or sys.executable).resolve():
        raise ValueError('The helper does not match the verified download.')
    if target.is_symlink() or not target.is_file() or target.suffix.lower()!='.exe' or target.parent.resolve()==stage:
        raise ValueError('Invalid update destination.')
    target=target.resolve();pid=document.get('pid');checksum=document.get('sha256','')
    if type(pid) is not int or not 0<pid<=0xffffffff or not re.fullmatch('[a-f0-9]{64}',checksum):raise ValueError('Invalid update identity.')
    if file_digest(source)!=checksum:raise ValueError('The downloaded application changed before installation.')
    with source.open('rb') as stream:
        if stream.read(2)!=b'MZ':raise ValueError('The download is not a Windows executable.')
    (wait or wait_for_application)(pid,target)
    stat=target.stat()
    if stat.st_size!=document.get('old_size') or stat.st_mtime_ns!=document.get('old_mtime'):
        raise ValueError('The installed application changed before the update.')
    backup=stage/'previous.exe'
    if backup.exists():raise ValueError('This update was already applied.')
    shutil.copyfile(target,backup)
    fd,temporary=tempfile.mkstemp(prefix='.UniversalSaveEditor-update-',suffix='.exe',dir=target.parent)
    os.close(fd);temporary=Path(temporary);replaced=False
    try:
        shutil.copyfile(source,temporary)
        if file_digest(temporary)!=checksum:raise ValueError('The update copy did not pass verification.')
        for attempt in range(51):
            current=target.stat()
            if (current.st_size,current.st_mtime_ns)!=(stat.st_size,stat.st_mtime_ns):raise ValueError('The installed application changed before replacement.')
            try:os.replace(temporary,target);break
            except PermissionError:
                # A frozen Windows app has an outer bootloader that may release
                # its executable just after the old GUI process has exited.
                if attempt==50:raise
                time.sleep(0.1)
        replaced=True
        if launch:launch(target,Path(manifest))
        else:subprocess.Popen([str(target),'--finish-update',str(manifest)],close_fds=True,
                              creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    except Exception:
        if replaced:
            shutil.copyfile(backup,temporary);os.replace(temporary,target)
        raise
    finally:temporary.unlink(missing_ok=True)


def finish_install(manifest,executable=None):
    """Remove only the known files in this handoff's exact cache directory."""
    stage=stage_for(manifest)
    if Path(manifest).stat().st_size>8192:raise ValueError('Invalid update manifest.')
    document=json.loads(Path(manifest).read_text(encoding='utf-8'))
    if Path(document['target']).resolve()!=Path(executable or sys.executable).resolve():raise ValueError('Update destination mismatch.')
    names={'update.json','UniversalSaveEditor.exe','previous.exe'}
    if any(p.name not in names or p.is_symlink() or not p.is_file() for p in stage.iterdir()):raise ValueError('Unexpected update cache contents.')
    # The helper may still be exiting; keep the manifest for a later retry.
    for name in ('UniversalSaveEditor.exe','previous.exe'):(stage/name).unlink(missing_ok=True)
    Path(manifest).unlink();stage.rmdir()


def helper_main(manifest):
    try:apply_install(manifest);return 0
    except Exception:
        if sys.platform=='win32':
            ctypes.windll.user32.MessageBoxW(None,
                'The update could not be completed. Download the latest release and replace the application manually. Your save files were not changed.',
                'UniversalSaveEditor update',0x10)
        return 1
