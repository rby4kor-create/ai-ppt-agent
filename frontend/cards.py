import streamlit as st

from config import RSS_FEEDS


def dashboard_cards():
    """
    Renders the four top-of-page metric cards from real state:
    - Before a report has been generated, shows configured source
      count and neutral placeholders (never fake numbers like a
      hardcoded "25 Articles").
    - After generation, reads actual pipeline stats from
      st.session_state["last_run"] (set by frontend/home.py once
      run_pipeline() returns).
    """

    last_run = st.session_state.get("last_run")

    if last_run:
        cards = [
            ("🛰️", "Sources", str(len(last_run["sources"])), "RSS Providers Used"),
            ("📰", "Articles", str(last_run["selected"]), "Selected This Run"),
            ("🖼️", "Images", str(last_run["images_resolved"]), "Resolved"),
            ("✅", "Status", "COMPLETE", "Last Run Succeeded"),
        ]
    else:
        cards = [
            ("🛰️", "Sources", str(len(RSS_FEEDS)), "RSS Providers Configured"),
            ("📰", "Articles", "—", "Run a report to see this"),
            ("🖼️", "Images", "—", "Run a report to see this"),
            ("🟣", "Status", "READY", "Awaiting Generation"),
        ]

    cols = st.columns(4)
    for col, (icon, title, value, subtitle) in zip(cols, cards):
        with col:
            html = f"""
<div class="metric-card">
<div class="metric-label">{icon}&nbsp; {title}</div>
<div class="metric-value">{value}</div>
<div class="metric-sub">{subtitle}</div>
</div>
""".strip()
            st.markdown(html, unsafe_allow_html=True)
