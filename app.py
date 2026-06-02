from datetime import datetime, timezone

import streamlit as st

from src.config import POOL_NAME, PICK_DEADLINE, SCORING, BONUS_QUESTIONS
from src.database import get_database
from src.validation import normalize_name, validate_name

st.set_page_config(page_title=POOL_NAME, page_icon="⚽", layout="wide")

if "display_name" not in st.session_state:
    st.session_state.display_name = ""


def deadline_message() -> str:
    now = datetime.now(timezone.utc)
    if now >= PICK_DEADLINE:
        return "Picks are locked — the tournament has started."
    remaining = PICK_DEADLINE - now
    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes = remainder // 60
    return f"Picks close in **{days}d {hours}h {minutes}m** (first kickoff: June 11, 2026)."


st.title(f"⚽ {POOL_NAME}")
st.caption(deadline_message())

st.markdown(
    """
Welcome to the office pool! Enter your name below, then head to **Make Picks** to submit
your predictions before the deadline.
"""
)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Join the pool")
    name_input = st.text_input(
        "Your display name",
        value=st.session_state.display_name,
        placeholder="e.g. Alex",
        max_chars=50,
    )

    if st.button("Continue", type="primary"):
        error = validate_name(name_input)
        if error:
            st.error(error)
        else:
            normalized = normalize_name(name_input)
            st.session_state.display_name = normalized
            db = get_database()
            entry = db.get_entry_by_name(normalized)
            if entry:
                st.success(f"Welcome back, {normalized}! Your existing picks are saved.")
            else:
                st.success(f"Welcome, {normalized}! Head to Make Picks to submit your entry.")
            st.rerun()

    if st.session_state.display_name:
        st.info(f"Signed in as **{st.session_state.display_name}**")

with col2:
    st.subheader("How scoring works")
    st.markdown(
        f"""
| Pick | Points |
|------|--------|
| Champion | {SCORING['champion']} |
| Runner-up | {SCORING['runner_up']} |
| Each semi-finalist | {SCORING['semi_finalist']} |
| Each group winner | {SCORING['group_winner']} |
| Each bonus question | {SCORING['bonus']} |
"""
    )

st.divider()
st.subheader("Bonus questions")
for key, label in BONUS_QUESTIONS.items():
    st.markdown(f"- **{label}**")

st.divider()
entry_count = len(get_database().list_entries())
st.metric("Entries submitted", entry_count)
