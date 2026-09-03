"""
App version + changelog.

CHANGELOG.md at the repo root is the single source of truth for "what
changed since the last version" -- every release adds a dated section
there. This module just parses it so the Settings page (and the
Activity Log) can show it inside the app, instead of it being a file
nobody opens.

Bump APP_VERSION and add a matching "## [x.y.z] - YYYY-MM-DD" section
to CHANGELOG.md whenever you ship a change.
"""
import os
import re
from pathlib import Path

APP_VERSION = "1.1.0"

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG_PATH = os.path.join(ROOT_DIR, "CHANGELOG.md")

_ENTRY_RE = re.compile(r"^##\s*\[(?P<version>[^\]]+)\]\s*-\s*(?P<date>\d{4}-\d{2}-\d{2})\s*$")


def read_changelog_entries():
    """
    Parses CHANGELOG.md into a list of
    {"version": "1.1.0", "date": "2026-09-02", "lines": ["...", "..."]}
    dicts, most recent first (top of file = most recent, by convention).
    Returns [] if the file is missing rather than raising -- a missing
    changelog should never break the Settings page.
    """
    path = Path(CHANGELOG_PATH)
    if not path.exists():
        return []

    entries = []
    current = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        match = _ENTRY_RE.match(raw_line.strip())
        if match:
            if current:
                entries.append(current)
            current = {"version": match.group("version"), "date": match.group("date"), "lines": []}
            continue
        if current is None:
            continue
        line = raw_line.strip()
        if line.startswith("- "):
            current["lines"].append(line[2:].strip())
    if current:
        entries.append(current)
    return entries


def latest_entry():
    entries = read_changelog_entries()
    return entries[0] if entries else None
