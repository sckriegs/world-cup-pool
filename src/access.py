import streamlit as st

from src.secrets_helper import get_secret


def require_pool_access() -> None:
    """Gate participant pages when POOL_PASSCODE is configured."""
    if not get_secret("POOL_PASSCODE"):
        return
    if st.session_state.get("pool_unlocked"):
        return
    st.warning("Enter the pool passcode on the Home page first.")
    st.page_link("app.py", label="Go to Home", icon="🏠")
    st.stop()
