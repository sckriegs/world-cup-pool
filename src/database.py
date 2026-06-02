import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from src.config import GROUPS, SEEDED_TEAMS, SQLITE_PATH, TEAMS_FILE
from src.models import Entry, Picks, Results
from src.scoring import calculate_points


def load_teams_data() -> dict:
    with open(TEAMS_FILE, encoding="utf-8") as f:
        return json.load(f)


def all_teams() -> list[str]:
    data = load_teams_data()
    teams: list[str] = []
    for group in GROUPS:
        teams.extend(data["groups"][group])
    return sorted(set(teams))


def dark_horse_teams() -> list[str]:
    return sorted(t for t in all_teams() if t not in SEEDED_TEAMS)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class Database:
    def get_entry_by_name(self, display_name: str) -> Entry | None:
        raise NotImplementedError

    def save_entry(self, display_name: str, picks: Picks) -> Entry:
        raise NotImplementedError

    def list_entries(self) -> list[Entry]:
        raise NotImplementedError

    def update_entry_points(self, entry_id: int | str, total_points: int) -> None:
        raise NotImplementedError

    def delete_entry(self, entry_id: int | str) -> bool:
        raise NotImplementedError

    def get_results(self) -> Results:
        raise NotImplementedError

    def save_results(self, results: Results) -> None:
        raise NotImplementedError

    def recalculate_all_points(self) -> None:
        results = self.get_results()
        for entry in self.list_entries():
            points = calculate_points(entry.picks, results)["total"]
            self.update_entry_points(entry.id, points)


class SQLiteDatabase(Database):
    def __init__(self, path: Path = SQLITE_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    display_name TEXT NOT NULL COLLATE NOCASE,
                    picks TEXT NOT NULL DEFAULT '{}',
                    total_points INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(display_name COLLATE NOCASE)
                );

                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    data TEXT NOT NULL DEFAULT '{}',
                    updated_at TEXT
                );

                INSERT OR IGNORE INTO results (id, data, updated_at) VALUES (1, '{}', NULL);
                """
            )

    def _row_to_entry(self, row: sqlite3.Row) -> Entry:
        picks_data = json.loads(row["picks"])
        return Entry(
            id=row["id"],
            display_name=row["display_name"],
            picks=Picks.from_dict(picks_data),
            total_points=row["total_points"],
            created_at=_parse_dt(row["created_at"]),
            updated_at=_parse_dt(row["updated_at"]),
        )

    def get_entry_by_name(self, display_name: str) -> Entry | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM entries WHERE display_name = ? COLLATE NOCASE",
                (display_name.strip(),),
            ).fetchone()
        return self._row_to_entry(row) if row else None

    def save_entry(self, display_name: str, picks: Picks) -> Entry:
        name = display_name.strip()
        now = _now_iso()
        picks_json = json.dumps(picks.to_dict())

        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM entries WHERE display_name = ? COLLATE NOCASE",
                (name,),
            ).fetchone()

            if existing:
                conn.execute(
                    """
                    UPDATE entries
                    SET picks = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (picks_json, now, existing["id"]),
                )
                entry_id = existing["id"]
                created_at = conn.execute(
                    "SELECT created_at FROM entries WHERE id = ?", (entry_id,)
                ).fetchone()["created_at"]
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO entries (display_name, picks, total_points, created_at, updated_at)
                    VALUES (?, ?, 0, ?, ?)
                    """,
                    (name, picks_json, now, now),
                )
                entry_id = cursor.lastrowid
                created_at = now

            conn.commit()

        entry = Entry(
            id=entry_id,
            display_name=name,
            picks=picks,
            created_at=_parse_dt(created_at),
            updated_at=_parse_dt(now),
        )
        results = self.get_results()
        points = calculate_points(picks, results)["total"]
        self.update_entry_points(entry_id, points)
        entry.total_points = points
        return entry

    def list_entries(self) -> list[Entry]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM entries ORDER BY total_points DESC, created_at ASC"
            ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def update_entry_points(self, entry_id: int | str, total_points: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE entries SET total_points = ? WHERE id = ?",
                (total_points, entry_id),
            )
            conn.commit()

    def delete_entry(self, entry_id: int | str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_results(self) -> Results:
        with self._connect() as conn:
            row = conn.execute("SELECT data, updated_at FROM results WHERE id = 1").fetchone()
        if not row:
            return Results()
        data = json.loads(row["data"])
        results = Results.from_dict(data)
        results.updated_at = _parse_dt(row["updated_at"])
        return results

    def save_results(self, results: Results) -> None:
        now = _now_iso()
        with self._connect() as conn:
            conn.execute(
                "UPDATE results SET data = ?, updated_at = ? WHERE id = 1",
                (json.dumps(results.to_dict()), now),
            )
            conn.commit()
        self.recalculate_all_points()

    def recalculate_all_points(self) -> None:
        results = self.get_results()
        for entry in self.list_entries():
            points = calculate_points(entry.picks, results)["total"]
            self.update_entry_points(entry.id, points)


class SupabaseDatabase(Database):
    def __init__(self, url: str, key: str):
        from supabase import create_client

        self.client = create_client(url, key)

    def _row_to_entry(self, row: dict) -> Entry:
        picks_data = row["picks"] if isinstance(row["picks"], dict) else json.loads(row["picks"])
        return Entry(
            id=row["id"],
            display_name=row["display_name"],
            picks=Picks.from_dict(picks_data),
            total_points=row.get("total_points", 0),
            created_at=_parse_dt(row.get("created_at")),
            updated_at=_parse_dt(row.get("updated_at")),
        )

    def get_entry_by_name(self, display_name: str) -> Entry | None:
        response = (
            self.client.table("entries")
            .select("*")
            .ilike("display_name", display_name.strip())
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return self._row_to_entry(response.data[0])

    def save_entry(self, display_name: str, picks: Picks) -> Entry:
        name = display_name.strip()
        now = _now_iso()
        picks_dict = picks.to_dict()
        existing = self.get_entry_by_name(name)

        if existing:
            response = (
                self.client.table("entries")
                .update({"picks": picks_dict, "updated_at": now})
                .eq("id", existing.id)
                .execute()
            )
            entry = self._row_to_entry(response.data[0])
        else:
            response = (
                self.client.table("entries")
                .insert(
                    {
                        "display_name": name,
                        "picks": picks_dict,
                        "total_points": 0,
                        "created_at": now,
                        "updated_at": now,
                    }
                )
                .execute()
            )
            entry = self._row_to_entry(response.data[0])

        results = self.get_results()
        points = calculate_points(entry.picks, results)["total"]
        self.update_entry_points(entry.id, points)
        entry.total_points = points
        return entry

    def list_entries(self) -> list[Entry]:
        response = (
            self.client.table("entries")
            .select("*")
            .order("total_points", desc=True)
            .order("created_at")
            .execute()
        )
        return [self._row_to_entry(row) for row in response.data]

    def update_entry_points(self, entry_id: int | str, total_points: int) -> None:
        self.client.table("entries").update({"total_points": total_points}).eq("id", entry_id).execute()

    def delete_entry(self, entry_id: int | str) -> bool:
        response = self.client.table("entries").delete().eq("id", entry_id).execute()
        return bool(response.data)

    def get_results(self) -> Results:
        response = self.client.table("results").select("*").eq("id", 1).limit(1).execute()
        if not response.data:
            return Results()
        row = response.data[0]
        data = row["data"] if isinstance(row["data"], dict) else json.loads(row["data"])
        results = Results.from_dict(data)
        results.updated_at = _parse_dt(row.get("updated_at"))
        return results

    def save_results(self, results: Results) -> None:
        now = _now_iso()
        self.client.table("results").upsert(
            {"id": 1, "data": results.to_dict(), "updated_at": now}
        ).execute()
        self.recalculate_all_points()

    def recalculate_all_points(self) -> None:
        results = self.get_results()
        for entry in self.list_entries():
            points = calculate_points(entry.picks, results)["total"]
            self.update_entry_points(entry.id, points)


@st.cache_resource
def get_database() -> Database:
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if hasattr(st, "secrets"):
        supabase_url = supabase_url or st.secrets.get("SUPABASE_URL")
        supabase_key = supabase_key or st.secrets.get("SUPABASE_KEY")

    if supabase_url and supabase_key:
        return SupabaseDatabase(supabase_url, supabase_key)
    return SQLiteDatabase()
