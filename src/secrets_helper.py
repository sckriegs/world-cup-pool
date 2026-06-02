import os

import streamlit as st


def get_secret(key: str, default: str | None = None) -> str | None:
    value = os.environ.get(key)
    if hasattr(st, "secrets"):
        try:
            value = value or st.secrets.get(key)
        except Exception:
            pass
    return value if value is not None else default
