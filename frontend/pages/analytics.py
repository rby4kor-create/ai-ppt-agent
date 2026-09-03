"""
Analytics -- executive-level views built strictly from real session
data: the candidate pool's category distribution, source activity,
and the report_history accumulated by Generate this session. No
random/rainbow charts -- each one answers a specific executive
question, and any section without enough data yet renders an honest
empty state instead of a fabricated chart.
"""
from collections import Counter

import matplotlib.pyplot as plt
import streamlit as st

from config import RSS_FEEDS

GRAPHITE = "#1C1C1E"
SLATE = "#63636A"
BOSCH_RED = "#E2001A"
HAIRLINE = "#E5E3DE"


def _style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(HAIRLINE)
    ax.tick_params(colors=SLATE, labelsize=9)
    ax.grid(False)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily("sans-serif")


def _signal_momentum(candidates):
    st.markdown(
        '<div class="section-head"><div class="section-title">AI Signal Momentum</div>'
        '<div class="section-note">Article volume by category, current candidate pool</div></div>',
        unsafe_allow_html=True,
    )
    if not candidates:
        st.caption("Run Find Topics on Generate to populate this view.")
        return

    counts = Counter(a.category or "Uncategorized" for a in candidates)
    ranked = counts.most_common(10)
    labels = [c for c, _ in ranked][::-1]
    values = [v for _, v in ranked][::-1]

    fig, ax = plt.subplots(figsize=(8, max(2.2, 0.4 * len(labels))))
    bars = ax.barh(labels, values, color=GRAPHITE, height=0.55)
    if bars:
        bars[-1].set_color(BOSCH_RED)
    _style_ax(ax)
    ax.set_xlabel("")
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    st.pyplot(fig, use_container_width=True)


def _source_activity(candidates):
    st.markdown(
        '<div class="section-head"><div class="section-title">Source Activity</div>'
        '<div class="section-note">Articles surfaced per tracked source</div></div>',
        unsafe_allow_html=True,
    )
    if not candidates:
        st.caption("Run Find Topics on Generate to populate this view.")
        return

    counts = Counter(a.source for a in candidates)
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])[:12]
    labels = [c for c, _ in ranked][::-1]
    values = [v for _, v in ranked][::-1]

    fig, ax = plt.subplots(figsize=(8, max(2.2, 0.32 * len(labels))))
    ax.barh(labels, values, color=GRAPHITE, height=0.55)
    _style_ax(ax)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    st.pyplot(fig, use_container_width=True)


def _report_production(history):
    st.markdown(
        '<div class="section-head"><div class="section-title">Report Production</div>'
        '<div class="section-note">Slides generated per run, this session</div></div>',
        unsafe_allow_html=True,
    )
    if not history:
        st.caption("No reports generated yet this session.")
        return

    runs = list(reversed(history))
    labels = [f"Run {i+1}" for i in range(len(runs))]
    slides = [r["slides"] for r in runs]

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(labels, slides, color=BOSCH_RED, marker="o", linewidth=2, markersize=5)
    ax.fill_between(labels, slides, color=BOSCH_RED, alpha=0.06)
    _style_ax(ax)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    st.pyplot(fig, use_container_width=True)


def _enterprise_relevance(history):
    st.markdown(
        '<div class="section-head"><div class="section-title">Enterprise Relevance</div>'
        '<div class="section-note">Readiness and innovation, most recent run</div></div>',
        unsafe_allow_html=True,
    )
    if not history:
        st.caption("No reports generated yet this session.")
        return

    latest = history[0]
    html = f"""
<div class="metric-strip">
    <div class="metric-cell"><div class="m-label">Enterprise Ready</div><div class="m-value">{latest['readiness_pct']:.0f}%</div></div>
    <div class="metric-cell"><div class="m-label">Avg. Innovation</div><div class="m-value">{latest['avg_innovation']:.1f}</div></div>
    <div class="metric-cell"><div class="m-label">Images Resolved</div><div class="m-value">{latest['images_resolved']}</div></div>
    <div class="metric-cell"><div class="m-label">LLM-Written</div><div class="m-value">{latest['diagnostics']['llm']}</div></div>
</div>
""".strip()
    st.markdown(html, unsafe_allow_html=True)


def render():
    candidates = st.session_state.get("candidates")
    history = st.session_state.get("report_history", [])

    st.markdown(
        '<div class="kicker">Executive Analytics</div>'
        '<div style="font-family:Manrope,sans-serif;font-size:22px;font-weight:800;">'
        'What the data says this week</div>',
        unsafe_allow_html=True,
    )

    _enterprise_relevance(history)
    _signal_momentum(candidates)
    _source_activity(candidates)
    _report_production(history)

    st.markdown(
        f'<div style="margin-top:32px;font-size:11.5px;color:{SLATE};">'
        f'{len(RSS_FEEDS)} sources configured in this workspace.</div>',
        unsafe_allow_html=True,
    )
