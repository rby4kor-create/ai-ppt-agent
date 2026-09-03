import streamlit as st


def hero():
    html = """
<div class="hero-shell">
<div class="eyebrow">Enterprise AI Intelligence</div>
<div class="hero-title">Weekly GenAI Report, on autopilot</div>
<div class="hero-sub">Collects the week's AI news, ranks it, writes the analysis, and builds a
board-ready PowerPoint -- you just pick the topics.</div>
<div class="hero-pills">
<span class="hero-pill">🛰️ 17 sources tracked</span>
<span class="hero-pill">🧠 LLM-written analysis</span>
<span class="hero-pill">🖼️ Curated visual library</span>
<span class="hero-pill">📝 Feedback &amp; activity log built in</span>
</div>
</div>
""".strip()
    st.markdown(html, unsafe_allow_html=True)
