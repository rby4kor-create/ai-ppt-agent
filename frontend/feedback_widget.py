"""
Floating feedback widget: a small round button pinned to the bottom
right of the screen. Clicking it expands a compact card where anyone
-- including someone who wants to flag discomfort, confusion, a bug,
or anything else about the experience -- can leave a note. Submissions
are appended to data/feedback.jsonl and mirrored into the activity log.

Because Streamlit has no client-side JS<->Python bridge without a
custom component, "floating" + "expandable" is built as: a
fixed-position container (CSS) whose contents toggle between a small
circular button and an open card, driven by normal Streamlit state
(a rerun on click) -- so it behaves like a floating chat/feedback
widget without needing a custom frontend build.
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

from frontend.activity_log import log_event
from utils.email_utils import send_feedback_email

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.jsonl")

MOODS = [
    ("great", "🟢 Going well"),
    ("mixed", "🟡 Mixed / unsure"),
    ("uncomfortable", "🔴 Something's off"),
]


def _save_feedback(entry: dict):
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def render_feedback_widget():
    st.session_state.setdefault("feedback_open", False)
    st.session_state.setdefault("feedback_sent", False)

    # A *keyed* container gets a stable, real wrapping <div> in the DOM
    # (class "st-key-feedback_widget_fab"), which styles.py pins to the
    # viewport corner with position:fixed. A plain st.markdown div does
    # NOT wrap the widgets rendered after it -- Streamlit renders each
    # element as an independent sibling -- so that approach silently
    # fails to float anything; this is the mechanism that actually works.
    with st.container(key="feedback_widget_fab"):
        if not st.session_state["feedback_open"]:
            if st.button("💬 Feedback", key="feedback_fab_open", help="Share feedback or report discomfort"):
                st.session_state["feedback_open"] = True
                st.session_state["feedback_sent"] = False
                st.rerun()
        else:
            with st.container(border=True):
                st.markdown("**We're listening**")
                st.caption(
                    "Something confusing, uncomfortable, or just plain wrong? "
                    "Say it here -- it goes straight into a private log, no judgement."
                )

                if st.session_state["feedback_sent"]:
                    st.success("Thanks -- this has been recorded. You can close this now.")
                    if st.button("Close", key="feedback_close_after_send", use_container_width=True):
                        st.session_state["feedback_open"] = False
                        st.session_state["feedback_sent"] = False
                        st.rerun()
                else:
                    mood_key = st.radio(
                        "How's this feeling?",
                        options=[m[0] for m in MOODS],
                        format_func=lambda k: dict(MOODS)[k],
                        key="feedback_mood",
                        horizontal=False,
                    )
                    message = st.text_area(
                        "Your message",
                        key="feedback_message",
                        placeholder="Tell us what's going on -- as much or as little detail as you want.",
                        height=120,
                    )
                    contact = st.text_input(
                        "Email (optional, if you'd like a reply)",
                        key="feedback_contact",
                        placeholder="you@example.com",
                    )

                    c1, c2 = st.columns([1, 1])
                    with c1:
                        submit = st.button("Send", key="feedback_submit", use_container_width=True, type="primary")
                    with c2:
                        cancel = st.button("Cancel", key="feedback_cancel", use_container_width=True)

                    if submit:
                        if not message.strip():
                            st.warning("Add a note before sending -- even one line helps.")
                        else:
                            entry = {
                                "id": uuid.uuid4().hex[:10],
                                "ts": datetime.now().isoformat(timespec="seconds"),
                                "mood": mood_key,
                                "message": message.strip(),
                                "contact": contact.strip() or None,
                                "page": st.session_state.get("nav_page", "Dashboard"),
                            }
                            try:
                                _save_feedback(entry)
                            except Exception as e:
                                st.error(f"Couldn't save feedback locally: {e}")
                            else:
                                log_event("feedback_submitted", {"mood": mood_key})
                                emailed, detail = send_feedback_email(entry)
                                if emailed:
                                    log_event("feedback_emailed", {"to": "rby4kor@bosch.com"})
                                elif detail != "smtp_not_configured":
                                    # Configured but the send itself failed (bad
                                    # creds, network, etc) -- worth a record since
                                    # it's silent to the person submitting.
                                    log_event("feedback_email_failed", {"reason": detail})
                                st.session_state["feedback_sent"] = True
                                st.rerun()

                    if cancel:
                        st.session_state["feedback_open"] = False
                        st.rerun()


def load_feedback_entries():
    """Used by the admin/analytics-style view if the operator wants to review submissions."""
    if not os.path.exists(FEEDBACK_PATH):
        return []
    entries = []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries
