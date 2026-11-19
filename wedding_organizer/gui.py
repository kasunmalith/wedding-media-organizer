from __future__ import annotations

from pathlib import Path
from threading import Event
import csv
import time
import base64
import webbrowser
from .branding import ICON_PNG_BASE64

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFileDialog, QFrame,
                             QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QProgressBar, QPushButton, QTabWidget, QTableView,
                             QVBoxLayout, QWidget)

from .engine import organize
from .model import CATEGORIES, Plan, Report, human_size
from .planner import scan


class TableModel(QAbstractTableModel):
    def __init__(self, headers, rows=(), parent=None):
        super().__init__(parent)
        self.headers, self.rows = headers, list(rows)

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        value = self.rows[index.row()][index.column()]
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
            return str(value)
        if role == Qt.ItemDataRole.ForegroundRole and index.column() == len(self.headers) - 1:
            text = str(value).lower()
            if any(word in text for word in ("conflict", "invalid", "failed", "skipped", "cancelled", "unresolved")):
                return QColor("#ad4a15")
            if text.startswith("moved"):
                return QColor("#157b63")
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def reset(self, rows):
        self.beginResetModel()
        self.rows = list(rows)
        self.endResetModel()


class SearchProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.query = ""
        self.category = "All types"

    def filterAcceptsRow(self, row, parent):
        values = self.sourceModel().rows[row]
        return ((self.category == "All types" or values[1] == self.category) and
                (not self.query or any(self.query in str(v).casefold() for v in values)))


class Worker(QThread):
    completed = Signal(object)
    problem = Signal(str)
    updated = Signal(str, int, int)

    def __init__(self, mode: str, value, parent=None):
        super().__init__(parent)
        self.mode, self.value = mode, value
        self.cancel = Event()
        self.last_update = 0.0
        self.moved = self.skipped = self.failed = self.folders = 0

    def scan_progress(self, path, count):
        now = time.monotonic()
        if now - self.last_update > 0.08:
            self.updated.emit(f"Scanning · {count:,} files found\n{path}", 0, 0)
            self.last_update = now

    def move_progress(self, result, completed, total):
        self.moved += result.status == "moved" and result.category != "Folder"
        self.folders += result.status == "moved" and result.category == "Folder"
        self.failed += result.status == "failed"
        self.skipped += result.status in {"skipped", "conflict", "cancelled"}
        now = time.monotonic()
        if now - self.last_update > 0.08 or completed == total:
            self.updated.emit(f"{self.moved:,} files moved · {self.skipped:,} skipped · {self.failed:,} failed · "
                              f"{self.folders:,} folders moved · {completed:,}/{total:,} items\n{result.source}", completed, total)
            self.last_update = now

    def run(self):
        try:
            result = (scan(self.value, self.cancel, self.scan_progress) if self.mode == "scan"
                      else organize(self.value, self.cancel, self.move_progress))
            self.completed.emit(result)
        except Exception as exc:
            self.problem.emit(f"{type(exc).__name__}: {exc}")


STYLE = """
QMainWindow, QWidget { background: #f4f6f8; color: #20303e; font-family: 'Segoe UI'; font-size: 10pt; }
QLabel#title { font-size: 25pt; font-weight: 650; color: #18362f; }
QLabel#subtitle { color: #667782; font-size: 11pt; }
QLabel#eyebrow { color: #21836e; font-weight: 700; font-size: 9pt; }
QFrame#card { background: white; border: 1px solid #dfe5e8; border-radius: 9px; }
QFrame#card QLabel { background: transparent; }
QLabel#metric { font-size: 20pt; font-weight: 600; color: #18362f; }
QLabel#metricName { color: #657581; font-size: 9pt; }
QPushButton { background: white; border: 1px solid #cbd6db; border-radius: 6px; padding: 10px 18px; font-weight: 600; }
QPushButton:hover { background: #e9f3ef; border-color: #729f91; }
QPushButton#primary { background: #176b55; color: white; border-color: #176b55; }
QPushButton#primary:hover { background: #125540; }
QPushButton:disabled { background: #e6ebed; color: #8d9aa2; border-color: #dce3e6; }
QLineEdit, QComboBox { background: white; border: 1px solid #cbd6db; border-radius: 5px; padding: 9px; }
QTableView { background: white; alternate-background-color: #f7f9fa; gridline-color: #edf0f2; border: 1px solid #dde4e7; selection-background-color: #d8ebe5; selection-color: #20303e; }
QHeaderView::section { background: #edf2f3; color: #52636e; padding: 10px; border: 0; border-bottom: 1px solid #dce4e7; font-weight: 600; }
QTabWidget::pane { border: 0; }
QTabBar::tab { padding: 11px 20px; margin-right: 5px; color: #657581; border: 0; background: transparent; }
QTabBar::tab:selected { color: #176b55; border-bottom: 3px solid #176b55; font-weight: 600; }
QProgressBar { background: #e1e8eb; border: 0; border-radius: 4px; height: 9px; text-align: center; }
QProgressBar::chunk { background: #26977a; border-radius: 4px; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.root: Path | None = None
        self.plan: Plan | None = None
        self.report: Report | None = None
        self.worker: Worker | None = None
        self.setWindowTitle("Eon Episode — Wedding Media File Organizer — 1.0.3")
        logo_pixmap = QPixmap()
        logo_pixmap.loadFromData(base64.b64decode(ICON_PNG_BASE64), 'PNG')
        self.setWindowIcon(QIcon(logo_pixmap))
        self.resize(1320, 870)
        self.setMinimumSize(960, 700)
        self.setStyleSheet(STYLE)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(13)
        eyebrow = QLabel("WEDDING PRODUCTION  /  MEDIA MANAGEMENT")
        eyebrow.setObjectName("eyebrow")
        layout.addWidget(eyebrow)
        heading = QHBoxLayout()
        self.logo_label = QLabel()
        self.logo_label.setPixmap(logo_pixmap.scaled(108, 108, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.logo_label.setFixedSize(108, 108)
        self.logo_label.setAccessibleName("Eon Episode logo")
        heading.addWidget(self.logo_label)
        title = QLabel("Eon Episode\nWedding Media File Organizer")
        title.setObjectName("title")
        heading.addWidget(title, 1)
        layout.addLayout(heading)
        subtitle = QLabel("A clear home for every frame. Scan your backup, review every destination, then organize.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        folder_row = QHBoxLayout()
        self.select_button = QPushButton("Select Wedding Folder")
        self.select_button.clicked.connect(self.select_folder)
        folder_row.addWidget(self.select_button)
        self.path_field = QLineEdit()
        self.path_field.setReadOnly(True)
        self.path_field.setPlaceholderText("Choose the wedding backup folder on your computer or external drive")
        folder_row.addWidget(self.path_field, 1)
        self.scan_button = QPushButton("Scan Files")
        self.scan_button.clicked.connect(self.start_scan)
        folder_row.addWidget(self.scan_button)
        layout.addLayout(folder_row)

        metrics = QGridLayout()
        metrics.setSpacing(10)
        self.metrics = {}
        for index, name in enumerate(("Files detected", "RAW photos", "JPEG photos", "Video files", "WAV audio", "Other files")):
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 10, 15, 10)
            value, label = QLabel("—"), QLabel(name)
            value.setObjectName("metric")
            label.setObjectName("metricName")
            card_layout.addWidget(value)
            card_layout.addWidget(label)
            self.metrics[name] = value
            metrics.addWidget(card, 0, index)
        layout.addLayout(metrics)
        self.details = QLabel("Offline processing  •  Original names preserved  •  Existing files never replaced")
        self.details.setWordWrap(True)
        layout.addWidget(self.details)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search filenames, paths, prefixes, or warnings…")
        self.search.textChanged.connect(self.filter_rows)
        filters.addWidget(self.search, 1)
        self.category = QComboBox()
        self.category.addItems(["All types", *CATEGORIES])
        self.category.currentTextChanged.connect(self.filter_rows)
        filters.addWidget(self.category)
        layout.addLayout(filters)
        self.tabs = QTabWidget()
        self.file_model = TableModel(["Original Filename", "File Type", "Camera Prefix", "Original Location",
                                      "Destination Location", "File Size", "Status"])
        self.proxy = SearchProxy(self)
        self.proxy.setSourceModel(self.file_model)
        self.file_table = self.make_table(self.proxy)
        for column, width in enumerate((180, 80, 100, 210, 235, 85, 310)):
            self.file_table.setColumnWidth(column, width)
        self.tabs.addTab(self.file_table, "File preview")
        self.folder_model = TableModel(["Original folder", "Destination", "Status"])
        self.tabs.addTab(self.make_table(self.folder_model), "Original folders")
        self.issue_model = TableModel(["Location", "Reason / manual review"])
        self.tabs.addTab(self.make_table(self.issue_model), "Scan issues")
        self.result_model = TableModel(["Original location", "Destination", "Type", "Result / details"])
        self.tabs.addTab(self.make_table(self.result_model), "Session results")
        layout.addWidget(self.tabs, 1)

        self.status = QLabel("1  Select a wedding backup folder to begin.")
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setMinimumHeight(45)
        layout.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        actions = QHBoxLayout()
        self.log_button = QPushButton("Open Log Folder")
        self.log_button.clicked.connect(self.open_logs)
        actions.addWidget(self.log_button)
        self.export_button = QPushButton("Export Report")
        self.export_button.clicked.connect(self.export_report)
        actions.addWidget(self.export_button)
        actions.addStretch()
        self.stop_button = QPushButton("Stop Safely")
        self.stop_button.clicked.connect(self.stop)
        actions.addWidget(self.stop_button)
        self.organize_button = QPushButton("Organize Files")
        self.organize_button.setObjectName("primary")
        self.organize_button.clicked.connect(self.confirm_organize)
        actions.addWidget(self.organize_button)
        layout.addLayout(actions)
        self.credit = QLabel('Software Development by <a href="https://www.energeticedge.lk/" style="color:#176b55;">Energetic Edge (Pvt) Ltd</a>')
        self.credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.credit.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.credit.setOpenExternalLinks(False)
        self.credit.linkActivated.connect(lambda url: webbrowser.open(url, new=1))
        self.credit.setStyleSheet('font-size: 9pt; color: #657581; padding-top: 8px;')
        layout.addWidget(self.credit)
        self.refresh_actions()

    def make_table(self, model):
        table = QTableView()
        table.setModel(model)
        table.setAlternatingRowColors(True)
        table.setWordWrap(False)
        table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().hide()
        table.verticalHeader().setDefaultSectionSize(32)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.horizontalHeader().setStretchLastSection(True)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        for index in range(model.columnCount()):
            table.setColumnWidth(index, 160 if index < 3 else 270)
        return table

    def filter_rows(self):
        self.proxy.beginFilterChange()
        self.proxy.query = self.search.text().casefold()
        self.proxy.category = self.category.currentText()
        self.proxy.endFilterChange(QSortFilterProxyModel.Direction.Rows)

    def refresh_actions(self):
        busy = self.worker is not None
        self.select_button.setEnabled(not busy)
        self.scan_button.setEnabled(not busy and self.root is not None)
        self.organize_button.setEnabled(not busy and self.plan is not None and self.plan.valid
                                        and bool(self.plan.files or self.plan.folders))
        self.stop_button.setEnabled(busy)
        self.log_button.setEnabled(not busy and self.report is not None)
        self.export_button.setEnabled(not busy and self.report is not None)

    def select_folder(self):
        selected = QFileDialog.getExistingDirectory(self, "Select Wedding Folder", str(self.root or Path.home()),
                                                    QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if selected:
            self.set_folder(Path(selected))

    def set_folder(self, path: Path):
        self.root, self.plan, self.report = path, None, None
        self.path_field.setText(str(path))
        for model in (self.file_model, self.folder_model, self.issue_model, self.result_model):
            model.reset([])
        for metric in self.metrics.values():
            metric.setText("—")
        self.details.setText("Ready to scan all eligible subfolders. Scanning makes no changes.")
        self.status.setText("2  Select Scan Files to build the organization preview.")
        self.progress.setValue(0)
        self.refresh_actions()

    def start_scan(self):
        if self.root is not None and self.worker is None:
            self.plan = None
            self.file_model.reset([])
            self.folder_model.reset([])
            self.issue_model.reset([])
            self.start_worker("scan", self.root)

    def start_worker(self, mode, value):
        self.worker = Worker(mode, value, self)
        self.worker.updated.connect(self.on_progress)
        self.worker.completed.connect(self.on_completed)
        self.worker.problem.connect(self.on_problem)
        self.worker.finished.connect(self.on_finished)
        self.progress.setRange(0, 0)
        self.status.setText("Scanning all eligible subfolders…" if mode == "scan" else "Preparing the session log and validating operations…")
        self.refresh_actions()
        self.worker.start()

    def confirm_organize(self):
        if self.worker is not None or self.plan is None or not self.plan.valid:
            return
        plan = self.plan
        folders = sum(not op.conflict for op in plan.folders)
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Confirm organization")
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setTextFormat(Qt.TextFormat.PlainText)
        dialog.setText(f"Organize this wedding backup?\n\n{plan.root}")
        dialog.setInformativeText(f"{len(plan.ready):,} planned file moves · {human_size(plan.size)}\n"
                                  f"{folders:,} original folders eligible after file moves\n"
                                  f"{plan.conflicts:,} filename conflicts · {sum(bool(x.conflict) for x in plan.folders):,} blocked folders\n"
                                  f"{len(plan.issues):,} scan issues\n\n"
                                  "Conflicting files stay in place. Folder moves depend on successful file operations. "
                                  "Keep this backup connected and avoid editing it during organization.")
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        if dialog.exec() == QMessageBox.StandardButton.Yes:
            self.start_worker("organize", plan)

    def on_progress(self, text, completed, total):
        self.status.setText(text)
        self.progress.setRange(0, total)
        self.progress.setValue(completed)

    def on_completed(self, result):
        if isinstance(result, Plan):
            self.plan = result
            values = [len(result.files), *(result.counts[c] for c in CATEGORIES)]
            for label, value in zip(self.metrics.values(), values):
                label.setText(f"{value:,}")
            invalid = sum(op.reason.startswith("Invalid") for op in result.files)
            prefixes = {op.prefix for op in result.files if op.prefix}
            media_size = sum(op.snapshot.size for op in result.files if op.category != "Other")
            self.details.setText(f"{len(result.directories):,} original folders · {len(prefixes):,} camera prefixes · "
                                 f"{invalid:,} invalid prefixes · {result.conflicts:,} filename conflicts · "
                                 f"{human_size(media_size)} detected media · {human_size(result.size)} planned moves")
            self.file_model.reset((op.source.name, op.category, op.prefix or "—", str(op.source),
                                   str(op.destination), human_size(op.snapshot.size),
                                   f"Conflict: {op.conflict}" if op.conflict else op.reason or "Ready") for op in result.files)
            self.folder_model.reset((str(op.source), str(op.destination),
                                     f"Skipped: {op.conflict}" if op.conflict else "After all contained files move successfully") for op in result.folders)
            self.issue_model.reset((str(issue.path), issue.reason) for issue in result.issues)
            self.tabs.setTabText(0, f"File preview ({len(result.files):,})")
            self.tabs.setTabText(1, f"Original folders ({len(result.folders):,})")
            self.tabs.setTabText(2, f"Scan issues ({len(result.issues):,})")
            self.tabs.setCurrentIndex(0 if result.valid else 2)
            self.status.setText("Scan stopped. No files were moved. Scan again to build a complete plan." if result.cancelled else
                                "Scan incomplete or unsafe destination detected. Review Scan issues, resolve them, and scan again." if not result.valid else
                                "No new files or original folders to organize." if not result.files and not result.folders else
                                "3  Review the file and folder previews, then select Organize Files. No files have moved yet.")
        else:
            self.report, self.plan = result, None  # Every execution consumes its plan.
            self.result_model.reset((r.source, r.destination, r.category,
                                     r.status.capitalize() + (f": {r.detail}" if r.detail else "")) for r in result.results)
            self.tabs.setCurrentIndex(3)
            moved = result.moved
            self.details.setText("Organized: " + " · ".join(f"{moved[c]:,} {c}" for c in CATEGORIES) +
                                 f" · {moved['Folder']:,} original folders")
            outcome = "Completed successfully" if result.success else "Stopped safely" if result.cancelled else "Partially completed — manual review required"
            filename_conflicts = sum(r.status == "conflict" and r.category != "Folder" for r in result.results)
            self.status.setText(f"{outcome}. {result.skipped:,} skipped items · {result.failed:,} failures · "
                                f"{filename_conflicts:,} unresolved filename conflicts.\nLog: {result.log}" +
                                (f"\n{result.fatal_error}" if result.fatal_error else ""))
        self.progress.setRange(0, 100)
        self.progress.setValue(100)

    def on_problem(self, message):
        self.plan = None
        self.status.setText(f"Operation stopped: {message}\nScan again before retrying.")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        QMessageBox.warning(self, "Unable to complete operation", message)

    def on_finished(self):
        worker, self.worker = self.worker, None
        if worker:
            worker.deleteLater()
        self.refresh_actions()

    def stop(self):
        if self.worker:
            self.worker.cancel.set()
            self.stop_button.setEnabled(False)
            self.status.setText("Stopping after the current filesystem operation. Please keep the drive connected…")

    def open_logs(self):
        if self.report:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.report.log.parent)))

    def export_report(self):
        if not self.report:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export session report", str(self.report.log.with_suffix(".csv")), "CSV report (*.csv)")
        if not path:
            return
        try:
            if Path(path).resolve().is_relative_to(self.report.root.resolve()):
                raise ValueError("Save the report outside the wedding backup folder.")
            with Path(path).open("x", newline="", encoding="utf-8-sig") as stream:
                writer = csv.writer(stream)
                writer.writerow(["Original location", "Destination", "Category", "Camera prefix", "Status", "Details"])
                for item in self.report.results:
                    values = [item.source, item.destination, item.category, item.prefix, item.status, item.detail]
                    writer.writerow(["'" + v if v.startswith(("=", "+", "-", "@")) else v for v in values])
            self.status.setText(f"Report exported: {path}\nOperation log: {self.report.log}")
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Report not exported", str(exc))

    def closeEvent(self, event):
        if self.worker is not None:
            self.stop()
            event.ignore()
            return
        event.accept()


def main() -> int:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Wedding Media File Organizer")
    app.setOrganizationName("WeddingMediaOrganizer")
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec()
