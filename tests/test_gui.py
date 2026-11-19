import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import time

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox
import pytest

from wedding_organizer.gui import MainWindow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def wait_for_worker(app, window, timeout=15):
    until = time.monotonic() + timeout
    while window.worker is not None and time.monotonic() < until:
        app.processEvents()
        QTest.qWait(10)
    assert window.worker is None, "Worker did not finish"


def test_complete_gui_workflow(app, tmp_path, monkeypatch):
    root = tmp_path / "Wedding"
    (root / "DCIM").mkdir(parents=True)
    source = root / "DCIM" / "EML_1.NEF"
    source.write_bytes(b"dummy photo")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local-appdata"))
    window = MainWindow()
    window.show()
    assert not window.scan_button.isEnabled()
    assert not window.organize_button.isEnabled()
    window.set_folder(root)
    QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
    assert not window.select_button.isEnabled()
    assert not window.scan_button.isEnabled()
    wait_for_worker(app, window)
    assert window.organize_button.isEnabled()
    assert source.exists()
    assert window.file_model.rowCount() == 1
    assert window.folder_model.rowCount() == 1
    window.search.setText("does not exist")
    assert window.proxy.rowCount() == 0
    window.search.setText("EML")
    assert window.proxy.rowCount() == 1
    window.category.setCurrentText("WAV")
    assert window.proxy.rowCount() == 0
    window.category.setCurrentText("All types")
    # Cancel must not move anything.
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.StandardButton.Cancel)
    QTest.mouseClick(window.organize_button, Qt.MouseButton.LeftButton)
    assert source.exists() and window.worker is None
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.StandardButton.Yes)
    QTest.mouseClick(window.organize_button, Qt.MouseButton.LeftButton)
    wait_for_worker(app, window)
    assert window.report.success
    assert window.result_model.rowCount() == 2
    assert (root / "Photos/Raw/EML/EML_1.NEF").read_bytes() == b"dummy photo"
    assert not window.organize_button.isEnabled()  # Used plan cannot run twice.
    assert window.log_button.isEnabled() and window.export_button.isEnabled()
    QTest.mouseClick(window.scan_button, Qt.MouseButton.LeftButton)
    wait_for_worker(app, window)
    assert window.file_model.rowCount() == 0
    assert not window.organize_button.isEnabled()
    window.close()


def test_close_requests_cancellation_without_destroying_worker(app, tmp_path):
    root = tmp_path / "Wedding"
    root.mkdir()
    for index in range(300):
        (root / f"EML_{index}.NEF").write_bytes(b"dummy")
    window = MainWindow()
    window.show()
    window.set_folder(root)
    window.start_scan()
    window.close()
    assert window.worker.cancel.is_set()
    assert window.isVisible()
    wait_for_worker(app, window)
    assert len(list(root.glob("*.NEF"))) == 300
    window.close()
