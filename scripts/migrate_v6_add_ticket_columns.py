# Migration: add missing columns to tickets table for Phase 6+
from pathlib import Path
import sys
from typing import Set

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine  # type: ignore
from sqlalchemy import text
from sqlalchemy.engine import Connection


def get_columns(conn: Connection, table: str) -> Set[str]:
    cols = set()
    for row in conn.execute(text(f"PRAGMA table_xinfo('{table}')")):
        cols.add(row[1])  # name column
    return cols


def column_exists(conn: Connection, table: str, column: str) -> bool:
    return column in get_columns(conn, table)


def add_column_if_missing(conn: Connection, table: str, ddl: str) -> None:
    # ddl example: "ADD COLUMN branch_id INTEGER"
    conn.execute(text(f"ALTER TABLE {table} {ddl}"))


def main() -> None:
    with engine.begin() as conn:
        cols = get_columns(conn, "tickets")
        print("Current tickets columns:", ", ".join(sorted(cols)))

        # Add branch_id (nullable INTEGER)
        if "branch_id" not in cols:
            print("Adding column: branch_id INTEGER NULL")
            add_column_if_missing(conn, "tickets", "ADD COLUMN branch_id INTEGER")

        # Add resolved_at (nullable DATETIME)
        if "resolved_at" not in cols:
            print("Adding column: resolved_at DATETIME NULL")
            add_column_if_missing(conn, "tickets", "ADD COLUMN resolved_at DATETIME")

        # Add closed_at (nullable DATETIME)
        if "closed_at" not in cols:
            print("Adding column: closed_at DATETIME NULL")
            add_column_if_missing(conn, "tickets", "ADD COLUMN closed_at DATETIME")

        print("Migration completed.")


if __name__ == "__main__":
    main()
