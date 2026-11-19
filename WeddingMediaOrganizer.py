"""Wedding Media File Organizer 1.0.3 — Python revision, no installer.

Requires Python 3.12+ and PySide6. Run this file or the accompanying launcher.
Generated from the supplied maintained source modules by make_single_file.py.
"""
from __future__ import annotations


# ==================== BRANDING ====================
ICON_PNG_BASE64 = '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'


# ==================== MODEL ====================

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
import os

DESTINATIONS = frozenset({"photos", "videography", "other files", "other folders"})
CATEGORIES = ("RAW", "JPEG", "Video", "WAV", "Other")


@dataclass(frozen=True)
class Snapshot:
    device: int
    inode: int
    size: int
    modified: int
    created: int

    @classmethod
    def of(cls, st: os.stat_result) -> Snapshot:
        return cls(st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)

    def same_object(self, st: os.stat_result) -> bool:
        return (self.device, self.inode) == (st.st_dev, st.st_ino)


@dataclass(frozen=True)
class FileOperation:
    source: Path
    destination: Path
    category: str
    prefix: str
    snapshot: Snapshot
    reason: str = ""
    conflict: str = ""


@dataclass(frozen=True)
class FolderOperation:
    source: Path
    destination: Path
    snapshot: Snapshot
    conflict: str = ""


@dataclass(frozen=True)
class Issue:
    path: Path
    reason: str


@dataclass
class Plan:
    root: Path
    root_snapshot: Snapshot
    files: list[FileOperation] = field(default_factory=list)
    folders: list[FolderOperation] = field(default_factory=list)
    directories: dict[Path, Snapshot] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)
    valid: bool = True
    cancelled: bool = False

    @property
    def counts(self) -> Counter:
        return Counter(op.category for op in self.files)

    @property
    def conflicts(self) -> int:
        return sum(bool(op.conflict) for op in self.files)

    @property
    def ready(self) -> list[FileOperation]:
        return [op for op in self.files if not op.conflict]

    @property
    def size(self) -> int:
        return sum(op.snapshot.size for op in self.ready)


@dataclass
class Result:
    source: str
    destination: str
    category: str
    prefix: str
    status: str
    detail: str = ""


@dataclass
class Report:
    root: Path
    log: Path
    results: list[Result] = field(default_factory=list)
    cancelled: bool = False
    fatal_error: str = ""

    @property
    def moved(self) -> Counter:
        return Counter(r.category for r in self.results if r.status == "moved")

    @property
    def skipped(self) -> int:
        return sum(r.status in {"skipped", "conflict", "cancelled"} for r in self.results)

    @property
    def failed(self) -> int:
        return sum(r.status == "failed" for r in self.results)

    @property
    def conflicts(self) -> int:
        return sum(r.status == "conflict" for r in self.results)

    @property
    def success(self) -> bool:
        return not (self.cancelled or self.fatal_error or self.skipped or self.failed)


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if value < 1024 or unit == "PB":
            return f"{value:,.1f} {unit}"
        value /= 1024


# ==================== SAFETY ====================
"""Windows handle-based no-replace renames; never copy, unlink or merge.

Ancestors are held without delete sharing while a move is validated and
performed. A source file is held without write/delete sharing. The kernel's
FileRenameInfo call has ReplaceIfExists=False, including for directories.
"""

from contextlib import ExitStack, contextmanager
from pathlib import Path
import ctypes
from ctypes import wintypes
import os
import stat



class UnsafeOperation(OSError):
    pass


class MoveVerificationError(OSError):
    """Rename succeeded, but its outcome requires manual verification."""


def native_path(path: Path) -> str:
    value = str(path)
    return "\\\\?\\" + value if os.name == "nt" and not value.startswith("\\\\?\\") else value


def file_stat(path: Path) -> os.stat_result:
    return os.lstat(native_path(path))


def is_reparse(st: os.stat_result) -> bool:
    return stat.S_ISLNK(st.st_mode) or bool(getattr(st, "st_file_attributes", 0) & 0x400)


def regular_directory(path: Path, device: int | None = None) -> os.stat_result:
    st = file_stat(path)
    if is_reparse(st) or not stat.S_ISDIR(st.st_mode):
        raise UnsafeOperation(f"Not an ordinary directory (links/reparse points excluded): {path}")
    if device is not None and st.st_dev != device:
        raise UnsafeOperation(f"Filesystem boundary: {path}")
    return st


def checked_root(path: Path) -> Path:
    text = str(path)
    if text.startswith("\\\\?\\") and len(text) > 5 and text[5] == ":":
        text = text[4:]
    root = Path(os.path.abspath(text))
    if os.name == "nt" and (str(root).startswith("\\\\") or root == Path(root.anchor)):
        raise UnsafeOperation("Select a wedding backup folder on a local drive, not a network share or drive root.")
    for item in reversed((root, *root.parents)):
        regular_directory(item)
    return root


def contained(root: Path, path: Path) -> None:
    if not path.is_absolute() or ".." in path.parts or path == root or not path.is_relative_to(root):
        raise UnsafeOperation(f"Path is not strictly inside the selected wedding folder: {path}")


def inspect_destination(root: Path, destination: Path, listings: dict | None = None) -> str:
    """Read-only validation, including case-insensitive component collisions."""
    contained(root, destination)
    current = root
    parts = destination.relative_to(root).parts
    for index, part in enumerate(parts):
        try:
            file_stat(current)
        except FileNotFoundError:
            return ""
        regular_directory(current)
        names = None if listings is None else listings.get(current)
        if names is None:
            with os.scandir(native_path(current)) as entries:
                names = {}
                for entry in entries:
                    names.setdefault(entry.name.casefold(), []).append(entry.name)
            if listings is not None:
                listings[current] = names
        matches = names.get(part.casefold(), [])
        if len(matches) > 1:
            return f"Ambiguous case-insensitive destination component: {current / part}"
        if not matches:
            return ""
        current /= matches[0]
        if index == len(parts) - 1:
            return f"Destination already exists: {current}"
        try:
            regular_directory(current, file_stat(root).st_dev)
        except OSError as exc:
            return str(exc)
    return ""


if os.name == "nt":
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                  ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                                  ctypes.c_void_p, wintypes.DWORD]
    kernel.SetFileInformationByHandle.restype = wintypes.BOOL
    class HandleInformation(ctypes.Structure):
        _fields_ = [("attributes", wintypes.DWORD), ("created", wintypes.FILETIME),
                    ("accessed", wintypes.FILETIME), ("modified", wintypes.FILETIME),
                    ("volume", wintypes.DWORD), ("size_high", wintypes.DWORD),
                    ("size_low", wintypes.DWORD), ("links", wintypes.DWORD),
                    ("index_high", wintypes.DWORD), ("index_low", wintypes.DWORD)]

    kernel.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(HandleInformation)]
    kernel.GetFileInformationByHandle.restype = wintypes.BOOL


def handle_information(handle) -> tuple[int, int, int]:
    info = HandleInformation()
    if not kernel.GetFileInformationByHandle(handle, ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    return info.volume, (info.index_high << 32) | info.index_low, (info.size_high << 32) | info.size_low


def verify_renamed_handle(handle, source: Path, destination: Path, snapshot: Snapshot,
                          *, directory: bool) -> None:
    """Compare the still-open renamed object with its new path, not its old ID.

    FAT/exFAT may change the file ID during a rename. NTFS's usual stable-ID
    behavior must not be assumed across all supported local filesystems.
    """
    destination_handle = kernel.CreateFileW(native_path(destination), 0x80, 0x7, None, 3,
                                             0x02000000 | 0x00200000, None)
    if destination_handle == ctypes.c_void_p(-1).value:
        raise MoveVerificationError(f"Moved, but destination could not be opened for verification: {ctypes.WinError(ctypes.get_last_error())}")
    try:
        if handle_information(handle) != handle_information(destination_handle):
            raise MoveVerificationError("Moved, but destination does not match the open source handle; manual review required.")
        final = file_stat(destination)
        if is_reparse(final) or (directory and not stat.S_ISDIR(final.st_mode)) or (not directory and
                (not stat.S_ISREG(final.st_mode) or
                 (final.st_size, final.st_mtime_ns) != (snapshot.size, snapshot.modified))):
            raise MoveVerificationError("Moved, but destination metadata verification failed; manual review required.")
        try:
            file_stat(source)
        except FileNotFoundError:
            pass
        else:
            raise MoveVerificationError("Moved, but the original path is occupied again; scan again and review it.")
    finally:
        kernel.CloseHandle(destination_handle)


@contextmanager
def locked_handle(path: Path, *, rename: bool = False, directory: bool = True):
    if os.name != "nt":
        raise UnsafeOperation("Safe execution is supported only on Windows 10/11.")
    # READ_DATA/LIST_DIRECTORY is essential: an attributes-only handle does not
    # participate in Windows data-access sharing checks and would not lock paths.
    access = 0x1 | 0x80 | (0x10000 if rename else 0)
    sharing = 0x1 | (0x2 if directory else 0)  # Directories need WRITE sharing for child renames; never DELETE.
    handle = kernel.CreateFileW(native_path(path), access, sharing, None, 3,
                                0x02000000 | 0x00200000, None)  # BACKUP_SEMANTICS | OPEN_REPARSE_POINT
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        st = file_stat(path)
        if is_reparse(st):
            raise UnsafeOperation(f"Reparse point excluded: {path}")
        yield handle
    finally:
        kernel.CloseHandle(handle)


def rename_handle(handle, destination: Path) -> None:
    encoded = native_path(destination).encode("utf-16-le")

    class RenameInfo(ctypes.Structure):
        _fields_ = [("Flags", wintypes.DWORD), ("RootDirectory", wintypes.HANDLE),
                    ("FileNameLength", wintypes.DWORD), ("FileName", wintypes.WCHAR * 1)]

    size = max(ctypes.sizeof(RenameInfo), RenameInfo.FileName.offset + len(encoded) + 2)
    buffer = ctypes.create_string_buffer(size)
    info = RenameInfo.from_buffer(buffer)
    info.Flags = 0  # ReplaceIfExists = FALSE. Never set REPLACE or copy flags.
    info.RootDirectory = None
    info.FileNameLength = len(encoded)
    ctypes.memmove(ctypes.addressof(buffer) + RenameInfo.FileName.offset, encoded, len(encoded))
    if not kernel.SetFileInformationByHandle(handle, 3, buffer, size):
        error = ctypes.get_last_error()
        if error in (80, 183):
            raise FileExistsError(error, "Destination appeared before rename", str(destination))
        raise ctypes.WinError(error)


class WindowsMover:
    def move(self, root: Path, root_snapshot: Snapshot, source: Path, destination: Path,
             snapshot: Snapshot, *, directory: bool = False,
             expected_directories: dict[Path, Snapshot] | None = None) -> None:
        contained(root, source)
        contained(root, destination)
        if directory and destination.is_relative_to(source):
            raise UnsafeOperation("Cannot move a directory into itself or a descendant.")
        with ExitStack() as locks:
            held: set[Path] = set()

            def hold(path: Path):
                if path not in held:
                    locks.enter_context(locked_handle(path))
                    regular_directory(path)
                    held.add(path)

            for ancestor in reversed((root, *root.parents)):
                hold(ancestor)
            if not root_snapshot.same_object(file_stat(root)):
                raise UnsafeOperation("Selected wedding folder changed since scanning.")
            for parent in reversed(source.parent.relative_to(root).parents):
                hold(root / parent)
            hold(source.parent)
            # Validate each parent, including its original identity when scanned.
            for parent in (source.parent, *source.parent.parents):
                if parent == root:
                    break
                regular_directory(parent, root_snapshot.device)
                expected = (expected_directories or {}).get(parent)
                if expected and not expected.same_object(file_stat(parent)):
                    raise UnsafeOperation(f"Source directory changed since scan: {parent}")

            src_handle = locks.enter_context(locked_handle(source, rename=True, directory=directory))
            current = file_stat(source)
            if current.st_dev != root_snapshot.device:
                raise UnsafeOperation("Cross-filesystem moves are not allowed.")
            if directory:
                if not stat.S_ISDIR(current.st_mode) or not snapshot.same_object(current):
                    raise UnsafeOperation("Original directory changed since scanning.")
                # Only empty, previously discovered directory structures may move.
                with ExitStack() as subtree_locks:
                    pending = [source]
                    while pending:
                        parent = pending.pop()
                        with os.scandir(native_path(parent)) as entries:
                            for entry in entries:
                                path = parent / entry.name
                                st = file_stat(path)
                                expected = (expected_directories or {}).get(path)
                                if is_reparse(st) or not stat.S_ISDIR(st.st_mode) or not expected or not expected.same_object(st):
                                    raise UnsafeOperation(f"Folder contains unresolved or new content: {path}")
                                subtree_locks.enter_context(locked_handle(path))
                                regular_directory(path, root_snapshot.device)
                                pending.append(path)
                # Windows disallows renaming a parent with open child handles.
                # Release the child audit handles; keep the source and ancestors locked.
            elif not stat.S_ISREG(current.st_mode) or Snapshot.of(current) != snapshot:
                raise UnsafeOperation("Source is missing, replaced, or changed since scanning; scan again.")

            current_parent = root
            for part in destination.parent.relative_to(root).parts:
                current_parent /= part
                try:
                    os.mkdir(native_path(current_parent))
                except FileExistsError:
                    pass
                hold(current_parent)
                regular_directory(current_parent, root_snapshot.device)
            conflict = inspect_destination(root, destination)
            if conflict:
                raise FileExistsError(conflict)
            rename_handle(src_handle, destination)
            verify_renamed_handle(src_handle, source, destination, snapshot, directory=directory)


# ==================== PLANNER ====================

from contextlib import ExitStack
from dataclasses import replace
from pathlib import Path
import os
import re
import stat
from threading import Event
from typing import Callable


RAW = {".nef", ".arw", ".cr2", ".cr3", ".dng", ".raf", ".orf", ".rw2"}
RESERVED = {"CON", "PRN", "AUX", "NUL"}


def classify(root: Path, source: Path) -> tuple[str, str, Path, str]:
    extension = source.suffix.lower()
    category = ("RAW" if extension in RAW else "JPEG" if extension in {".jpg", ".jpeg"}
                else "Video" if extension in {".mp4", ".mov"} else "WAV" if extension == ".wav" else "Other")
    if category == "WAV":
        return category, "", root / "Videography" / "Audio" / source.name, ""
    reason = "Unsupported extension" if category == "Other" else ""
    prefix = ""
    if category != "Other":
        camera_stem = source.stem.lstrip("_")
        if not re.fullmatch(r"[A-Za-z0-9]{3}", camera_stem[:3]):
            category, reason = "Other", "Invalid camera prefix: after leading underscores, first three stem characters must be ASCII letters or digits"
        else:
            prefix = camera_stem[:3].upper()
            if prefix in RESERVED:
                category, prefix, reason = "Other", "", "Invalid camera prefix: reserved Windows directory name"
    bases = {"RAW": root / "Photos" / "Raw", "JPEG": root / "Photos" / "Jpg",
             "Video": root / "Videography"}
    destination = (root / "Other Files" / source.relative_to(root) if category == "Other"
                   else bases[category] / prefix / source.name)
    return category, prefix, destination, reason


def scan(root: Path, cancel: Event | None = None,
         progress: Callable[[str, int], None] | None = None) -> Plan:
    root = checked_root(root)
    plan = Plan(root, Snapshot.of(file_stat(root)))
    pending = [root]
    top_folders: list[Path] = []
    # Holding directory handles through the read-only scan prevents replacement
    # by a junction between discovery and traversal on Windows.
    with ExitStack() as locks:
        if os.name == "nt":
            for ancestor in reversed((root, *root.parents)):
                locks.enter_context(locked_handle(ancestor))
                regular_directory(ancestor)
        while pending:
            if cancel and cancel.is_set():
                plan.valid, plan.cancelled = False, True
                break
            parent = pending.pop()
            try:
                regular_directory(parent, plan.root_snapshot.device)
                with os.scandir(native_path(parent)) as iterator:
                    entries = sorted(iterator, key=lambda e: (e.name.casefold(), e.name))
                for entry in entries:
                    if cancel and cancel.is_set():
                        plan.valid, plan.cancelled = False, True
                        break
                    path = parent / entry.name
                    # DirEntry.stat on Windows may report zero st_dev/st_ino.
                    st = file_stat(path)
                    if parent == root and entry.name.casefold() in DESTINATIONS:
                        if is_reparse(st) or not stat.S_ISDIR(st.st_mode):
                            plan.issues.append(Issue(path, "Reserved destination is not an ordinary directory"))
                            plan.valid = False
                        continue
                    if is_reparse(st):
                        plan.issues.append(Issue(path, "Skipped symbolic link, junction, or reparse point; left in place"))
                        continue
                    if st.st_dev != plan.root_snapshot.device:
                        plan.issues.append(Issue(path, "Skipped filesystem boundary"))
                        continue
                    if stat.S_ISDIR(st.st_mode):
                        if os.name == "nt":
                            locks.enter_context(locked_handle(path))
                            st = regular_directory(path, plan.root_snapshot.device)
                        plan.directories[path] = Snapshot.of(st)
                        if parent == root:
                            top_folders.append(path)
                        pending.append(path)
                    elif stat.S_ISREG(st.st_mode):
                        category, prefix, destination, reason = classify(root, path)
                        plan.files.append(FileOperation(path, destination, category, prefix, Snapshot.of(st), reason))
                    else:
                        plan.issues.append(Issue(path, "Unsupported filesystem object; left in place"))
                    if progress and (len(plan.files) % 100 == 0):
                        progress(str(path), len(plan.files))
            except OSError as exc:
                plan.issues.append(Issue(parent, f"Incomplete scan: {exc}"))
                plan.valid = False

    plan.files.sort(key=lambda op: (CATEGORIES.index(op.category), str(op.source).casefold(), str(op.source)))
    claimed: dict[str, Path] = {}
    listings: dict = {}
    for index, op in enumerate(plan.files):
        key = str(op.destination).casefold()
        try:
            conflict = inspect_destination(root, op.destination, listings)
        except OSError as exc:
            conflict = f"Cannot safely inspect destination: {exc}"
        if key in claimed:
            conflict = f"Same destination as {claimed[key]}; source will stay in place"
        else:
            claimed[key] = op.source
        if conflict:
            plan.files[index] = replace(op, conflict=conflict)

    for source in sorted(top_folders, key=lambda p: (str(p).casefold(), str(p))):
        destination = root / "Other Folders" / source.name
        try:
            conflict = inspect_destination(root, destination, listings)
        except OSError as exc:
            conflict = str(exc)
        if any(op.conflict and op.source.is_relative_to(source) for op in plan.files):
            conflict = conflict or "Contains unresolved filename conflicts; folder will stay in place"
        if any(issue.path.is_relative_to(source) for issue in plan.issues):
            conflict = conflict or "Contains skipped or unreadable content; manual review required"
        plan.folders.append(FolderOperation(source, destination, plan.directories[source], conflict))
    return plan


# ==================== ENGINE ====================

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from typing import Callable
import json
import os
import uuid



def log_directory() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "WeddingMediaOrganizer" / "Logs"


class Journal:
    def __init__(self, root: Path, directory: Path | None = None):
        directory = (directory or log_directory()).absolute()
        # resolve is appropriate for log-location validation, never source traversal.
        if directory.resolve().is_relative_to(root.resolve()):
            raise UnsafeOperation("Operation logs must be outside the wedding folder.")
        directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = directory / f"session-{stamp}-{uuid.uuid4().hex[:8]}.jsonl"
        self.file = self.path.open("x", encoding="utf-8")
        try:
            self.write("session", root=str(root), version="1.0.3")
        except BaseException:
            self.file.close()
            raise

    def write(self, event: str, **data):
        self.file.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "event": event, **data}, ensure_ascii=False) + "\n")
        self.file.flush()
        os.fsync(self.file.fileno())

    def close(self):
        self.file.close()


def organize(plan: Plan, cancel: Event | None = None,
             progress: Callable[[Result, int, int], None] | None = None,
             *, logs: Path | None = None, mover: WindowsMover | None = None) -> Report:
    if not plan.valid or plan.cancelled:
        raise UnsafeOperation("A complete, valid scan is required before organizing.")
    mover = mover or WindowsMover()
    journal = Journal(plan.root, logs)
    report = Report(plan.root, journal.path)
    total = len(plan.files) + len(plan.folders) + len(plan.issues)

    def record(result: Result):
        # Record in memory first: even a failing log write must not hide a completed rename.
        report.results.append(result)
        journal.write("result", **asdict(result))
        if progress:
            progress(result, len(report.results), total)

    try:
        # Persist the entire plan before any mutation; pending intents can be reconciled
        # with source/destination paths after power loss or an abrupt process exit.
        for op in [*plan.files, *plan.folders]:
            journal.write("planned", source=str(op.source), destination=str(op.destination),
                          category=getattr(op, "category", "Folder"), prefix=getattr(op, "prefix", ""),
                          snapshot=asdict(op.snapshot), conflict=op.conflict,
                          reason=getattr(op, "reason", ""))
        for issue in plan.issues:
            record(Result(str(issue.path), "", "Scan issue", "", "skipped", issue.reason))
        unresolved: list[Path] = [issue.path for issue in plan.issues]
        for op in [*plan.files, *plan.folders]:
            directory = not hasattr(op, "category")
            category = "Folder" if directory else op.category
            prefix = getattr(op, "prefix", "")
            status, detail = "moved", ""
            if cancel and cancel.is_set():
                report.cancelled = True
                status, detail = "cancelled", "Stopped before this operation; scan again to resume"
            elif op.conflict:
                status, detail = "conflict", op.conflict
            elif directory and any(path.is_relative_to(op.source) for path in unresolved):
                status, detail = "skipped", "Original folder contains unresolved items; left in place"
            else:
                journal.write("intent", source=str(op.source), destination=str(op.destination), category=category)
                try:
                    mover.move(plan.root, plan.root_snapshot, op.source, op.destination, op.snapshot,
                               directory=directory, expected_directories=plan.directories)
                except FileExistsError as exc:
                    status, detail = "conflict", str(exc)
                except UnsafeOperation as exc:
                    status, detail = "skipped", str(exc)
                except OSError as exc:
                    status, detail = "failed", str(exc)
            if status != "moved":
                unresolved.append(op.source)
            record(Result(str(op.source), str(op.destination), category, prefix, status, detail))
        journal.write("summary", success=report.success, cancelled=report.cancelled,
                      moved=dict(report.moved), skipped=report.skipped, failed=report.failed,
                      conflicts=report.conflicts)
    except Exception as exc:
        report.fatal_error = f"Session stopped: {exc}. Review the log and scan again before resuming."
        processed = {r.source for r in report.results}
        for op in [*plan.files, *plan.folders]:
            if str(op.source) not in processed:
                report.results.append(Result(str(op.source), str(op.destination),
                                             getattr(op, "category", "Folder"), getattr(op, "prefix", ""),
                                             "skipped", "Session stopped; outcome requires a fresh scan"))
    finally:
        try:
            journal.close()
        except OSError as exc:
            report.fatal_error = f"Could not close the session log: {exc}. Review the listed results and scan again."
    return report


# ==================== GUI ====================

from pathlib import Path
from threading import Event
import csv
import time
import base64
import webbrowser

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFileDialog, QFrame,
                             QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QProgressBar, QPushButton, QTabWidget, QTableView,
                             QVBoxLayout, QWidget)



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


if __name__ == "__main__":
    raise SystemExit(main())
