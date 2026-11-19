# Third-party components

The Windows distribution dynamically bundles Python 3.13.14, PySide6/Qt 6.11.2,
Shiboken 6.11.2 and the PyInstaller 6.22.3 bootloader. These components retain
their upstream copyrights and licenses. This application's source is supplied
alongside the executable. Qt DLLs remain separate in `_internal`.

Upstream sources and license information:

- Python: https://www.python.org/downloads/source/ and https://github.com/python/cpython
- Qt 6.11.2: https://download.qt.io/archive/qt/6.11/6.11.2/ and https://code.qt.io/cgit/qt/
- PySide6 and Shiboken: https://code.qt.io/cgit/pyside/pyside-setup.git/ (v6.11.2)
- PyInstaller: https://github.com/pyinstaller/pyinstaller/tree/v6.22.3
- Qt third-party attributions: https://doc.qt.io/qt-6/licenses-used-in-qt.html

PySide6_Essentials package metadata declares LGPL-3.0-only OR GPL-2.0-only OR
GPL-3.0-only. The LGPL/GPL texts and Python/PyInstaller notices are included
here; the wheel's own license notices and metadata are also retained in
`_internal`. Qt's commercial license notice describes the alternative
commercial licensing route and does not imply this application requires a
paid license.

Replace or relink the separately distributed libraries in accordance with
their licenses. No application restriction is intended to prevent reverse
engineering for debugging modifications to LGPL-covered libraries. Consult
the upstream source packages for all component-specific third-party notices.
