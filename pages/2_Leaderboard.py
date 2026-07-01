from datetime import timedelta

import streamlit as st

from src.access import require_pool_access
from src.branding import apply_branding, brand_header
from src.config import LEADERBOARD_REFRESH_SECONDS, POOL_NAME
from src.database import get_database
from src.scoring import calculate_points, has_scoring_data, results_are_set

st.set_page_config(page_title=f"Leaderboard | {POOL_NAME}", page_icon="⚽", layout="wide")
apply_branding()
require_pool_access()


def render_leaderboard() -> None:
    db = get_database()
    entries = db.list_entries()
    results = db.get_results()
    has_results = has_scoring_data(results)
    tournament_complete = results_are_set(results)
    current_name = st.session_state.get("display_name", "")

    if not entries:
        st.info("No entries yet. Be the first to submit picks!")
        return

    if not has_results:
        st.warning(
            "No results yet. Points appear after the admin syncs or enters outcomes."
        )
    elif not tournament_complete:
        st.info(
            "Live scoring — points update as groups finish and knockouts are decided. "
            "Champion and runner-up points award after the final."
        )

    ranked = sorted(
        [(entry, calculate_points(entry.picks, results)) for entry in entries],
        key=lambda row: (-row[1]["total"], row[0].created_at or row[0].updated_at),
    )

    rows = []
    for rank, (entry, breakdown) in enumerate(ranked, start=1):
        rows.append(
            {
                "Rank": rank,
                "Name": entry.display_name,
                "Total": breakdown["total"] if has_results else "—",
                "Champion": breakdown["champion"] if has_results else "—",
                "Runner-up": breakdown["runner_up"] if has_results else "—",
                "Semis": breakdown["semi_finalists"] if has_results else "—",
                "Groups": breakdown["group_winners"] if has_results else "—",
                "Bonus": breakdown["bonuses"] if has_results else "—",
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
