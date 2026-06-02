import os

import streamlit as st

from src.branding import apply_branding, brand_header
from src.config import BONUS_QUESTIONS, DARK_HORSE_SEEDED_NOTE, GROUPS, POOL_NAME
from src.database import all_teams, dark_horse_teams, get_database, load_teams_data
from src.models import Results
from src.scoring import results_are_set

st.set_page_config(page_title=f"Admin | {POOL_NAME}", page_icon="🔒", layout="wide")
apply_branding()

admin_password = os.environ.get("ADMIN_PASSWORD")
if hasattr(st, "secrets"):
    admin_password = admin_password or st.secrets.get("ADMIN_PASSWORD")

if not admin_password:
    st.error("Admin password not configured. Set ADMIN_PASSWORD in environment or Streamlit secrets.")
    st.stop()

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    brand_header("Admin Login", "Enter your admin password to enter results.")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        if password == admin_password:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

db = get_database()
teams = all_teams()
teams_data = load_teams_data()
current = db.get_results()

brand_header("Admin — Enter Results", "Save official outcomes to recalculate all entry scores.")

if results_are_set(current):
    st.success(f"Results last saved: {current.updated_at.strftime('%Y-%m-%d %H:%M UTC') if current.updated_at else 'unknown'}")

st.subheader("Knockout results")
col1, col2 = st.columns(2)
with col1:
    champion = st.selectbox(
        "Champion",
        [""] + teams,
        index=([""] + teams).index(current.champion) if current.champion in teams else 0,
    )
with col2:
    runner_up = st.selectbox(
        "Runner-up",
        [""] + teams,
        index=([""] + teams).index(current.runner_up) if current.runner_up in teams else 0,
    )

st.markdown("**Semi-finalists**")
semi_cols = st.columns(2)
semi_results: list[str] = []
for i in range(4):
    default = current.semi_finalists[i] if i < len(current.semi_finalists) else ""
    with semi_cols[i % 2]:
        pick = st.selectbox(
            f"Semi-finalist {i + 1}",
            [""] + teams,
            index=([""] + teams).index(default) if default in teams else 0,
            key=f"admin_semi_{i}",
        )
        semi_results.append(pick)

st.subheader("Group winners")
group_cols = st.columns(4)
group_winners: dict[str, str] = {}
for i, group in enumerate(GROUPS):
    group_teams = teams_data["groups"][group]
    default = current.group_winners.get(group, "")
    with group_cols[i % 4]:
        winner = st.selectbox(
            f"Group {group}",
            [""] + group_teams,
            index=([""] + group_teams).index(default) if default in group_teams else 0,
            key=f"admin_group_{group}",
        )
        group_winners[group] = winner

st.subheader("Bonus answers")
bonus_results: dict[str, str] = {}
for key, label in BONUS_QUESTIONS.items():
    default = current.bonuses.get(key, "")
    if key == "dark_horse":
        options = dark_horse_teams()
        st.caption(DARK_HORSE_SEEDED_NOTE)
    else:
        options = teams
    bonus_results[key] = st.selectbox(
        label,
        [""] + options,
        index=([""] + options).index(default) if default in options else 0,
        key=f"admin_bonus_{key}",
    )

if st.button("Save results & recalculate scores", type="primary"):
    results = Results(
        champion=champion,
        runner_up=runner_up,
        semi_finalists=semi_results,
        group_winners=group_winners,
        bonuses=bonus_results,
    )
    db.save_results(results)
    st.success("Results saved and all scores recalculated!")
    st.rerun()

st.divider()
st.subheader("All entries")
entries = db.list_entries()
if entries:
    for entry in entries:
        with st.expander(f"{entry.display_name} — {entry.total_points} pts"):
            st.json(entry.picks.to_dict())
else:
    st.info("No entries yet.")

if st.button("Log out"):
    st.session_state.admin_authenticated = False
    st.rerun()
