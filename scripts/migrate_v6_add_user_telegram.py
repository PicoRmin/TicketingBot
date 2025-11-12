# Migration: add telegram integration columns to users table
from pathlib import Path
import sys
from typing import Set

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.database import engine  # type: ignore


def get_columns(table: str) -> Set[str]:
    with engine.connect() as conn:
        result = conn.execute(text(f"PRAGMA table_xinfo('{table}')"))
        return {row[1] for row in result}


def add_column(column_ddl: str) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE users {column_ddl}"))


def ensure_unique_index() -> None:
    with engine.begin() as conn:
        conn.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_telegram_chat_id ON users(telegram_chat_id) WHERE telegram_chat_id IS NOT NULL")
        )


def main() -> None:
    columns = get_columns("users")
    print("Current users columns:", ", ".join(sorted(columns)))

    if "telegram_chat_id" not in columns:
        print("Adding column: telegram_chat_id TEXT NULL")
        add_column("ADD COLUMN telegram_chat_id TEXT")
    else:
        print("Column telegram_chat_id already exists")

    ensure_unique_index()
    print("Migration completed.")


if __name__ == "__main__":
    main()
