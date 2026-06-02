import streamlit as st

from src.branding import apply_branding, brand_header
from src.config import BONUS_QUESTIONS, DARK_HORSE_SEEDED_NOTE, GROUPS, POOL_NAME
from src.database import all_teams, dark_horse_teams, get_database, load_teams_data
from src.models import Picks
from src.validation import picks_are_locked, validate_picks

st.set_page_config(page_title=f"Make Picks | {POOL_NAME}", page_icon="⚽", layout="wide")
apply_branding()

if "display_name" not in st.session_state or not st.session_state.display_name:
    st.warning("Enter your name on the Home page first.")
    st.page_link("app.py", label="Go to Home", icon="🏠")
    st.stop()

display_name = st.session_state.display_name
db = get_database()
teams = all_teams()
teams_data = load_teams_data()
existing = db.get_entry_by_name(display_name)
current = existing.picks if existing else Picks()

brand_header("Make Your Picks", f"Entry for {display_name}")

if picks_are_locked():
    st.error("Picks are locked. You can view your submitted picks below but cannot change them.")
    read_only = True
else:
    read_only = False
    if existing:
        st.info("You can update your picks anytime before the deadline.")

st.subheader("Knockout predictions")

col1, col2 = st.columns(2)
with col1:
    champion = st.selectbox(
        "Champion",
        [""] + teams,
        index=([""] + teams).index(current.champion) if current.champion in teams else 0,
        disabled=read_only,
    )
with col2:
    runner_up = st.selectbox(
        "Runner-up",
        [""] + teams,
        index=([""] + teams).index(current.runner_up) if current.runner_up in teams else 0,
        disabled=read_only,
    )

st.markdown("**Semi-finalists** (pick 4 distinct teams)")
semi_cols = st.columns(2)
semi_picks: list[str] = []
for i in range(4):
    default = current.semi_finalists[i] if i < len(current.semi_finalists) else ""
    with semi_cols[i % 2]:
        pick = st.selectbox(
            f"Semi-finalist {i + 1}",
            [""] + teams,
            index=([""] + teams).index(default) if default in teams else 0,
            key=f"semi_{i}",
            disabled=read_only,
        )
        semi_picks.append(pick)

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
            key=f"group_{group}",
            disabled=read_only,
        )
        group_winners[group] = winner

st.subheader("Bonus questions")
bonus_picks: dict[str, str] = {}
for key, label in BONUS_QUESTIONS.items():
    default = current.bonuses.get(key, "")
    if key == "dark_horse":
        options = dark_horse_teams()
        st.caption(DARK_HORSE_SEEDED_NOTE)
    else:
        options = teams
    bonus_picks[key] = st.selectbox(
        label,
        [""] + options,
        index=([""] + options).index(default) if default in options else 0,
        key=f"bonus_{key}",
        disabled=read_only,
    )

if not read_only:
    if st.button("Save picks", type="primary"):
        errors = validate_picks(champion, runner_up, semi_picks, group_winners, bonus_picks)
        if errors:
            for err in errors:
                st.error(err)
        else:
            picks = Picks(
                champion=champion,
                runner_up=runner_up,
                semi_finalists=semi_picks,
                group_winners=group_winners,
                bonuses=bonus_picks,
            )
            db.save_entry(display_name, picks)
            st.success("Picks saved!")
            st.balloons()
