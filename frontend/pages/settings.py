"""
Settings -- a configuration studio giving visibility into the real
values the pipeline runs with (config.py, models/theme.py). These are
process-level constants rather than a database-backed settings table,
so this page is an honest reference view organized by category rather
than a form pretending to persist changes the backend doesn't support.
"""
import os

import streamlit as st

import config
from config import RSS_FEEDS, SOURCE_TIER, MAX_SELECTED_TOPICS, USE_LLM, OPENROUTER_MODEL
from models.theme import Theme
from frontend.version import APP_VERSION, read_changelog_entries


def _row(label, value):
    st.markdown(
        f'<div class="source-row"><div class="source-name">{label}</div>'
        f'<div class="source-count" style="flex:0 0 auto;text-align:right;">{value}</div></div>',
        unsafe_allow_html=True,
    )


def render():
    st.markdown(
        '<div class="section-head"><div class="section-title">System Settings</div>'
        '<div class="section-note">Configuration reference</div></div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["General", "AI Engine", "Sources", "Visuals", "Presentation", "System"])

    with tabs[0]:
        st.markdown('<div class="kicker">General</div>', unsafe_allow_html=True)
        _row("Default topic slide target", MAX_SELECTED_TOPICS)
        _row("Default output filename", config.OUTPUT_FILENAME)
        _row("Output directory", config.OUTPUT_DIR)

    with tabs[1]:
        st.markdown('<div class="kicker">AI Engine</div>', unsafe_allow_html=True)
        _row("LLM analysis enabled", "Yes" if USE_LLM else "No — template fallback")
        _row("Model", OPENROUTER_MODEL)
        _row("Temperature", config.TEMPERATURE)
        _row("Max tokens", config.MAX_TOKENS)
        _row("Max retries", config.MAX_RETRIES)
        if not USE_LLM:
            st.info("USE_LLM is False in config.py — every article will use the deterministic template fallback.")

    with tabs[2]:
        st.markdown(f'<div class="kicker">{len(RSS_FEEDS)} Sources Configured</div>', unsafe_allow_html=True)
        for name, url in RSS_FEEDS.items():
            tier = "Tier 1 · Primary" if SOURCE_TIER.get(name) == 1 else "Tier 2 · Press"
            st.markdown(
                f'<div class="source-row"><div class="source-name">{name}</div>'
                f'<div class="source-tier">{tier}</div>'
                f'<div style="flex:2;font-size:11.5px;color:#63636A;text-align:right;overflow:hidden;'
                f'text-overflow:ellipsis;white-space:nowrap;">{url}</div></div>',
                unsafe_allow_html=True,
            )

    with tabs[3]:
        st.markdown('<div class="kicker">Visuals</div>', unsafe_allow_html=True)
        st.caption(
            "The Visual Library (page 04) is built from `config/visual_taxonomy.json` via "
            "`python tools/download_images.py`. Populate a `PEXELS_API_KEY` or "
            "`UNSPLASH_ACCESS_KEY` in `.env` to fetch the full curated set."
        )

    with tabs[4]:
        st.markdown('<div class="kicker">Presentation Themes</div>', unsafe_allow_html=True)
        for name in Theme.NAMES:
            desc = (
                "White/light backgrounds, near-black type, Bosch Red used sparingly as a sharp accent."
                if name == "Bosch Corporate"
                else "Dark navy backgrounds, warm gold accent, full-bleed photography."
            )
            st.markdown(
                f'<div class="source-row"><div class="source-name">{name}</div>'
                f'<div style="flex:2;font-size:12px;color:#63636A;">{desc}</div></div>',
                unsafe_allow_html=True,
            )

    with tabs[5]:
        st.markdown('<div class="kicker">System</div>', unsafe_allow_html=True)
        _row("App version", APP_VERSION)
        _row("Section divider threshold", f"{config.MIN_TOPICS_FOR_SECTION_DIVIDER} topics")
        _row("Activity log", "logs/activity.log")
        _row("Feedback log", "data/feedback.jsonl")

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="kicker">Feedback notifications</div>', unsafe_allow_html=True)
        _row("Feedback email recipient", os.environ.get("FEEDBACK_EMAIL_TO", "rby4kor@bosch.com"))
        smtp_configured = bool(os.environ.get("SMTP_HOST") and os.environ.get("SMTP_USERNAME"))
        _row("SMTP configured", "Yes" if smtp_configured else "No — set SMTP_HOST / SMTP_USERNAME / SMTP_PASSWORD")
        if not smtp_configured:
            st.info(
                "Feedback is always saved to `data/feedback.jsonl`. To also have it "
                "emailed, set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` "
                "(and optionally `FEEDBACK_EMAIL_FROM` / `FEEDBACK_EMAIL_TO`) as environment "
                "variables on the deployment — see `utils/email_utils.py`."
            )

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="kicker">What changed</div>', unsafe_allow_html=True)
        st.caption("Read from `CHANGELOG.md` — one section per version, most recent first.")
        entries = read_changelog_entries()
        if not entries:
            st.info("No CHANGELOG.md found.")
        for entry in entries[:6]:
            with st.expander(f"v{entry['version']} — {entry['date']}", expanded=(entry is entries[0])):
                for line in entry["lines"]:
                    st.markdown(f"- {line}")
