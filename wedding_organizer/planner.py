from __future__ import annotations

from contextlib import ExitStack
from dataclasses import replace
from pathlib import Path
import os
import re
import stat
from threading import Event
from typing import Callable

from .model import CATEGORIES, DESTINATIONS, FileOperation, FolderOperation, Issue, Plan, Snapshot
from .safety import checked_root, file_stat, inspect_destination, is_reparse, locked_handle, native_path, regular_directory

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
