"""
Migration v21: create telegram_sessions table for session management
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from app.config import settings
import logging

logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def upgrade():
    """Create telegram_sessions table"""
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            if settings.DATABASE_URL.startswith("sqlite"):
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS telegram_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        telegram_user_id INTEGER NOT NULL,
                        token VARCHAR(512) NOT NULL,
                        ip_address VARCHAR(64),
                        user_agent VARCHAR(255),
                        last_activity DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        expires_at DATETIME NOT NULL,
                        is_active INTEGER NOT NULL DEFAULT 1,
                        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                    );
                """))
                # Create indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_user_id ON telegram_sessions(user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_telegram_user_id ON telegram_sessions(telegram_user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_last_activity ON telegram_sessions(last_activity)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_expires_at ON telegram_sessions(expires_at)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_user_active ON telegram_sessions(user_id, is_active)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_telegram_user ON telegram_sessions(telegram_user_id, is_active)"))
            else:
                # PostgreSQL
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS telegram_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        telegram_user_id INTEGER NOT NULL,
                        token VARCHAR(512) NOT NULL,
                        ip_address VARCHAR(64),
                        user_agent VARCHAR(255),
                        last_activity TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        expires_at TIMESTAMPTZ NOT NULL,
                        is_active INTEGER NOT NULL DEFAULT 1
                    );
                """))
                # Create indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_user_id ON telegram_sessions(user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_telegram_user_id ON telegram_sessions(telegram_user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_last_activity ON telegram_sessions(last_activity)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_expires_at ON telegram_sessions(expires_at)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_user_active ON telegram_sessions(user_id, is_active)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_telegram_sessions_telegram_user ON telegram_sessions(telegram_user_id, is_active)"))
            
            conn.commit()
            logger.info("Migration v21 completed: telegram_sessions table created")
        except Exception as exc:
            conn.rollback()
            logger.error("Migration v21 failed: %s", exc, exc_info=True)
            raise


def downgrade():
    """Drop telegram_sessions table"""
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS telegram_sessions"))
            conn.commit()
            logger.info("Migration v21 downgrade completed: telegram_sessions dropped")
        except Exception as exc:
            conn.rollback()
            logger.error("Migration v21 downgrade failed: %s", exc, exc_info=True)
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    upgrade()

