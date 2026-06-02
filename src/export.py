import csv
import io

from src.config import BONUS_QUESTIONS, GROUPS
from src.models import Entry, Results
from src.scoring import calculate_points


def entries_to_csv(entries: list[Entry], results: Results) -> str:
    buffer = io.StringIO()
    bonus_keys = list(BONUS_QUESTIONS.keys())
    fieldnames = [
        "rank",
        "display_name",
        "total_points",
        "champion_pick",
        "runner_up_pick",
        "semi_1",
        "semi_2",
        "semi_3",
        "semi_4",
        *[f"group_{g}" for g in GROUPS],
        *[f"bonus_{k}" for k in bonus_keys],
        "points_champion",
        "points_runner_up",
        "points_semis",
        "points_groups",
        "points_bonus",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()

    ranked = sorted(entries, key=lambda e: (-e.total_points, e.created_at or e.updated_at))
    for rank, entry in enumerate(ranked, start=1):
        breakdown = calculate_points(entry.picks, results)
        semis = entry.picks.semi_finalists + [""] * (4 - len(entry.picks.semi_finalists))
        row = {
            "rank": rank,
            "display_name": entry.display_name,
            "total_points": breakdown["total"],
            "champion_pick": entry.picks.champion,
            "runner_up_pick": entry.picks.runner_up,
            "semi_1": semis[0],
            "semi_2": semis[1],
            "semi_3": semis[2],
            "semi_4": semis[3],
            "points_champion": breakdown["champion"],
            "points_runner_up": breakdown["runner_up"],
            "points_semis": breakdown["semi_finalists"],
            "points_groups": breakdown["group_winners"],
            "points_bonus": breakdown["bonuses"],
        }
        for g in GROUPS:
            row[f"group_{g}"] = entry.picks.group_winners.get(g, "")
        for k in bonus_keys:
            row[f"bonus_{k}"] = entry.picks.bonuses.get(k, "")
        writer.writerow(row)

    return buffer.getvalue()
