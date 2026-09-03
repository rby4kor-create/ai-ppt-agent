import streamlit as st

from frontend.home import home_page

st.set_page_config(
    page_title="Bosch AI Intelligence Workspace",
    page_icon="assets/Bosch-Logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

home_page()
