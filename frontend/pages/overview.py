"""
Overview -- "THIS WEEK IN AI". The editorial front page of the
workspace: hero narrative, the generated brief as a visual centerpiece,
intelligence signals (category momentum), source intelligence, and an
AI synthesis block. Every number here is read from real state
(st.session_state["last_run"], config.RSS_FEEDS, config.SOURCE_TIER) --
before a report has been generated, sections render honest empty
states instead of fabricated figures.
"""
from pathlib import Path
from collections import Counter

import streamlit as st

from config import RSS_FEEDS, SOURCE_TIER

COVER_CANDIDATES = ["assets/cover_ai.png", "assets/cover_hero.png"]


def _cover_image_path():
    for p in COVER_CANDIDATES:
        if Path(p).exists():
            return p
    return None


def _week_label():
    from datetime import date
    today = date.today()
    return f"Week {today.isocalendar()[1]} · {today.year}"


def _render_hero(last_run):
    if last_run:
        narrative = (
            f"{last_run['selected']} stories were analyzed this run, surfacing "
            f"{last_run['slides']} briefing slides across the categories that moved "
            "the enterprise AI landscape this week."
        )
    else:
        narrative = (
            "No brief has been generated yet this session. Run the collection and "
            "analysis pipeline from Generate to populate this workspace with real "
            "signal."
        )

    stats = [
        ("Sources Tracked", str(len(RSS_FEEDS))),
        ("Articles Analyzed", str(last_run["analyzed"]) if last_run else "—"),
        ("Briefing Slides", str(last_run["slides"]) if last_run else "—"),
    ]

    stat_html = "".join(
        f'<div class="hero-stat"><div class="stat-value">{v}</div>'
        f'<div class="stat-label">{l}</div></div>'
        for l, v in stats
    )

    html = f"""
<div class="hero-zone">
    <div class="hero-eyebrow">Executive Intelligence Briefing</div>
    <div class="hero-display">This week<br>in AI intelligence</div>
    <div class="hero-narrative">{narrative}</div>
    <div class="hero-stat-row">{stat_html}</div>
</div>
""".strip()
    st.markdown(html, unsafe_allow_html=True)

    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        if st.button("Explore Intelligence", use_container_width=True):
            st.session_state["nav_page"] = "Intelligence"
            st.rerun()
    with c2:
        if st.button("Generate Executive Brief", use_container_width=True, type="primary"):
            st.session_state["nav_page"] = "Generate"
            st.rerun()


def _render_featured_brief(last_run):
    st.markdown(
        '<div class="section-head"><div class="section-title">Featured Intelligence Brief</div>'
        '<div class="section-note">Most recent generation</div></div>',
        unsafe_allow_html=True,
    )

    if not last_run:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-eyebrow">Workspace Ready</div>'
            '<div class="empty-title">Your intelligence workspace is ready</div>'
            '<div class="empty-sub">Generate your first executive intelligence brief '
            'to see it showcased here as a presentation-grade artifact.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    cover = _cover_image_path()
    week = _week_label()

    cols = st.columns([1, 1.6])
    with cols[0]:
        if cover:
            st.image(cover, use_container_width=True)
        else:
            st.markdown(
                '<div style="background:#141416;height:220px;"></div>',
                unsafe_allow_html=True,
            )
    with cols[1]:
        st.markdown(
            f"""
<div class="brief-eyebrow">AI &amp; Enterprise Intelligence</div>
<div class="brief-title">Weekly Executive Report</div>
<div class="brief-meta">{week} &middot; {last_run['selected']} signals &middot; {len(last_run['sources'])} sources &middot; {last_run['images_resolved']} visuals</div>
<div class="brief-stats">
    <div class="b-stat"><div class="v">{last_run['analyzed']}</div><div class="l">Analyzed</div></div>
    <div class="b-stat"><div class="v">{last_run['slides']}</div><div class="l">Slides</div></div>
    <div class="b-stat"><div class="v">{last_run['avg_innovation']:.1f}</div><div class="l">Avg. Innovation</div></div>
    <div class="b-stat"><div class="v">{last_run['readiness_pct']:.0f}%</div><div class="l">Enterprise Ready</div></div>
</div>
""".strip(),
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Open Presentation →", use_container_width=True):
                st.session_state["nav_page"] = "Reports"
                st.rerun()
        with b2:
            ppt_path = last_run.get("pptx_path")
            if ppt_path and Path(ppt_path).exists():
                with open(ppt_path, "rb") as f:
                    st.download_button(
                        "Download PowerPoint →",
                        data=f,
                        file_name="Weekly_GenAI_Report.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True,
                    )


def _render_signals(last_run):
    st.markdown(
        '<div class="section-head"><div class="section-title">Intelligence Signals</div>'
        '<div class="section-note">Category momentum</div></div>',
        unsafe_allow_html=True,
    )

    candidates = st.session_state.get("candidates")
    if not candidates:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-eyebrow">No Signals Yet</div>'
            '<div class="empty-title">Fetch this week&rsquo;s candidates to surface signals</div>'
            '<div class="empty-sub">Run &ldquo;Find Topics&rdquo; from Generate to populate '
            'category-level momentum from real collected articles.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    counts = Counter(a.category or "Uncategorized" for a in candidates)
    ranked = counts.most_common()
    max_count = ranked[0][1] if ranked else 1

    rows = []
    for i, (category, count) in enumerate(ranked[:8], start=1):
        share = count / max_count
        if share >= 0.66:
            trend, cls = "↑ Emerging", "trend-up"
        elif share >= 0.33:
            trend, cls = "→ Stable", "trend-flat"
        else:
            trend, cls = "· Watch", "trend-watch"
        rows.append(
            f'<div class="signal-row">'
            f'<div class="signal-index">{str(i).zfill(2)}</div>'
            f'<div class="signal-name">{category}</div>'
            f'<div class="signal-meta">{count} article(s)</div>'
            f'<div class="trend-pill {cls}">{trend}</div>'
            f'</div>'
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def _render_sources():
    st.markdown(
        f'<div class="section-head"><div class="section-title">Source Intelligence</div>'
        f'<div class="section-note">{len(RSS_FEEDS)} sources tracked</div></div>',
        unsafe_allow_html=True,
    )

    candidates = st.session_state.get("candidates") or []
    counts = Counter(a.source for a in candidates)

    rows = []
    for name in sorted(RSS_FEEDS.keys(), key=lambda n: -counts.get(n, 0)):
        tier = "Tier 1 · Primary" if SOURCE_TIER.get(name) == 1 else "Tier 2 · Press"
        count = counts.get(name, 0)
        rows.append(
            f'<div class="source-row">'
            f'<div class="source-name">{name}</div>'
            f'<div class="source-tier">{tier}</div>'
            f'<div class="source-count">{count}</div>'
            f'</div>'
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def _render_synthesis(last_run):
    st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)

    if last_run:
        quote = (
            f"Analysis across {last_run['analyzed']} articles this run points to an "
            f"enterprise-readiness score of {last_run['readiness_pct']:.0f}%, with an "
            f"average innovation rating of {last_run['avg_innovation']:.1f} across "
            "the selected stories."
        )
        impact = (
            f"{last_run['images_resolved']} of {last_run['slides']} slides carry a "
            "resolved visual, and the deck is ready to download from Reports."
        )
        why = "This run reflects exactly the topics selected during the Generate workflow — nothing here is auto-picked without review."
        key_signal = f"{last_run['selected']} stories selected across {len(last_run['sources'])} tracked sources."
    else:
        quote = "Generate your first brief to populate this synthesis with real analysis from the current run."
        impact = "—"
        why = "—"
        key_signal = "—"

    html = f"""
<div class="synthesis-block">
    <div class="synthesis-label">AI Synthesis</div>
    <div class="synthesis-quote">&ldquo;{quote}&rdquo;</div>
    <div class="synthesis-grid">
        <div class="s-col"><div class="s-label">Key Signal</div><div class="s-value">{key_signal}</div></div>
        <div class="s-col"><div class="s-label">Why It Matters</div><div class="s-value">{why}</div></div>
        <div class="s-col"><div class="s-label">Enterprise Impact</div><div class="s-value">{impact}</div></div>
    </div>
</div>
""".strip()
    st.markdown(html, unsafe_allow_html=True)


def render():
    last_run = st.session_state.get("last_run")
    _render_hero(last_run)
    _render_featured_brief(last_run)
    _render_signals(last_run)
    _render_sources()
    _render_synthesis(last_run)
