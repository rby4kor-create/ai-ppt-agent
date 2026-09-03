import streamlit as st
from datetime import date, datetime, timedelta

from config import RSS_FEEDS, MAX_SELECTED_TOPICS
from models.theme import Theme


def _week_bounds(offset_weeks=0):
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    if offset_weeks == 0:  # current (in-progress) week
        start = this_monday
        end = today
    else:  # last completed week
        start = this_monday - timedelta(days=7)
        end = this_monday - timedelta(days=1)
    return start, end


def configuration():
    """
    Renders the report configuration panel and returns the selected
    values as a dict, so the Generate button can pass them straight into
    run_pipeline(). Previously these widgets rendered but nothing read
    their values - the pipeline always ran with hardcoded defaults
    regardless of what was selected here.
    """

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Report Configuration")

        report = st.radio("", ["Current Week", "Last Week", "Custom Range"])

        if report == "Custom Range":
            c1, c2 = st.columns(2)
            with c1:
                start_date = st.date_input("Start", date.today() - timedelta(days=7))
            with c2:
                end_date = st.date_input("End", date.today())
        elif report == "Last Week":
            start_date, end_date = _week_bounds(offset_weeks=1)
        else:
            start_date, end_date = _week_bounds(offset_weeks=0)

        source_names = list(RSS_FEEDS.keys())
        selected_sources = st.multiselect(
            "Sources",
            source_names,
            default=source_names[:5],
        )

    with right:
        st.subheader("Settings")

        theme = st.selectbox(
            "Theme", Theme.NAMES,
            help="Bosch Corporate: white/light, red accent. "
                 "Modern Executive: dark navy, gold accent, full-bleed photography.",
        )
        generate_images = st.toggle("Generate Images", True)
        executive_summary = st.toggle("Executive Summary", True)
        dashboard = st.toggle("Dashboard", True)
        references = st.toggle("References", True)
        max_topics = st.slider("Max topic slides", min_value=3, max_value=12, value=MAX_SELECTED_TOPICS)

    return {
        "start_date": datetime.combine(start_date, datetime.min.time()),
        "end_date": datetime.combine(end_date, datetime.max.time().replace(microsecond=0)),
        "sources": selected_sources or source_names,
        "theme": theme,
        "generate_images": generate_images,
        "show_executive_summary": executive_summary,
        "show_dashboard": dashboard,
        "show_references": references,
        "max_topics": max_topics,
    }
