"""Packaged-app diagnostic: only creates and moves its own temporary dummy files."""
from pathlib import Path
import json
import os
import tempfile
import time
import traceback


def smoke_test(output: Path) -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    result = {"success": False}
    window = None
    app = None
    try:
        from PySide6.QtWidgets import QApplication
        from .gui import MainWindow
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory(prefix="WeddingOrganizer-smoke-") as temp:
            base = Path(temp)
            root = base / "Dummy Wedding"
            (root / "DCIM/100NIKON").mkdir(parents=True)
            (root / "DCIM/100NIKON/EML_1.NEF").write_bytes(b"dummy RAW")
            (root / "REC001.WAV").write_bytes(b"dummy audio")
            (root / "DCIM/100NIKON/metadata.xml").write_bytes(b"dummy metadata")
            (root / "NIKON/settings").mkdir(parents=True)
            (root / "NIKON/settings/camera.DAT").write_bytes(b"dummy settings")
            (root / "NIKON001.DSC").write_bytes(b"dummy camera index")
            (root / "DCIM/100NIKON/_MSP7396.NEF").write_bytes(b"dummy underscore RAW")
            os.environ["LOCALAPPDATA"] = str(base / "LocalAppData")
            window = MainWindow()
            assert 'Eon Episode' in window.windowTitle()
            assert not window.windowIcon().isNull()
            assert not window.logo_label.pixmap().isNull()
            assert 'https://www.energeticedge.lk/' in window.credit.text()
            problems = []
            window.on_problem = problems.append  # Diagnostics must not open blocking error dialogs.
            window.set_folder(root)
            window.start_scan()

            def wait():
                deadline = time.monotonic() + 30
                while window.worker is not None and time.monotonic() < deadline:
                    app.processEvents()
                    time.sleep(0.01)
                if window.worker is not None:
                    raise RuntimeError("Background worker timed out")
                if problems:
                    raise RuntimeError("; ".join(problems))

            wait()
            assert window.plan.valid and len(window.plan.files) == 6
            assert window.organize_button.isEnabled()
            window.start_worker("organize", window.plan)
            wait()
            assert window.report.success, window.report
            assert (root / "Photos/Raw/EML/EML_1.NEF").read_bytes() == b"dummy RAW"
            assert (root / "Videography/Audio/REC001.WAV").read_bytes() == b"dummy audio"
            assert (root / "Other Files/DCIM/100NIKON/metadata.xml").read_bytes() == b"dummy metadata"
            assert (root / "Other Folders/DCIM/100NIKON").is_dir()
            assert (root / "Photos/Raw/MSP/_MSP7396.NEF").read_bytes() == b"dummy underscore RAW"
            assert (root / "Other Files/NIKON001.DSC").read_bytes() == b"dummy camera index"
            assert (root / "Other Files/NIKON/settings/camera.DAT").read_bytes() == b"dummy settings"
            assert (root / "Other Folders/NIKON/settings").is_dir()
            assert not (root / "DCIM").exists() and not (root / "NIKON").exists()
            assert window.result_model.rowCount() == 8
            result = {"success": True, "checks": ["Qt widget initialization", "background recursive scan",
                      "background Windows handle renames", "RAW/WAV/miscellaneous byte preservation",
                      "root DCIM/NIKON folders and NIKON001.DSC", "underscore camera prefix",
                      "original folder preservation", "session log", "GUI completion report"]}
    except Exception:
        result["error"] = traceback.format_exc()
    finally:
        if window is not None:
            if window.worker:
                window.worker.cancel.set()
                window.worker.wait()
                app.processEvents()
            window.close()
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if result["success"] else 1
