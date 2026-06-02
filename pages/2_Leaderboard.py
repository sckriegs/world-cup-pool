from datetime import timedelta

import streamlit as st

from src.access import require_pool_access
from src.branding import apply_branding, brand_header
from src.config import LEADERBOARD_REFRESH_SECONDS, POOL_NAME
from src.database import get_database
from src.scoring import calculate_points, results_are_set

st.set_page_config(page_title=f"Leaderboard | {POOL_NAME}", page_icon="⚽", layout="wide")
apply_branding()
require_pool_access()


def render_leaderboard() -> None:
    db = get_database()
    entries = db.list_entries()
    results = db.get_results()
    scored = results_are_set(results)
    current_name = st.session_state.get("display_name", "")

    if not entries:
        st.info("No entries yet. Be the first to submit picks!")
        return

    if not scored:
        st.warning(
            "Results haven't been entered yet. Standings update when the admin saves or syncs results."
        )

    rows = []
    for rank, entry in enumerate(
        sorted(entries, key=lambda e: (-e.total_points, e.created_at or e.updated_at)),
        start=1,
    ):
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

    if results.updated_at:
        st.caption(f"Results last updated: {results.updated_at.strftime('%Y-%m-%d %H:%M UTC')}")


brand_header("Leaderboard")

auto_refresh = st.toggle(
    "Auto-refresh live",
    value=True,
    help="Refreshes standings every minute when results are syncing during the tournament.",
)

if auto_refresh and LEADERBOARD_REFRESH_SECONDS > 0:

    @st.fragment(run_every=timedelta(seconds=LEADERBOARD_REFRESH_SECONDS))
    def _live_board() -> None:
        render_leaderboard()
        st.caption(f"Auto-refreshing every {LEADERBOARD_REFRESH_SECONDS} seconds.")

    _live_board()
else:
    render_leaderboard()
