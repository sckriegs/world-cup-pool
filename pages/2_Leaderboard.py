import streamlit as st

from src.config import POOL_NAME
from src.database import get_database
from src.scoring import calculate_points, results_are_set

st.set_page_config(page_title=f"Leaderboard | {POOL_NAME}", page_icon="⚽", layout="wide")

db = get_database()
entries = db.list_entries()
results = db.get_results()
scored = results_are_set(results)
current_name = st.session_state.get("display_name", "")

st.title("Leaderboard")

if not entries:
    st.info("No entries yet. Be the first to submit picks!")
    st.stop()

if not scored:
    st.warning("Results haven't been entered yet. Standings will update once the admin enters official outcomes.")

rows = []
for rank, entry in enumerate(entries, start=1):
    breakdown = calculate_points(entry.picks, results) if scored else {}
    rows.append(
        {
            "Rank": rank,
            "Name": entry.display_name,
            "Total": breakdown.get("total", entry.total_points) if scored else "—",
            "Champion": breakdown.get("champion", 0) if scored else "—",
            "Runner-up": breakdown.get("runner_up", 0) if scored else "—",
            "Semis": breakdown.get("semi_finalists", 0) if scored else "—",
            "Groups": breakdown.get("group_winners", 0) if scored else "—",
            "Bonus": breakdown.get("bonuses", 0) if scored else "—",
        }
    )

st.dataframe(rows, use_container_width=True, hide_index=True)

if current_name:
    match = next((r for r in rows if r["Name"].lower() == current_name.lower()), None)
    if match:
        st.success(f"You are ranked **#{match['Rank']}** with **{match['Total']}** points.")

if scored and results.updated_at:
    st.caption(f"Last updated: {results.updated_at.strftime('%Y-%m-%d %H:%M UTC')}")
