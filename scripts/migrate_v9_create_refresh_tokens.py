"""Create refresh_tokens table if it doesn't exist."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.database import engine

SQL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token_hash TEXT NOT NULL UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        expires_at DATETIME NOT NULL,
        revoked BOOLEAN DEFAULT 0 NOT NULL,
        revoked_at DATETIME,
        user_agent TEXT,
        ip_address TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_refresh_tokens_user_id ON refresh_tokens(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_refresh_tokens_expires_at ON refresh_tokens(expires_at)"
]


def main() -> None:
    with engine.begin() as conn:
        for statement in SQL_STATEMENTS:
            conn.execute(text(statement))
    print("refresh_tokens table ensured.")


if __name__ == "__main__":
    main()
