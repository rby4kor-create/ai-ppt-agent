"""
Activity -- editorial timeline redesign of frontend/activity_log.py's
data (same on-disk logs/activity.log, same log_event() writer used
everywhere in the app). Only the rendering changed: a real timeline
with a connecting rule, instead of a monospace table.
"""
import os

import streamlit as st

from frontend.activity_log import (
    EVENT_LABELS,
    LOG_PATH,
    _read_all_entries,
    _session_id,
)


def render():
    st.markdown(
        '<div class="section-head"><div class="section-title">Activity Log</div>'
        '<div class="section-note">Every action, written to disk</div></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "A running record of what happened in this app -- page views, topic picks, "
        f"report generations, downloads, and feedback -- written to `logs/activity.log` "
        "on every action so it survives restarts."
    )

    entries = list(reversed(_read_all_entries()))

    html = f"""
<div class="metric-strip">
    <div class="metric-cell"><div class="m-label">Total Events</div><div class="m-value">{len(entries)}</div></div>
    <div class="metric-cell"><div class="m-label">Sessions Seen</div><div class="m-value">{len({e.get('session') for e in entries})}</div></div>
    <div class="metric-cell"><div class="m-label">This Session</div><div class="m-value" style="font-size:16px;">{_session_id()}</div></div>
</div>
""".strip()
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

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
        with open(LOG_PATH, "rb") as f:
            st.download_button(
                "Download raw log file (.log)", data=f, file_name="activity.log",
                mime="text/plain", use_container_width=True,
            )

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    if not filtered:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-eyebrow">Nothing Yet</div>'
            '<div class="empty-title">No activity recorded yet</div>'
            '<div class="empty-sub">Actions across the workspace will show up here as they happen.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    rows = []
    for e in filtered[:300]:
        label, _kind = EVENT_LABELS.get(e["event"], (e["event"], "info"))
        detail_bits = " &middot; ".join(f"{k}: {v}" for k, v in (e.get("details") or {}).items())
        ts = e.get("ts", "")
        time_part = ts.split("T")[-1] if "T" in ts else ts
        rows.append(
            f'<div class="tl-row">'
            f'<div class="tl-time">{time_part}</div>'
            f'<div class="tl-line"></div>'
            f'<div style="flex:1;">'
            f'<div class="tl-event">{label}</div>'
            f'<div class="tl-detail">{detail_bits}</div>'
            f'</div>'
            f'</div>'
        )
    st.markdown("".join(rows), unsafe_allow_html=True)

    if len(filtered) > 300:
        st.caption(f"...and {len(filtered) - 300} more. Download the log file to see everything.")
