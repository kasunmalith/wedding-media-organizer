from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from threading import Event
import ctypes
import hashlib
import json
import os
import subprocess

import pytest

from wedding_organizer.engine import Journal, organize
from wedding_organizer.model import Snapshot
from wedding_organizer.planner import RAW, classify, scan
from wedding_organizer.safety import UnsafeOperation, WindowsMover, locked_handle
import wedding_organizer.safety as safety


pytestmark = pytest.mark.skipif(os.name != "nt", reason="Real Windows no-replace operations required")


@pytest.fixture
def wedding(tmp_path):
    root = tmp_path / "Wedding Backup"
    root.mkdir()
    return root


def put(root, path, data=None):
    file = root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes(data if data is not None else ("original:" + path).encode())
    return file


def contents(root):
    return Counter(hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file() and not p.is_symlink())


def run(root, plan=None, **kwargs):
    return organize(plan or scan(root), logs=root.parent / "logs", **kwargs)


@pytest.mark.parametrize("extension", sorted(RAW))
@pytest.mark.parametrize("folder", ["", "DCIM/", "DCIM/card/nested/Photos/"])
def test_raw_every_extension_and_depth(wedding, extension, folder):
    source = put(wedding, folder + "eml_0001" + extension.upper())
    before = contents(wedding)
    plan = scan(wedding)
    assert source.exists() and len(plan.files) == 1  # Scan is read-only.
    assert plan.files[0].destination == wedding / "Photos" / "Raw" / "EML" / source.name
    report = run(wedding, plan)
    assert report.success, report
    assert contents(wedding) == before


@pytest.mark.parametrize("filename,category,destination", [
    ("WAR_1.JpG", "JPEG", "Photos/Jpg/WAR"), ("A7C_2.JPEG", "JPEG", "Photos/Jpg/A7C"),
    ("EML_1.Mp4", "Video", "Videography/EML"), ("WAR_2.mOv", "Video", "Videography/WAR"),
    ("r.WaV", "WAV", "Videography/Audio"),
])
@pytest.mark.parametrize("folder", ["", "Camera 2/PRIVATE/deep/"])
def test_photo_video_audio(wedding, filename, category, destination, folder):
    put(wedding, folder + filename)
    before = contents(wedding)
    plan = scan(wedding)
    assert plan.counts[category] == 1
    assert plan.files[0].destination == wedding / destination / filename
    assert run(wedding, plan).success
    assert contents(wedding) == before
    assert not (wedding / "Audio").exists()


@pytest.mark.parametrize("filename", ["a.NEF", "ab.jpg", "_AB.mov", "éML.NEF", "猫ab.mp4", "CON_1.NEF", "PRN.jpg", "A B.CR3"])
def test_invalid_prefix_preserved_and_explained(wedding, filename):
    put(wedding, "card/" + filename)
    plan = scan(wedding)
    assert plan.files[0].category == "Other"
    assert plan.files[0].reason.startswith("Invalid")
    assert run(wedding, plan).success
    assert (wedding / "Other Files" / "card" / filename).is_file()


def test_miscellaneous_and_empty_folder_structure(wedding):
    for path in ["notes.txt", "DCIM/100NIKON/metadata.xml", "DCIM/100NIKON/settings.xmp", "Camera/readme", "Camera/clip.MP3"]:
        put(wedding, path)
    (wedding / "PRIVATE" / "a" / "b").mkdir(parents=True)
    before = contents(wedding)
    plan = scan(wedding)
    assert plan.counts["Other"] == 5
    assert run(wedding, plan).success
    assert (wedding / "Other Files/DCIM/100NIKON/metadata.xml").exists()
    assert (wedding / "Other Folders/PRIVATE/a/b").is_dir()
    assert (wedding / "Other Folders/DCIM/100NIKON").is_dir()
    assert contents(wedding) == before


def test_all_categories_and_prefixes(wedding):
    for path in ["EML_1.NEF", "WAR_1.nef", "DSC12.jpg", "A7C_2.ARW", "ABC00.MP4", "XYZ00.MOV", "voice.wav", "notes.txt"]:
        put(wedding, path)
    plan = scan(wedding)
    assert plan.counts == {"RAW": 3, "JPEG": 1, "Video": 2, "WAV": 1, "Other": 1}
    assert len({op.prefix for op in plan.files if op.prefix}) == 6
    assert [op.category for op in plan.files] == ["RAW"] * 3 + ["JPEG", "Video", "Video", "WAV", "Other"]
    assert run(wedding, plan).success


def test_duplicate_destinations_and_parent_preserved(wedding):
    first = put(wedding, "A/nested/EML_1.NEF", b"first")
    second = put(wedding, "B/nested/EML_1.NEF", b"second")
    before = contents(wedding)
    plan = scan(wedding)
    assert plan.conflicts == 1
    report = run(wedding, plan)
    assert report.moved["RAW"] == 1 and not report.success
    assert (wedding / "Photos/Raw/EML/EML_1.NEF").read_bytes() == b"first"
    assert second.read_bytes() == b"second"
    assert second.parent.exists() and not first.exists()
    assert (wedding / "Other Folders/A/nested").exists()
    assert not (wedding / "Other Folders/B").exists()
    assert contents(wedding) == before


@pytest.mark.parametrize("existing", ["file", "directory"])
def test_existing_destination_never_replaced(wedding, existing):
    source = put(wedding, "card/EML_1.NEF", b"original")
    destination = wedding / "Photos/Raw/EML/EML_1.NEF"
    if existing == "file":
        put(wedding, str(destination.relative_to(wedding)), b"existing")
    else:
        destination.mkdir(parents=True)
    plan = scan(wedding)
    assert plan.conflicts == 1
    report = run(wedding, plan)
    assert not report.success and source.read_bytes() == b"original"
    assert destination.is_dir() if existing == "directory" else destination.read_bytes() == b"existing"


def test_existing_folder_destination_is_not_merged(wedding):
    put(wedding, "DCIM/EML_1.NEF")
    (wedding / "Other Folders/DCIM/old").mkdir(parents=True)
    report = run(wedding)
    assert report.moved["RAW"] == 1
    assert report.moved["Folder"] == 0
    assert (wedding / "DCIM").exists()
    assert (wedding / "Other Folders/DCIM/old").exists()


@pytest.mark.parametrize("change", ["content", "missing", "replace"])
def test_changed_sources_are_not_moved(wedding, change):
    source = put(wedding, "card/EML_1.NEF", b"original")
    plan = scan(wedding)
    if change == "content":
        source.write_bytes(b"changed after preview")
    elif change == "missing":
        source.rename(source.with_suffix(".gone"))
    else:
        source.rename(source.with_suffix(".original"))
        source.write_bytes(b"replacement")
    report = run(wedding, plan)
    assert not report.success and report.moved["RAW"] == 0
    assert (wedding / "card").exists()
    assert not (wedding / "Photos/Raw/EML/EML_1.NEF").exists()


def test_destination_created_after_preview(wedding):
    source = put(wedding, "card/EML_1.NEF", b"source")
    plan = scan(wedding)
    put(wedding, "Photos/Raw/EML/EML_1.NEF", b"late arrival")
    report = run(wedding, plan)
    assert report.conflicts and source.read_bytes() == b"source"
    assert (wedding / "Photos/Raw/EML/EML_1.NEF").read_bytes() == b"late arrival"


def test_kernel_blocks_race_after_last_exists_check(wedding, monkeypatch):
    source = put(wedding, "EML_1.NEF", b"source")
    plan = scan(wedding)
    native_rename = safety.rename_handle

    def race(handle, destination):
        destination.write_bytes(b"racing writer")
        native_rename(handle, destination)

    monkeypatch.setattr(safety, "rename_handle", race)
    report = run(wedding, plan)
    assert not report.success
    assert source.read_bytes() == b"source"
    assert plan.files[0].destination.read_bytes() == b"racing writer"


def test_kernel_does_not_merge_directory_race(wedding, monkeypatch):
    (wedding / "card/nested").mkdir(parents=True)
    plan = scan(wedding)
    native_rename = safety.rename_handle

    def race(handle, destination):
        destination.mkdir()
        native_rename(handle, destination)

    monkeypatch.setattr(safety, "rename_handle", race)
    assert not run(wedding, plan).success
    assert (wedding / "card/nested").is_dir()
    assert not (wedding / "Other Folders/card/nested").exists()


def test_permission_failure_keeps_nested_parent(wedding, monkeypatch):
    source = put(wedding, "DCIM/a/b/EML_1.NEF")
    original = source.read_bytes()
    def denied(*args):
        raise PermissionError("Simulated access denied")
    monkeypatch.setattr(safety, "rename_handle", denied)
    report = run(wedding)
    assert report.failed == 1
    assert source.read_bytes() == original
    assert not (wedding / "Other Folders/DCIM").exists()


def test_actual_locked_file_is_preserved(wedding):
    source = put(wedding, "card/EML_1.NEF")
    plan = scan(wedding)
    with locked_handle(source, directory=False):
        report = run(wedding, plan)
    assert not report.success and source.exists()


def test_cancel_after_one_file_then_resume(wedding):
    for index in range(4):
        put(wedding, f"DCIM/EML_{index}.NEF")
    before = contents(wedding)
    cancel = Event()
    def progress(result, done, total):
        if result.status == "moved":
            cancel.set()
    report = run(wedding, cancel=cancel, progress=progress)
    assert report.cancelled and report.moved["RAW"] == 1
    assert (wedding / "DCIM").exists()
    assert contents(wedding) == before
    assert run(wedding).success
    assert contents(wedding) == before


def test_journal_failure_stops_further_moves(wedding, monkeypatch):
    for index in range(3):
        put(wedding, f"card/EML_{index}.NEF")
    before = contents(wedding)
    real_write = Journal.write
    def write(self, event, **data):
        if event == "result":
            raise OSError("Log drive full")
        return real_write(self, event, **data)
    monkeypatch.setattr(Journal, "write", write)
    report = run(wedding)
    assert report.fatal_error and report.moved["RAW"] == 1
    assert len(report.results) == 4
    assert contents(wedding) == before
    assert (wedding / "card").exists()


def test_logs_are_external_complete_and_no_scan_writes(wedding):
    source = put(wedding, "DCIM/EML_1.NEF")
    before = sorted(str(p.relative_to(wedding)) for p in wedding.rglob("*"))
    plan = scan(wedding)
    assert before == sorted(str(p.relative_to(wedding)) for p in wedding.rglob("*"))
    assert not (wedding.parent / "logs").exists()
    report = run(wedding, plan)
    records = [json.loads(line) for line in report.log.read_text(encoding="utf-8").splitlines()]
    assert records[0]["event"] == "session"
    assert records[-1]["success"]
    assert any(row["event"] == "intent" and row["source"] == str(source) for row in records)
    assert not report.log.is_relative_to(wedding)


def test_log_directory_inside_wedding_refused(wedding):
    source = put(wedding, "EML_1.NEF")
    with pytest.raises(UnsafeOperation):
        organize(scan(wedding), logs=wedding / "logs")
    assert source.exists()


def test_repeated_runs_and_nested_reserved_names(wedding):
    put(wedding, "DCIM/Photos/EML_1.NEF")
    put(wedding, "DCIM/Videography/WAR_1.MOV")
    assert run(wedding).success
    plan = scan(wedding)
    assert not plan.files and not plan.folders and not plan.directories
    put(wedding, "new card/EML_2.NEF")
    before = contents(wedding)
    assert len(scan(wedding).files) == 1
    assert run(wedding).success
    assert contents(wedding) == before
    assert not scan(wedding).files


def test_windows_case_insensitive_collisions(wedding):
    put(wedding, "A/eml_1.nef", b"one")
    second = put(wedding, "B/EML_1.NEF", b"two")
    plan = scan(wedding)
    assert plan.conflicts == 1
    run(wedding, plan)
    assert second.read_bytes() == b"two"


def test_existing_lowercase_destination(wedding):
    put(wedding, "photos/raw/eml/eml_1.nef", b"existing")
    source = put(wedding, "EML_1.NEF", b"source")
    assert scan(wedding).conflicts == 1
    run(wedding)
    assert source.read_bytes() == b"source"


@pytest.mark.parametrize("reserved", ["Photos", "Videography", "Other Files", "Other Folders"])
def test_reserved_root_file_blocks_execution(wedding, reserved):
    put(wedding, reserved)
    put(wedding, "EML_1.NEF")
    plan = scan(wedding)
    assert not plan.valid
    with pytest.raises(UnsafeOperation):
        run(wedding, plan)


def test_new_content_in_source_folder_prevents_folder_move(wedding):
    put(wedding, "card/EML_1.NEF")
    plan = scan(wedding)
    late = put(wedding, "card/new.txt", b"late")
    report = run(wedding, plan)
    assert report.moved["RAW"] == 1 and report.moved["Folder"] == 0
    assert late.read_bytes() == b"late"


def test_missing_root_fails_without_changes(wedding):
    put(wedding, "EML_1.NEF")
    plan = scan(wedding)
    renamed = wedding.with_name("disconnected-backup")
    wedding.rename(renamed)
    report = run(wedding, plan)
    assert report.failed and not report.success
    assert (renamed / "EML_1.NEF").exists()


def test_replaced_root_identity_blocks_execution(wedding):
    put(wedding, "EML_1.NEF")
    plan = scan(wedding)
    wedding.rename(wedding.with_name("original-backup"))
    wedding.mkdir()
    replacement = put(wedding, "EML_1.NEF", b"replacement")
    report = run(wedding, plan)
    assert not report.success and replacement.read_bytes() == b"replacement"


def test_junction_never_followed_or_moved(wedding):
    outside = wedding.parent / "outside"
    outside.mkdir()
    original = put(outside, "EML_1.NEF", b"outside")
    link = wedding / "card" / "linked"
    link.parent.mkdir()
    # Literal, fixture-controlled paths; no deletion is delegated to cmd.
    result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True)
    assert result.returncode == 0, result.stderr
    try:
        plan = scan(wedding)
        assert not plan.files and plan.issues
        report = run(wedding, plan)
        assert not report.success and link.exists() and original.read_bytes() == b"outside"
    finally:
        # os.rmdir removes the junction itself, never its target.
        os.rmdir(link)


def test_reparse_destination_inserted_after_scan(wedding):
    source = put(wedding, "EML_1.NEF")
    plan = scan(wedding)
    outside = wedding.parent / "outside"
    outside.mkdir()
    link = wedding / "Photos"
    result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True)
    assert result.returncode == 0
    try:
        report = run(wedding, plan)
        assert not report.success and source.exists() and not list(outside.iterdir())
    finally:
        os.rmdir(link)


def test_symlink_file_excluded(wedding):
    outside = put(wedding.parent, "outside.NEF", b"outside")
    link = wedding / "EML_link.NEF"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"Windows symlink privilege unavailable: {exc}")
    plan = scan(wedding)
    assert not plan.files and plan.issues
    assert not run(wedding, plan).success
    assert link.is_symlink() and outside.read_bytes() == b"outside"


def test_scan_permission_failure_disables_plan(wedding, monkeypatch):
    import wedding_organizer.planner as planner
    put(wedding, "card/EML_1.NEF")
    real_scandir = os.scandir
    def denied(path):
        if Path(path).name == "card":
            raise PermissionError("Unreadable directory")
        return real_scandir(path)
    monkeypatch.setattr(planner.os, "scandir", denied)
    plan = scan(wedding)
    assert not plan.valid and plan.issues


def test_scan_cancellation_is_read_only(wedding):
    source = put(wedding, "EML_1.NEF")
    event = Event()
    event.set()
    plan = scan(wedding, event)
    assert plan.cancelled and not plan.valid and source.exists()


def test_cross_filesystem_snapshot_rejected(wedding):
    from dataclasses import replace
    source = put(wedding, "EML_1.NEF")
    plan = scan(wedding)
    plan.root_snapshot = replace(plan.root_snapshot, device=plan.root_snapshot.device + 1)
    report = run(wedding, plan)
    assert not report.success and source.exists()


def test_many_files_and_deep_tree(wedding):
    deep = "card/" + "a/" * 55
    for index in range(1100):
        put(wedding, (deep if index < 2 else "card/") + f"EML_{index:04}.NEF", str(index).encode())
    before = contents(wedding)
    plan = scan(wedding)
    assert len(plan.files) == 1100
    report = run(wedding, plan)
    assert report.success, report
    assert contents(wedding) == before
    assert not scan(wedding).files


def test_unicode_paths_and_filenames_preserved(wedding):
    put(wedding, "විවාහය/EML_මතකය.NEF", b"original")
    report = run(wedding)
    assert report.success, report
    assert (wedding / "Photos/Raw/EML/EML_මතකය.NEF").read_bytes() == b"original"


def test_source_handle_blocks_concurrent_writer(wedding, monkeypatch):
    source = put(wedding, "EML_1.NEF", b"original")
    native_rename = safety.rename_handle
    def try_write(handle, destination):
        with pytest.raises(PermissionError):
            source.write_bytes(b"changed")
        native_rename(handle, destination)
    monkeypatch.setattr(safety, "rename_handle", try_write)
    assert run(wedding).success
    assert (wedding / "Photos/Raw/EML/EML_1.NEF").read_bytes() == b"original"


def test_destination_ancestor_cannot_be_replaced_during_move(wedding, monkeypatch):
    put(wedding, "EML_1.NEF")
    native_rename = safety.rename_handle
    def try_replace(handle, destination):
        with pytest.raises(PermissionError):
            destination.parent.rename(destination.parent.with_name("swapped"))
        native_rename(handle, destination)
    monkeypatch.setattr(safety, "rename_handle", try_replace)
    assert run(wedding).success


def test_abrupt_process_exit_after_rename_resumes(wedding):
    import sys
    for index in range(4):
        put(wedding, f"card/EML_{index}.NEF")
    before = contents(wedding)
    script = """
import os, sys
from pathlib import Path
from wedding_organizer.engine import organize
from wedding_organizer.planner import scan
from wedding_organizer.safety import WindowsMover
class InterruptedMover(WindowsMover):
    def move(self, *args, **kwargs):
        super().move(*args, **kwargs)
        os._exit(73)
root = Path(sys.argv[1])
organize(scan(root), logs=root.parent / 'logs', mover=InterruptedMover())
"""
    result = subprocess.run([sys.executable, "-c", script, str(wedding)], cwd=Path(__file__).parents[1])
    assert result.returncode == 73
    assert contents(wedding) == before
    records = [json.loads(line) for p in (wedding.parent / "logs").glob("*.jsonl") for line in p.read_text().splitlines()]
    assert records[-1]["event"] == "intent"
    assert len(scan(wedding).files) == 3
    assert run(wedding).success
    assert contents(wedding) == before


def test_insufficient_storage_error_preserves_source(wedding, monkeypatch):
    source = put(wedding, "card/EML_1.NEF", b"original")
    def disk_full(*args):
        raise OSError(112, "Not enough space on the disk")
    monkeypatch.setattr(safety, "rename_handle", disk_full)
    report = run(wedding)
    assert report.failed == 1 and source.read_bytes() == b"original"
    assert (wedding / "card").exists()


def test_destination_parent_is_a_file(wedding):
    source = put(wedding, "EML_1.NEF", b"original")
    put(wedding, "Photos/Raw", b"existing")
    plan = scan(wedding)
    assert plan.conflicts == 1
    assert not run(wedding, plan).success
    assert source.read_bytes() == b"original"
    assert (wedding / "Photos/Raw").read_bytes() == b"existing"


def test_no_fixed_depth_limit(wedding):
    # Explicit extended paths create a fixture beyond legacy Windows MAX_PATH.
    path = wedding
    for index in range(105):
        path /= "a"
    native = Path(safety.native_path(path))
    native.mkdir(parents=True)
    (native / "EML_1.NEF").write_bytes(b"deep")
    plan = scan(wedding)
    assert len(plan.files) == 1 and len(plan.directories) == 105
    assert run(wedding, plan).success
