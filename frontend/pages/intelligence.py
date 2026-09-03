"""
Intelligence -- a read-only deep dive into the current candidate pool
(st.session_state["candidates"], populated by "Find Topics" on the
Generate page). Editorial browsing by category, real article titles,
sources and scores. Selection itself still happens on Generate; this
page is for understanding the landscape before deciding.
"""
from collections import defaultdict

import streamlit as st


def _empty_state():
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-eyebrow">No Candidates Collected</div>'
        '<div class="empty-title">Fetch this week&rsquo;s intelligence to browse it here</div>'
        '<div class="empty-sub">Head to Generate and run &ldquo;Find Topics&rdquo; to pull '
        'real candidate articles from your tracked sources.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    if st.button("Go to Generate", use_container_width=False):
        st.session_state["nav_page"] = "Generate"
        st.rerun()


def render():
    st.markdown(
        '<div class="section-head"><div class="section-title">Intelligence</div>'
        '<div class="section-note">Candidate landscape, ranked by relevance</div></div>',
        unsafe_allow_html=True,
    )

    candidates = st.session_state.get("candidates")
    if not candidates:
        _empty_state()
        return

    meta = st.session_state.get("candidate_meta", {})
    selected_links = st.session_state.get("selected_links", set())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Collected", meta.get("collected", len(candidates)))
    m2.metric("After De-dup", meta.get("after_dedup", len(candidates)))
    m3.metric("Candidates Shown", len(candidates))
    m4.metric("Selected For Brief", len(selected_links))

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    by_category = defaultdict(list)
    for article in candidates:
        by_category[article.category or "Uncategorized"].append(article)

    for category, articles in sorted(by_category.items(), key=lambda kv: -len(kv[1])):
        st.markdown(
            f'<div style="font-family:Manrope,sans-serif;font-weight:800;font-size:14px;'
            f'text-transform:uppercase;letter-spacing:0.6px;margin:22px 0 8px 0;">'
            f'{category} <span style="color:#63636A;font-weight:600;text-transform:none;'
            f'letter-spacing:normal;">&middot; {len(articles)} article(s)</span></div>',
            unsafe_allow_html=True,
        )
        rows = []
        for article in articles:
            mark = "Selected" if article.link in selected_links else ""
            rows.append(
                f'<div class="signal-row">'
                f'<div class="signal-name">{article.title}</div>'
                f'<div class="signal-meta">{article.source} &middot; {article.published:%d %b}</div>'
                f'<div class="trend-pill {"trend-up" if mark else "trend-flat"}">{mark or "In pool"}</div>'
                f'</div>'
            )
        st.markdown("".join(rows), unsafe_allow_html=True)
