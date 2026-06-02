import json

from src.config import DATA_DIR, TEAMS_FILE
from src.database import all_teams


def _load_aliases() -> dict[str, list[str]]:
    path = DATA_DIR / "team_name_aliases.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _canonical_by_lower() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for team in all_teams():
        mapping[team.lower()] = team
    for canonical, aliases in _load_aliases().items():
        mapping[canonical.lower()] = canonical
        for alias in aliases:
            mapping[alias.lower()] = canonical
    return mapping


def resolve_team_name(api_name: str) -> str | None:
    """Map an API / broadcast team name to our pool team name."""
    if not api_name:
        return None
    lookup = _canonical_by_lower()
    cleaned = api_name.strip()
    if cleaned.lower() in lookup:
        return lookup[cleaned.lower()]
    # Try without common suffixes
    for suffix in (" FC", " National Team"):
        if cleaned.endswith(suffix):
            short = cleaned[: -len(suffix)].strip()
            if short.lower() in lookup:
                return lookup[short.lower()]
    return None
