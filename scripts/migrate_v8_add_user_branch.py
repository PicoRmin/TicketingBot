"""Add branch_id column to users table if missing."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.database import engine


def has_column(column_name: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_xinfo('users')"))
        return any(row[1] == column_name for row in result)


def main() -> None:
    if has_column("branch_id"):
        print("users.branch_id already exists")
        return

    statements = [
        "ALTER TABLE users ADD COLUMN branch_id INTEGER",
        "CREATE INDEX IF NOT EXISTS ix_users_branch_id ON users(branch_id)"
    ]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
    print("branch_id column added to users table")


if __name__ == "__main__":
    main()
