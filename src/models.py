from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Picks:
    champion: str = ""
    runner_up: str = ""
    semi_finalists: list[str] = field(default_factory=lambda: ["", "", "", ""])
    group_winners: dict[str, str] = field(default_factory=dict)
    bonuses: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "champion": self.champion,
            "runner_up": self.runner_up,
            "semi_finalists": self.semi_finalists,
            "group_winners": self.group_winners,
            "bonuses": self.bonuses,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Picks":
        if not data:
            return cls()
        return cls(
            champion=data.get("champion", ""),
            runner_up=data.get("runner_up", ""),
            semi_finalists=data.get("semi_finalists", ["", "", "", ""]),
            group_winners=data.get("group_winners", {}),
            bonuses=data.get("bonuses", {}),
        )


@dataclass
class Entry:
    id: int | str
    display_name: str
    picks: Picks
    total_points: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Results:
    champion: str = ""
    runner_up: str = ""
    semi_finalists: list[str] = field(default_factory=lambda: ["", "", "", ""])
    group_winners: dict[str, str] = field(default_factory=dict)
    bonuses: dict[str, str] = field(default_factory=dict)
    updated_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "champion": self.champion,
            "runner_up": self.runner_up,
            "semi_finalists": self.semi_finalists,
            "group_winners": self.group_winners,
            "bonuses": self.bonuses,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Results":
        if not data:
            return cls()
        return cls(
            champion=data.get("champion", ""),
            runner_up=data.get("runner_up", ""),
            semi_finalists=data.get("semi_finalists", ["", "", "", ""]),
            group_winners=data.get("group_winners", {}),
            bonuses=data.get("bonuses", {}),
        )
