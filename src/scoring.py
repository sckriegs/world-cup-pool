from src.config import SCORING
from src.models import Picks, Results


def calculate_points(picks: Picks, results: Results) -> dict[str, int]:
    """Return point breakdown and total for a single entry."""
    breakdown: dict[str, int] = {
        "champion": 0,
        "runner_up": 0,
        "semi_finalists": 0,
        "group_winners": 0,
        "bonuses": 0,
    }

    if results.champion and picks.champion == results.champion:
        breakdown["champion"] = SCORING["champion"]

    if results.runner_up and picks.runner_up == results.runner_up:
        breakdown["runner_up"] = SCORING["runner_up"]

    result_semis = {s for s in results.semi_finalists if s}
    for semi in picks.semi_finalists:
        if semi and semi in result_semis:
            breakdown["semi_finalists"] += SCORING["semi_finalist"]

    for group, winner in results.group_winners.items():
        if winner and picks.group_winners.get(group) == winner:
            breakdown["group_winners"] += SCORING["group_winner"]

    for key, answer in results.bonuses.items():
        if answer and picks.bonuses.get(key) == answer:
            breakdown["bonuses"] += SCORING["bonus"]

    breakdown["total"] = sum(
        breakdown[k] for k in ("champion", "runner_up", "semi_finalists", "group_winners", "bonuses")
    )
    return breakdown


def results_are_set(results: Results) -> bool:
    """True if admin has entered at least champion and runner-up."""
    return bool(results.champion and results.runner_up)
