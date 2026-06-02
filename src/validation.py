from datetime import datetime, timezone

from src.config import BONUS_QUESTIONS, GROUPS, PICK_DEADLINE, SEEDED_TEAMS


def picks_are_locked() -> bool:
    return datetime.now(timezone.utc) >= PICK_DEADLINE


def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())


def validate_name(name: str) -> str | None:
    normalized = normalize_name(name)
    if not normalized:
        return "Please enter your name."
    if len(normalized) < 2:
        return "Name must be at least 2 characters."
    if len(normalized) > 50:
        return "Name must be 50 characters or fewer."
    return None


def validate_picks(
    champion: str,
    runner_up: str,
    semi_finalists: list[str],
    group_winners: dict[str, str],
    bonuses: dict[str, str],
) -> list[str]:
    errors: list[str] = []

    if not champion:
        errors.append("Select a champion.")
    if not runner_up:
        errors.append("Select a runner-up.")

    semi_set = [s for s in semi_finalists if s]
    if len(semi_set) < 4:
        errors.append("Select all 4 semi-finalists.")
    if len(set(semi_set)) < len(semi_set):
        errors.append("Semi-finalist picks must be distinct teams.")

    all_knockout = [champion, runner_up, *semi_set]
    if len(set(all_knockout)) != len(all_knockout):
        errors.append("Champion, runner-up, and semi-finalists must all be different teams.")

    for group in GROUPS:
        if not group_winners.get(group):
            errors.append(f"Select a winner for Group {group}.")

    for key in BONUS_QUESTIONS:
        if not bonuses.get(key):
            errors.append(f"Answer the bonus question: {BONUS_QUESTIONS[key]}.")

    dark_horse = bonuses.get("dark_horse", "")
    if dark_horse and dark_horse in SEEDED_TEAMS:
        errors.append("Dark horse must be a non-seeded team.")

    return errors
