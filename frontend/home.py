"""
Router for the Bosch AI Intelligence Workspace. Replaces the old
single-file home_page() (sidebar + hero + cards + dashboard + inline
fetch/generate logic) with: global CSS, the new shell (left nav + top
header), and a dispatch to one of frontend/pages/*.py.

Every backend call this used to make directly now lives inside the
page modules it moved to (mainly frontend/pages/generate.py) --
nothing in app.py, the agents, or the services changed.
"""
import streamlit as st

from config import RSS_FEEDS
from frontend.design_system import inject_global_css
from frontend.shell import sidebar_nav, top_header, footer
from frontend.activity_log import log_event
from frontend.feedback_widget import render_feedback_widget

from frontend.pages import overview, intelligence, generate, visuals, reports, analytics, activity, settings

PAGES = {
    "Overview": overview,
    "Intelligence": intelligence,
    "Generate": generate,
    "Visuals": visuals,
    "Reports": reports,
    "Analytics": analytics,
    "Activity Log": activity,
    "Settings": settings,
}


def _week_label():
    from datetime import date
    today = date.today()
    return f"Week {today.isocalendar()[1]}"


def home_page():
    inject_global_css()

    if "session_started" not in st.session_state:
        st.session_state["session_started"] = True
        log_event("session_start")

    nav = sidebar_nav()

    if st.session_state.get("last_nav_logged") != nav:
        log_event("page_view", {"page": nav})
        st.session_state["last_nav_logged"] = nav

    top_header(sources_count=len(RSS_FEEDS), week_label=_week_label())

    page_module = PAGES.get(nav, overview)
    page_module.render()

    footer()
    render_feedback_widget()
