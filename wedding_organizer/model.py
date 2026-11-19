from __future__ import annotations

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
