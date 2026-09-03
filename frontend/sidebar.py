import streamlit as st
from pathlib import Path

# "Dashboard", "Generate Report", "Visual Library", and "Activity Log"
# route to real pages in home.py. The rest stay as clearly-labeled
# placeholders (same behavior as before) so the nav doesn't lie about
# what's implemented.
NAV_PAGES = [
    "🏠 Dashboard",
    "⚙️ Generate Report",
    "🖼️ Visual Library",
    "📜 Activity Log",
    "📊 Analytics",
    "📁 Reports",
    "🔧 Settings",
]

# Map the decorated label back to the plain page name the rest of the
# app already keys off of, so home.py's routing logic doesn't need to
# know about emoji.
_LABEL_TO_PAGE = {
    "🏠 Dashboard": "Dashboard",
    "⚙️ Generate Report": "Generate Report",
    "🖼️ Visual Library": "Visual Library",
    "📜 Activity Log": "Activity Log",
    "📊 Analytics": "Analytics",
    "📁 Reports": "Reports",
    "🔧 Settings": "Settings",
}


def sidebar():
    with st.sidebar:
        logo = Path("assets/Bosch-Logo.png")
        if logo.exists():
            st.image(str(logo), width=140)

        st.markdown(
            "<div style='font-family:Sora,sans-serif;font-weight:800;"
            "font-size:20px;margin-top:6px;'>Top&nbsp;Gen&nbsp;AI</div>",
            unsafe_allow_html=True,
        )
        st.caption("Enterprise GenAI Intelligence Platform")
        st.divider()

        label = st.radio("Navigation", NAV_PAGES, key="nav_label", label_visibility="collapsed")
        selection = _LABEL_TO_PAGE[label]
        st.session_state["nav_page"] = selection

        st.divider()
        st.caption("Every action here is written to the Activity Log, and feedback goes straight to the team via the 💬 button.")

    return selection
