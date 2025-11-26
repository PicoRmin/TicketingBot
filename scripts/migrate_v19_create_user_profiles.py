"""
Migration v19: create user_profiles table for onboarding data
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
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            if settings.DATABASE_URL.startswith("sqlite"):
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL UNIQUE,
                        first_name VARCHAR(120),
                        last_name VARCHAR(120),
                        phone VARCHAR(50),
                        age_range VARCHAR(32),
                        skill_level VARCHAR(32),
                        goals TEXT,
                        responsibilities TEXT,
                        preferred_habits TEXT,
                        notes TEXT,
                        completed BOOLEAN NOT NULL DEFAULT 0,
                        completed_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                    );
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                        first_name VARCHAR(120),
                        last_name VARCHAR(120),
                        phone VARCHAR(50),
                        age_range VARCHAR(32),
                        skill_level VARCHAR(32),
                        goals JSONB,
                        responsibilities TEXT,
                        preferred_habits JSONB,
                        notes TEXT,
                        completed BOOLEAN NOT NULL DEFAULT FALSE,
                        completed_at TIMESTAMPTZ,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_profiles_user_id ON user_profiles(user_id)"))
            conn.commit()
            logger.info("Migration v19 completed: user_profiles table created")
        except Exception as exc:
            conn.rollback()
            logger.error("Migration v19 failed: %s", exc, exc_info=True)
            raise


def downgrade():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS user_profiles"))
            conn.commit()
            logger.info("Migration v19 downgrade completed: user_profiles dropped")
        except Exception as exc:
            conn.rollback()
            logger.error("Migration v19 downgrade failed: %s", exc, exc_info=True)
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    upgrade()

