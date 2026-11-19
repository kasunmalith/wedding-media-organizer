# Single-file portable Windows distribution. No installed Python required.
from pathlib import Path
import os
import sys
from PyInstaller.utils.hooks import copy_metadata

root = Path(SPECPATH)
# Build tools can inherit unrelated native-library folders (e.g. Poppler ICU).
# Restrict dependency search to this Python and Windows; Qt's hook supplies Qt.
os.environ['PATH'] = os.pathsep.join([str(Path(sys.executable).parent), sys.base_prefix,
                                     str(Path(os.environ['SystemRoot']) / 'System32'),
                                     os.environ['SystemRoot']])
notices = [(str(root / 'third_party'), 'third_party')]
for package in ('PySide6_Essentials', 'shiboken6'):
    notices += copy_metadata(package)
a = Analysis([str(root / 'main.py')], pathex=[str(root)], binaries=[], datas=notices,
             hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
             excludes=['tkinter', 'pytest'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='WeddingMediaOrganizer',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, disable_windowed_traceback=False, icon=str(root / 'assets/eon.ico'),
          manifest=str(root / 'windows.manifest'))

