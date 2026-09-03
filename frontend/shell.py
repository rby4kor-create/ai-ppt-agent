"""
Application shell for the Bosch AI Intelligence Workspace: the left
navigation rail and the top contextual header bar. Replaces
frontend/sidebar.py's emoji st.radio nav entirely.

Navigation state lives in st.session_state["nav_page"] so the rest of
the app (home.py's router) doesn't change shape -- only what draws the
chrome around it changes.
"""
from datetime import datetime
from pathlib import Path

import streamlit as st

NAV_ITEMS = [
    ("01", "Overview", "Overview"),
    ("02", "Intelligence", "Intelligence"),
    ("03", "Generate", "Generate"),
    ("04", "Visuals", "Visuals"),
    ("05", "Reports", "Reports"),
    ("06", "Analytics", "Analytics"),
    ("07", "Activity", "Activity Log"),
]

SETTINGS_ITEM = ("Settings", "Settings")


def _nav_button(number, label, page_key, current):
    is_active = current == page_key
    key = f"nav_{'active_' if is_active else ''}{page_key.lower().replace(' ', '_')}"
    with st.container(key=key):
        clicked = st.button(f"{number}   {label}", key=f"navbtn_{page_key}", use_container_width=True)
    if clicked:
        st.session_state["nav_page"] = page_key
        st.rerun()


def sidebar_nav():
    """Renders the left rail and returns the active page key."""
    current = st.session_state.get("nav_page", "Overview")

    with st.sidebar:
        logo = Path("assets/Bosch-Logo.png")
        st.markdown('<div class="nav-brand">', unsafe_allow_html=True)
        if logo.exists():
            st.image(str(logo), width=104)
        st.markdown(
            '<div class="nav-brand-name">AI INTELLIGENCE</div>'
            '<div class="nav-brand-sub">Enterprise Workspace</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

        for number, label, page_key in NAV_ITEMS:
            _nav_button(number, label, page_key, current)

        st.markdown(
            '<div style="height:1px;background:rgba(255,255,255,0.08);margin:16px 22px;"></div>',
            unsafe_allow_html=True,
        )
        _nav_button("", "System Settings", SETTINGS_ITEM[1], current)

        st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="padding:0 22px;font-size:10.5px;color:rgba(255,255,255,0.32);'
            'line-height:1.5;">Every action is written to the Activity Log. '
            'Feedback goes to the team via the widget in the corner and by email.</div>',
            unsafe_allow_html=True,
        )

    return current


def top_header(sources_count, week_label):
    """Premium contextual header bar -- not a conventional navbar."""
    now = datetime.now()
    html = f"""
<div class="workspace-header">
    <div>
        <div class="workspace-title">BOSCH AI INTELLIGENCE</div>
        <div class="workspace-subtitle">Enterprise Intelligence Workspace</div>
    </div>
    <div class="workspace-meta">
        <div class="workspace-meta-item">
            <div class="meta-label">Current Week</div>
            <div class="meta-value">{week_label}</div>
        </div>
        <div class="workspace-meta-item">
            <div class="meta-label">Sources Tracked</div>
            <div class="meta-value">{sources_count}</div>
        </div>
        <div class="workspace-meta-item">
            <div class="meta-label">System Status</div>
            <div class="meta-value"><span class="status-dot"></span>Ready</div>
        </div>
    </div>
</div>
""".strip()
    st.markdown(html, unsafe_allow_html=True)


def footer():
    st.markdown(
        '<div class="workspace-footer">'
        '<span>Bosch AI Intelligence Workspace &middot; Enterprise Edition</span>'
        '<span>Created by RB Yogeshwar</span>'
        '</div>',
        unsafe_allow_html=True,
    )
