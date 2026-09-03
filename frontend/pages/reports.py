"""
Reports -- a professional publishing library of everything generated
this session (st.session_state["report_history"], appended to by
frontend/pages/generate.py on every successful run). There is no
persistent report database in the backend, so history is honestly
scoped to "this session" rather than inventing a fake archive across
restarts.

Selecting a report opens a presentation detail view: real metadata,
download, and -- since the backend has no slide-to-image renderer --
an honest note rather than a fabricated slide-by-slide viewer.
"""
from datetime import date
from pathlib import Path

import streamlit as st

COVER_CANDIDATES = ["assets/cover_ai.png", "assets/cover_hero.png"]


def _cover_image_path():
    for p in COVER_CANDIDATES:
        if Path(p).exists():
            return p
    return None


def _render_library(history):
    st.markdown(f'<div class="kicker">{date.today().year}</div>', unsafe_allow_html=True)

    cover = _cover_image_path()

    for i, entry in enumerate(history):
        cols = st.columns([1, 4, 1])
        with cols[0]:
            if cover:
                st.markdown(
                    f'<div class="report-thumb"><img src="data:image/png;base64,{_b64(cover)}"></div>',
                    unsafe_allow_html=True,
                )
        with cols[1]:
            week = entry["generated_at"].isocalendar()[1]
            st.markdown(
                f"""
<div class="report-week">Week {week} &middot; {entry['theme']}</div>
<div class="report-title">Enterprise AI Intelligence</div>
<div class="report-sub">{len(entry['sources'])} sources &middot; {entry['selected']} signals &middot; {entry['slides']} slides &middot; generated {entry['generated_at']:%d %b, %H:%M}</div>
""".strip(),
                unsafe_allow_html=True,
            )
        with cols[2]:
            if st.button("Open →", key=f"open_report_{i}", use_container_width=True):
                st.session_state["viewing_report_idx"] = i
                st.rerun()
        st.markdown('<div style="border-bottom:1px solid rgba(28,28,30,0.10);margin:4px 0 4px 0;"></div>', unsafe_allow_html=True)


def _b64(path):
    import base64
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _render_detail(entry, idx):
    if st.button("← Back to Reports"):
        st.session_state.pop("viewing_report_idx", None)
        st.rerun()

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    cover = _cover_image_path()
    cols = st.columns([1, 1.6])
    with cols[0]:
        if cover:
            st.image(cover, use_container_width=True)
    with cols[1]:
        week = entry["generated_at"].isocalendar()[1]
        st.markdown(
            f"""
<div class="brief-eyebrow">AI &amp; Enterprise Intelligence</div>
<div class="brief-title">Weekly Executive Report</div>
<div class="brief-meta">Week {week} &middot; {entry['theme']} &middot; generated {entry['generated_at']:%d %b %Y, %H:%M}</div>
<div class="brief-stats">
    <div class="b-stat"><div class="v">{entry['selected']}</div><div class="l">Selected</div></div>
    <div class="b-stat"><div class="v">{entry['analyzed']}</div><div class="l">Analyzed</div></div>
    <div class="b-stat"><div class="v">{entry['images_resolved']}</div><div class="l">Images</div></div>
    <div class="b-stat"><div class="v">{entry['slides']}</div><div class="l">Slides</div></div>
</div>
""".strip(),
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
        ppt_path = entry.get("pptx_path")
        if ppt_path and Path(ppt_path).exists():
            with open(ppt_path, "rb") as f:
                st.download_button(
                    "Download PowerPoint",
                    data=f,
                    file_name="Weekly_GenAI_Report.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True,
                    key=f"detail_download_{idx}",
                )
        else:
            st.caption("The generated file for this run is no longer on disk.")

    st.markdown(
        '<div class="section-head"><div class="section-title">Presentation Preview</div>'
        '<div class="section-note">Slide-by-slide viewer</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-eyebrow">Not Yet Available</div>'
        '<div class="empty-title">A slide-by-slide viewer needs a PowerPoint renderer</div>'
        '<div class="empty-sub">The pipeline produces a real .pptx file, but this workspace '
        'does not yet render individual slides to images in-browser. Download the file above '
        'to view it in PowerPoint.</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render():
    st.markdown(
        '<div class="section-head"><div class="section-title">Reports</div>'
        '<div class="section-note">This session&rsquo;s generated briefs</div></div>',
        unsafe_allow_html=True,
    )

    history = st.session_state.get("report_history", [])
    viewing_idx = st.session_state.get("viewing_report_idx")

    if viewing_idx is not None and viewing_idx < len(history):
        _render_detail(history[viewing_idx], viewing_idx)
        return

    if not history:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-eyebrow">Library Empty</div>'
            '<div class="empty-title">No reports generated yet this session</div>'
            '<div class="empty-sub">Generate your first executive intelligence brief '
            'and it will appear here as a publishing-grade entry.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    _render_library(history)
