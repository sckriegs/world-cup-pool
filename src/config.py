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

GROUPS = list("ABCDEFGHIJKL")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TEAMS_FILE = DATA_DIR / "teams_2026.json"
SQLITE_PATH = DATA_DIR / "pool.sqlite"
