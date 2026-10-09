# Build on Windows: python -m PyInstaller --clean --noconfirm UniversalSaveEditor.spec
from pathlib import Path
import os
import sys
root=Path(SPECPATH)
# Resolve DLLs only from this Python environment and Windows. Unrelated tools
# on PATH may supply an incompatible ICU/UCRT DLL with the same filename.
if sys.platform == 'win32':
    windows=Path(os.environ['SystemRoot'])
    os.environ['PATH']=os.pathsep.join(map(str,[Path(sys.executable).parent,
        Path(sys.base_prefix),windows/'System32',windows]))
a=Analysis([str(root/'app.py')], pathex=[str(root)], binaries=[],
    datas=[(str(root/'theme.qss'),'.'),(str(root/'README.md'),'.'),
           (str(root/'LICENSE'),'.'),(str(root/'SOURCES.md'),'.'),
           (str(root/'assets'),'assets')],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['PySide6.QtWebEngineCore','PySide6.QtWebEngineWidgets','PySide6.QtQml','PySide6.QtQuick'],
    noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name='UniversalSaveEditor',
    debug=False,bootloader_ignore_signals=False,strip=False,upx=False,
    console=False,disable_windowed_traceback=False)
