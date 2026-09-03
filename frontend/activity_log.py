"""
Activity log: records what the person actually did in this app --
page views, topic selection, generation runs, downloads, feedback
submissions -- to a real file on disk (logs/activity.log, one JSON
object per line) so it survives page reloads and can be inspected,
searched, or handed to someone else, not just kept in memory for the
current session.

Usage:
    from frontend.activity_log import log_event, render_activity_log_page

    log_event("topic_selected", {"title": article.title})
    ...
    render_activity_log_page()   # inside the "Activity Log" nav page
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

from frontend.version import APP_VERSION, CHANGELOG_PATH, latest_entry

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
LOG_PATH = os.path.join(LOG_DIR, "activity.log")

EVENT_LABELS = {
    "session_start": ("Session started", "info"),
    "page_view": ("Viewed page", "info"),
    "topics_fetch_started": ("Started topic search", "info"),
    "topics_fetch_completed": ("Topic search completed", "ok"),
    "topics_fetch_failed": ("Topic search failed", "danger"),
    "topic_selected": ("Selected topic", "ok"),
    "topic_deselected": ("Deselected topic", "warn"),
    "image_override": ("Changed slide image", "info"),
    "generation_started": ("Started report generation", "info"),
    "generation_completed": ("Report generated", "ok"),
    "generation_failed": ("Report generation failed", "danger"),
    "report_downloaded": ("Downloaded report", "ok"),
    "feedback_submitted": ("Feedback submitted", "info"),
    "feedback_emailed": ("Feedback emailed", "ok"),
    "feedback_email_failed": ("Feedback email failed", "danger"),
}


def _ensure_log_file():
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(LOG_PATH):
        Path(LOG_PATH).touch()


def _session_id():
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid4().hex[:8]
    return st.session_state["session_id"]


def log_event(event: str, details: dict | None = None):
    """
    Appends one action to the on-disk activity log (JSON-lines) and to
    the in-memory session list used for the "just now" view. Never
    raises -- a logging failure should never break the actual pipeline
    action it's describing.
    """
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "session": _session_id(),
        "event": event,
        "details": details or {},
    }

    st.session_state.setdefault("activity_log_session", []).append(entry)

    try:
        _ensure_log_file()
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # best-effort; the UI action itself must not fail because of this


def _read_all_entries():
    _ensure_log_file()
    entries = []
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return entries


def _badge_class(kind):
    return {
        "ok": "badge-ok",
        "warn": "badge-warn",
        "info": "badge-info",
        "danger": "badge-danger",
    }.get(kind, "badge-info")


def render_activity_log_page():
    st.markdown(
        '<div class="section-title"><span class="dot"></span>Activity Log</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "A running record of what happened in this app -- page views, topic "
        "picks, report generations, downloads, and feedback -- written to "
        f"`logs/activity.log` on every action so it survives restarts."
    )

    latest = latest_entry()
    if latest:
        st.caption(
            f"Running **v{APP_VERSION}**"
            + (f" · latest changelog entry: v{latest['version']} ({latest['date']})" if latest else "")
            + " — see System Settings for full version history."
        )

    entries = list(reversed(_read_all_entries()))

    m1, m2, m3 = st.columns(3)
    m1.metric("Total events logged", len(entries))
    sessions = {e.get("session") for e in entries}
    m2.metric("Sessions seen", len(sessions))
    m3.metric("This session", _session_id())

    st.divider()

    all_events = sorted({e["event"] for e in entries})
    col1, col2 = st.columns([2, 1])
    with col1:
        event_filter = st.multiselect(
            "Filter by event type", all_events, default=[],
            format_func=lambda e: EVENT_LABELS.get(e, (e, "info"))[0],
        )
    with col2:
        only_this_session = st.toggle("Only this session", value=False)

    filtered = entries
    if event_filter:
        filtered = [e for e in filtered if e["event"] in event_filter]
    if only_this_session:
        sid = _session_id()
        filtered = [e for e in filtered if e.get("session") == sid]

    st.caption(f"Showing {len(filtered)} of {len(entries)} event(s), most recent first.")

    if os.path.exists(LOG_PATH):
        dl1, dl2 = st.columns(2)
        with dl1:
            with open(LOG_PATH, "rb") as f:
                st.download_button(
                    "Download raw log file (.log)",
                    data=f,
                    file_name="activity.log",
                    mime="text/plain",
                    use_container_width=True,
                )
        with dl2:
            if os.path.exists(CHANGELOG_PATH):
                with open(CHANGELOG_PATH, "rb") as f:
                    st.download_button(
                        "Download changelog (CHANGELOG.md)",
                        data=f,
                        file_name="CHANGELOG.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if not filtered:
        st.info("No activity recorded yet -- actions across the app will show up here as they happen.")
        return

    for e in filtered[:300]:
        label, kind = EVENT_LABELS.get(e["event"], (e["event"], "info"))
        detail_bits = ", ".join(f"{k}: {v}" for k, v in (e.get("details") or {}).items())
        html = f"""
<div class="log-line">
<span class="log-time">{e.get('ts', '')}</span>
<span class="badge {_badge_class(kind)}">{label}</span>
<span class="log-detail">{detail_bits}</span>
</div>
""".strip()
        st.markdown(html, unsafe_allow_html=True)

    if len(filtered) > 300:
        st.caption(f"...and {len(filtered) - 300} more. Download the log file to see everything.")
