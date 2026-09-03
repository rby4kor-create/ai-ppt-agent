import streamlit as st


def dashboard():
    """
    Secondary metric row. Same rule as cards.py: real numbers from the
    last completed run, neutral placeholders otherwise - never a
    hardcoded fake value.
    """

    st.markdown('<div class="section-title">Dashboard</div>', unsafe_allow_html=True)

    last_run = st.session_state.get("last_run")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Articles Selected", str(last_run["selected"]) if last_run else "—")
    with c2:
        st.metric("Avg. Innovation", f"{last_run['avg_innovation']:.1f}" if last_run else "—")
    with c3:
        st.metric("Enterprise Ready %", f"{last_run['readiness_pct']:.0f}%" if last_run else "—")
