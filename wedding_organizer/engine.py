from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from typing import Callable
import json
import os
import uuid

from .model import Plan, Report, Result
from .safety import WindowsMover, UnsafeOperation


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
