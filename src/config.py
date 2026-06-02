from datetime import datetime, timezone
from pathlib import Path

POOL_NAME = "World Cup 2026 Office Pool"

# First kickoff: Mexico vs South Africa, June 11, 2026 at 15:00 UTC (Estadio Azteca)
PICK_DEADLINE = datetime(2026, 6, 11, 15, 0, 0, tzinfo=timezone.utc)

SCORING = {
    "champion": 25,
    "runner_up": 15,
    "semi_finalist": 10,
    "group_winner": 3,
    "bonus": 5,
}

BONUS_QUESTIONS = {
    "golden_boot_country": "Golden Boot winner's country",
    "highest_scoring_team": "Highest-scoring team in the tournament",
    "dark_horse": "Dark horse (non-seed to reach quarter-finals)",
}

# FIFA pot-1 style seeds for the dark horse bonus (excluded from that pick only)
SEEDED_TEAMS = frozenset(
    {
        "Spain",
        "Argentina",
        "France",
        "England",
        "Brazil",
        "Portugal",
        "Netherlands",
        "Belgium",
        "Germany",
    }
)

DARK_HORSE_SEEDED_NOTE = (
    "Seeded teams (not eligible): Spain, Argentina, France, England, Brazil, "
    "Portugal, Netherlands, Belgium, and Germany."
)

GROUPS = list("ABCDEFGHIJKL")

# football-data.org — free tier: https://www.football-data.org/client/register
FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"
FOOTBALL_DATA_COMPETITION = "WC"  # FIFA World Cup
GROUP_STAGE_MATCHES = 3

# Leaderboard auto-refresh interval (seconds); set 0 to disable
LEADERBOARD_REFRESH_SECONDS = 60

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TEAMS_FILE = DATA_DIR / "teams_2026.json"
SQLITE_PATH = DATA_DIR / "pool.sqlite"
