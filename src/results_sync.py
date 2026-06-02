"""Fetch tournament results from football-data.org and merge into pool Results."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from src.config import GROUPS, GROUP_STAGE_MATCHES, FOOTBALL_DATA_BASE_URL, FOOTBALL_DATA_COMPETITION
from src.models import Results
from src.secrets_helper import get_secret
from src.team_names import resolve_team_name


@dataclass
class SyncReport:
    messages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def ok(self) -> bool:
        return not self.errors


def _api_key() -> str | None:
    return get_secret("FOOTBALL_DATA_API_KEY")


def _fetch(path: str) -> dict:
    key = _api_key()
    if not key:
        raise ValueError(
            "FOOTBALL_DATA_API_KEY is not set. Add it to Streamlit secrets or your environment. "
            "Get a free key at https://www.football-data.org/client/register"
        )
    url = f"{FOOTBALL_DATA_BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        headers={"X-Auth-Token": key, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode() if exc.fp else ""
        raise ValueError(f"football-data.org returned {exc.code}: {body[:200]}") from exc


def _group_letter(group_field: str) -> str | None:
    # e.g. GROUP_A, GROUP_B
    if not group_field or not group_field.startswith("GROUP_"):
        return None
    letter = group_field.replace("GROUP_", "").strip()
    return letter if letter in GROUPS else None


def _parse_group_winners(standings_payload: dict, report: SyncReport) -> dict[str, str]:
    winners: dict[str, str] = {}
    for block in standings_payload.get("standings", []):
        group = _group_letter(block.get("group", ""))
        if not group:
            continue
        table = block.get("table", [])
        if not table:
            continue
        played = [row.get("playedGames", 0) for row in table]
        if not played or max(played) < GROUP_STAGE_MATCHES:
            report.messages.append(f"Group {group}: still in progress (waiting for all {GROUP_STAGE_MATCHES} games).")
            continue
        leader = next((row for row in table if row.get("position") == 1), table[0])
        team_info = leader.get("team", {})
        raw_name = team_info.get("name") or team_info.get("shortName") or ""
        resolved = resolve_team_name(raw_name)
        if resolved:
            winners[group] = resolved
            report.messages.append(f"Group {group} winner: {resolved}")
        else:
            report.errors.append(f"Could not map group {group} winner '{raw_name}' to a pool team.")
    return winners


def _team_from_match_side(side: dict) -> str | None:
    team = side.get("team") or {}
    return resolve_team_name(team.get("name") or team.get("shortName") or "")


def _parse_knockouts(matches_payload: dict, report: SyncReport) -> tuple[str, str, list[str]]:
    champion = ""
    runner_up = ""
    semi_teams: list[str] = []

    matches = matches_payload.get("matches", [])
    for match in matches:
        if match.get("status") != "FINISHED":
            continue
        stage = (match.get("stage") or "").upper()
        home = match.get("score", {}).get("fullTime", {}).get("home")
        away = match.get("score", {}).get("fullTime", {}).get("away")
        if home is None or away is None:
            continue

        home_team = _team_from_match_side(match.get("homeTeam", {}))
        away_team = _team_from_match_side(match.get("awayTeam", {}))

        if stage == "SEMI_FINALS" and home_team and away_team:
            for t in (home_team, away_team):
                if t not in semi_teams:
                    semi_teams.append(t)

        if stage == "FINAL" and home_team and away_team:
            if home > away:
                champion, runner_up = home_team, away_team
            else:
                champion, runner_up = away_team, home_team
            report.messages.append(f"Final: {champion} def. {runner_up}")

    if len(semi_teams) == 4:
        report.messages.append(f"Semi-finalists: {', '.join(semi_teams)}")
    elif semi_teams:
        report.messages.append(f"Semi-finalists (partial): {', '.join(semi_teams)}")

    return champion, runner_up, semi_teams[:4]


def _parse_top_scorer_bonuses(competition_path: str, report: SyncReport) -> dict[str, str]:
    bonuses: dict[str, str] = {}
    try:
        scorers = _fetch(f"{competition_path}/scorers").get("scorers", [])
    except ValueError:
        return bonuses

    if not scorers:
        return bonuses

    top = scorers[0]
    player = top.get("player", {})
    team_info = top.get("team", {})
    team_name = resolve_team_name(team_info.get("name") or team_info.get("shortName") or "")
    goals = top.get("goals", 0)
    if team_name:
        bonuses["golden_boot_country"] = team_name
        report.messages.append(f"Golden Boot leader ({goals} goals): {team_name}")

    return bonuses


def _parse_highest_scoring_team(matches_payload: dict, report: SyncReport) -> str | None:
    totals: dict[str, int] = {}
    for match in matches_payload.get("matches", []):
        if match.get("status") != "FINISHED":
            continue
        ft = match.get("score", {}).get("fullTime", {})
        home_goals, away_goals = ft.get("home"), ft.get("away")
        if home_goals is None or away_goals is None:
            continue
        home = _team_from_match_side(match.get("homeTeam", {}))
        away = _team_from_match_side(match.get("awayTeam", {}))
        if home:
            totals[home] = totals.get(home, 0) + home_goals
        if away:
            totals[away] = totals.get(away, 0) + away_goals

    if not totals:
        return None
    best_team = max(totals, key=totals.get)
    report.messages.append(f"Highest-scoring team so far: {best_team} ({totals[best_team]} goals)")
    return best_team


def fetch_results_from_api() -> tuple[Results, SyncReport]:
    report = SyncReport()
    comp_path = f"/competitions/{FOOTBALL_DATA_COMPETITION}"

    standings = _fetch(f"{comp_path}/standings")
    matches = _fetch(f"{comp_path}/matches?status=FINISHED")

    group_winners = _parse_group_winners(standings, report)
    champion, runner_up, semi_teams = _parse_knockouts(matches, report)

    while len(semi_teams) < 4:
        semi_teams.append("")

    bonuses = _parse_top_scorer_bonuses(comp_path, report)
    high_scorer = _parse_highest_scoring_team(matches, report)
    if high_scorer:
        bonuses["highest_scoring_team"] = high_scorer

    results = Results(
        champion=champion,
        runner_up=runner_up,
        semi_finalists=semi_teams,
        group_winners=group_winners,
        bonuses=bonuses,
    )
    return results, report


def merge_results(existing: Results, fetched: Results) -> Results:
    """Keep existing values when the API has not determined an outcome yet."""
    semis = list(existing.semi_finalists)
    if len(semis) < 4:
        semis.extend([""] * (4 - len(semis)))
    if sum(1 for s in fetched.semi_finalists if s) >= 4:
        semis = fetched.semi_finalists
    else:
        for i, team in enumerate(fetched.semi_finalists):
            if team:
                semis[i] = team

    group_winners = dict(existing.group_winners)
    for group in GROUPS:
        if fetched.group_winners.get(group):
            group_winners[group] = fetched.group_winners[group]

    bonuses = dict(existing.bonuses)
    for key, value in fetched.bonuses.items():
        if value:
            bonuses[key] = value

    return Results(
        champion=fetched.champion or existing.champion,
        runner_up=fetched.runner_up or existing.runner_up,
        semi_finalists=semis,
        group_winners=group_winners,
        bonuses=bonuses,
    )


def sync_and_merge(existing: Results) -> tuple[Results, SyncReport]:
    fetched, report = fetch_results_from_api()
    merged = merge_results(existing, fetched)
    if not any(
        [
            merged.champion,
            merged.runner_up,
            any(merged.semi_finalists),
            any(merged.group_winners.values()),
            any(merged.bonuses.values()),
        ]
    ):
        report.errors.append("No results available from the API yet (tournament may not have started).")
    return merged, report
