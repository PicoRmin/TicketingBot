"""
Migration v20: create knowledge_articles table
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
                    CREATE TABLE IF NOT EXISTS knowledge_articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        slug VARCHAR(255) NOT NULL UNIQUE,
                        title VARCHAR(255) NOT NULL,
                        summary VARCHAR(512),
                        content TEXT NOT NULL,
                        category VARCHAR(120),
                        language VARCHAR(8) NOT NULL DEFAULT 'fa',
                        tags TEXT,
                        is_published BOOLEAN NOT NULL DEFAULT 1,
                        created_by_id INTEGER,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(created_by_id) REFERENCES users(id) ON DELETE SET NULL
                    );
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS knowledge_articles (
                        id SERIAL PRIMARY KEY,
                        slug VARCHAR(255) NOT NULL UNIQUE,
                        title VARCHAR(255) NOT NULL,
                        summary VARCHAR(512),
                        content TEXT NOT NULL,
                        category VARCHAR(120),
                        language VARCHAR(8) NOT NULL DEFAULT 'fa',
                        tags JSONB,
                        is_published BOOLEAN NOT NULL DEFAULT TRUE,
                        created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_knowledge_articles_category ON knowledge_articles(category)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_knowledge_articles_slug ON knowledge_articles(slug)"))
            conn.execute(text("""
                INSERT INTO knowledge_articles (slug, title, summary, content, category, language, tags, is_published)
                VALUES
                ('network-basics', 'راهنمای سریع عیب‌یابی اینترنت شعب', 'مراحل کلیدی برای بررسی لینک‌ها و مودم', '۱) بررسی روتر
۲) تست پینگ
۳) ریست سرویس', 'network', 'fa', '["internet","branch"]', 1),
                ('voip-quality', 'بهبود کیفیت VoIP', 'تنظیم QoS و بررسی SIP', 'بررسی jitter، latency و تنظیم VLAN برای کلاس‌های آنلاین.', 'voip', 'fa', '["voip","quality"]', 1)
                ON CONFLICT (slug) DO NOTHING;
            """))
            conn.commit()
            logger.info("Migration v20 completed: knowledge_articles table created")
        except Exception as exc:
            conn.rollback()
            logger.error("Migration v20 failed: %s", exc, exc_info=True)
            raise


def downgrade():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS knowledge_articles"))
            conn.commit()
            logger.info("Migration v20 downgrade completed: knowledge_articles dropped")
        except Exception as exc:
            conn.rollback()
            logger.error("Migration v20 downgrade failed: %s", exc, exc_info=True)
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    upgrade()

