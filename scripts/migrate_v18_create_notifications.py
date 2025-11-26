"""
Migration v18: ایجاد جدول notifications برای فید درون‌برنامه‌ای
Migration v18: Create notifications table for in-app feed
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
    """
    Create notifications table and indexes
    """
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            if settings.DATABASE_URL.startswith("sqlite"):
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        body TEXT NOT NULL,
                        severity VARCHAR(20) NOT NULL DEFAULT 'info',
                        metadata TEXT NULL,
                        read_at DATETIME NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        title VARCHAR(255) NOT NULL,
                        body TEXT NOT NULL,
                        severity VARCHAR(20) NOT NULL DEFAULT 'info',
                        metadata JSONB NULL,
                        read_at TIMESTAMPTZ NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_created_at ON notifications(created_at DESC)"))
            conn.commit()
            logger.info("Migration v18 completed: notifications table created")
        except Exception as exc:
            conn.rollback()
            logger.error("Migration v18 failed: %s", exc, exc_info=True)
            raise


def downgrade():
    """
    Drop notifications table
    """
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS notifications"))
            conn.commit()
            logger.info("Migration v18 downgrade completed: notifications table dropped")
        except Exception as exc:
            conn.rollback()
            logger.error("Migration v18 downgrade failed: %s", exc, exc_info=True)
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    upgrade()

