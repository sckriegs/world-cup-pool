#!/usr/bin/env python3
"""Pull latest results from football-data.org and recalculate all entry scores."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.database import get_database
from src.results_sync import sync_and_merge


def main() -> None:
    db = get_database()
    current = db.get_results()
    merged, report = sync_and_merge(current)
    db.save_results(merged)

    print("=== Sync report ===")
    for msg in report.messages:
        print(f"  • {msg}")
    for err in report.errors:
        print(f"  ! {err}")

    entries = db.list_entries()
    print(f"\nRecalculated {len(entries)} entries.")
    for entry in entries[:10]:
        print(f"  {entry.display_name}: {entry.total_points} pts")
    if len(entries) > 10:
        print(f"  ... and {len(entries) - 10} more")


if __name__ == "__main__":
    main()
