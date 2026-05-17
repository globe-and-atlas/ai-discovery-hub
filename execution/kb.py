#!/usr/bin/env python3
"""
kb.py — Knowledge Base logging utilities for AI Discovery Hub.

Provides two functions:
    log_error()          → knowledge/ERRORS.md   (infrastructure error table)
    log_session_event()  → knowledge/SESSION.md  (checkpoint line)

Import at the top of any execution script and call from try/except and atexit handlers.
Both functions are write-only and never raise — safe to call from exception handlers.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def log_error(
    project_root: Path | str,
    script_name: str,
    symptom: str,
    cause: str,
    fix: str = "(investigate)",
    error_class: str = "infrastructure",
) -> None:
    """
    Append an error row to knowledge/ERRORS.md.

    Args:
        project_root: Path to the project root (where knowledge/ lives)
        script_name:  The script that encountered the error (e.g. "fetch_feed.py")
        symptom:      What happened (short, one-line)
        cause:        Why it happened (short, one-line)
        fix:          How to fix / what was done
        error_class:  "deterministic" or "infrastructure" — controls table section
    """
    try:
        errors_path = Path(project_root) / "knowledge" / "ERRORS.md"
        if not errors_path.exists():
            return

        date = datetime.now().strftime("%Y-%m-%d")
        row = f"| {date} | {script_name} | {symptom} | {fix} |\n"

        content = errors_path.read_text(encoding="utf-8")

        # Append to the infrastructure table if it exists; otherwise append at end
        marker = "## Infrastructure Errors"
        if marker in content and "| Date |" in content:
            # Find the last row of the table and append after it
            lines = content.splitlines(keepends=True)
            insert_at = len(lines)
            in_infra = False
            for i, line in enumerate(lines):
                if marker in line:
                    in_infra = True
                if in_infra and line.startswith("|") and not line.startswith("| Date") and not line.startswith("|---"):
                    insert_at = i + 1
            lines.insert(insert_at, row)
            errors_path.write_text("".join(lines), encoding="utf-8")
        else:
            # Append a minimal infrastructure section
            errors_path.write_text(
                content.rstrip()
                + f"\n\n## Infrastructure Errors (auto-captured)\n\n"
                + "| Date | Script | Error | Notes |\n"
                + "|---|---|---|---|\n"
                + row,
                encoding="utf-8",
            )
    except Exception:
        pass  # Never let logging crash the caller


def log_session_event(
    project_root: Path | str,
    script_name: str,
    status: str,
    notes: str = "",
) -> None:
    """
    Append a checkpoint line to knowledge/SESSION.md.

    Args:
        project_root: Path to the project root (where knowledge/ lives)
        script_name:  The script that is logging (e.g. "build_hub.py")
        status:       Short status label ("completed", "failed", "exited_unexpectedly", etc.)
        notes:        Optional one-line detail (counts, filenames, error snippet)
    """
    try:
        session_path = Path(project_root) / "knowledge" / "SESSION.md"
        if not session_path.exists():
            return

        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        line = f"- {ts} — {script_name} → {status}"
        if notes:
            line += f" | {notes}"
        line += "\n"

        content = session_path.read_text(encoding="utf-8")

        # Find the Checkpoint Log section and append there; otherwise append at end
        marker = "## Checkpoint Log"
        if marker in content:
            lines = content.splitlines(keepends=True)
            insert_at = len(lines)
            in_section = False
            for i, line_text in enumerate(lines):
                if marker in line_text:
                    in_section = True
                    insert_at = i + 1
                    continue
                if in_section and line_text.startswith("## "):
                    insert_at = i
                    break
                if in_section:
                    insert_at = i + 1
            lines.insert(insert_at, line)
            session_path.write_text("".join(lines), encoding="utf-8")
        else:
            session_path.write_text(
                content.rstrip() + f"\n\n## Checkpoint Log\n\n" + line,
                encoding="utf-8",
            )
    except Exception:
        pass  # Never let logging crash the caller
