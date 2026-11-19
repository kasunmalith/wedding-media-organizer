"""Windows handle-based no-replace renames; never copy, unlink or merge.

Ancestors are held without delete sharing while a move is validated and
performed. A source file is held without write/delete sharing. The kernel's
FileRenameInfo call has ReplaceIfExists=False, including for directories.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
from pathlib import Path
import ctypes
from ctypes import wintypes
import os
import stat

from .model import Snapshot


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
