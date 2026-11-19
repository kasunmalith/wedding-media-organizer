from pathlib import Path
import os

import pytest

from wedding_organizer.engine import organize
from wedding_organizer.planner import scan
import wedding_organizer.safety as safety

pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Windows native move backend')


@pytest.mark.parametrize('filename,directory', [
    ('_MSP7396.NEF', 'Photos/Raw/MSP'),
    ('_msp7396.nef', 'Photos/Raw/MSP'),
    ('__MSP7396.ARW', 'Photos/Raw/MSP'),
    ('_MSP7396.JPG', 'Photos/Jpg/MSP'),
    ('_MSP7396.JPEG', 'Photos/Jpg/MSP'),
    ('_MSP7396.MOV', 'Videography/MSP'),
    ('_MSP7396.MP4', 'Videography/MSP'),
    ('_rec.WAV', 'Videography/Audio'),
])
def test_leading_underscores_classify_without_renaming(tmp_path, filename, directory):
    root = tmp_path / 'Wedding'
    parent = root / 'card/nested'
    parent.mkdir(parents=True)
    source = parent / filename
    source.write_bytes(b'original dummy bytes')
    plan = scan(root)
    assert plan.files[0].destination == root / directory / filename
    assert source.exists()
    report = organize(plan, logs=tmp_path / 'logs')
    assert report.success, report
    assert (root / directory / filename).read_bytes() == b'original dummy bytes'
    assert (root / 'Other Folders/card/nested').is_dir()


@pytest.mark.parametrize('filename', ['_AB.NEF', '__.JPG', '_A_B.MOV', '_CON7396.NEF'])
def test_underscore_does_not_bypass_invalid_prefix_checks(tmp_path, filename):
    root = tmp_path / 'Wedding'
    root.mkdir()
    (root / filename).write_bytes(b'dummy')
    plan = scan(root)
    assert plan.files[0].category == 'Other'
    assert plan.files[0].reason.startswith('Invalid')


def test_five_source_folders_and_nested_miscellaneous(tmp_path):
    root = tmp_path / 'Wedding'
    expected = {}
    for folder in ('2', '6g', 'f9', 'L8', 'r3'):
        parent = root / folder / 'DCIM' / 'nested'
        parent.mkdir(parents=True)
        for extension in ('NEF', 'JPG', 'MOV', 'MP4', 'WAV', 'XML', 'XMP', 'DAT', 'THM'):
            name = f'ABC_{folder}.{extension}'
            content = f'dummy original {folder} {extension}'.encode()
            (parent / name).write_bytes(content)
            expected[name] = content
    plan = scan(root)
    report = organize(plan, logs=tmp_path / 'logs')
    assert report.success, report
    assert report.moved['Other'] == 20 and report.moved['Folder'] == 5
    assert {p.name for p in root.iterdir()} == {'Photos', 'Videography', 'Other Files', 'Other Folders'}
    for folder in ('2', '6g', 'f9', 'L8', 'r3'):
        assert (root / 'Other Folders' / folder / 'DCIM/nested').is_dir()
        assert (root / 'Other Files' / folder / 'DCIM/nested' / f'ABC_{folder}.XML').is_file()
    assert {p.name: p.read_bytes() for p in root.rglob('*') if p.is_file()} == expected


def test_post_rename_path_inode_may_change(tmp_path, monkeypatch):
    root = tmp_path / 'Wedding'
    (root / '2').mkdir(parents=True)
    (root / '2' / 'ABC_1.NEF').write_bytes(b'dummy original')
    plan = scan(root)
    destinations = {op.destination for op in [*plan.files, *plan.folders]}
    original_stat = safety.file_stat

    class RenumberedStat:
        def __init__(self, value):
            self.value = value
        def __getattr__(self, name):
            if name == 'st_ino':
                return self.value.st_ino + 10000
            return getattr(self.value, name)

    def stat_after_rename(path):
        value = original_stat(path)
        return RenumberedStat(value) if path in destinations else value

    monkeypatch.setattr(safety, 'file_stat', stat_after_rename)
    report = organize(plan, logs=tmp_path / 'logs')
    assert report.success, report
    assert report.moved['RAW'] == 1 and report.moved['Folder'] == 1


def test_different_live_destination_identity_is_still_rejected(tmp_path, monkeypatch):
    root = tmp_path / 'Wedding'
    (root / '2').mkdir(parents=True)
    (root / '2' / 'ABC_1.NEF').write_bytes(b'dummy original')
    original_information = safety.handle_information
    calls = 0

    def mismatch(handle):
        nonlocal calls
        calls += 1
        volume, identity, size = original_information(handle)
        return volume, identity + (1000 if calls == 2 else 0), size

    monkeypatch.setattr(safety, 'handle_information', mismatch)
    report = organize(scan(root), logs=tmp_path / 'logs')
    assert report.failed == 1 and not report.success
    assert (root / 'Photos/Raw/ABC/ABC_1.NEF').read_bytes() == b'dummy original'
    assert (root / '2').is_dir()
