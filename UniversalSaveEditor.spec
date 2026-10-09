# Build on Windows: python -m PyInstaller --clean --noconfirm UniversalSaveEditor.spec
from pathlib import Path
root=Path(SPECPATH)
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
