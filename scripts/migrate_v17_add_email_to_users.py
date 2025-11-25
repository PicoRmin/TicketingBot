"""
Migration v17: اضافه کردن فیلد email به جدول users
Migration v17: Add email field to users table
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def upgrade():
    """
    اضافه کردن فیلد email به جدول users
    Add email field to users table
    """
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # بررسی وجود فیلد email
            if settings.DATABASE_URL.startswith("sqlite"):
                # برای SQLite
                result = conn.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM pragma_table_info('users') 
                    WHERE name = 'email'
                """))
                exists = result.fetchone()[0] > 0
            else:
                # برای PostgreSQL
                result = conn.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'email'
                """))
                exists = result.fetchone()[0] > 0
            
            if not exists:
                # اضافه کردن فیلد email
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN email VARCHAR(255) NULL
                """))
                
                # ایجاد index برای فیلد email
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)
                """))
                
                conn.commit()
                logger.info("Migration v17 completed: Added email field to users table")
            else:
                logger.info("Migration v17 skipped: email field already exists")
        except Exception as e:
            conn.rollback()
            logger.error(f"Migration v17 failed: {e}", exc_info=True)
            raise


def downgrade():
    """
    حذف فیلد email از جدول users
    Remove email field from users table
    """
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # حذف index
            conn.execute(text("""
                DROP INDEX IF EXISTS ix_users_email
            """))
            
            # حذف فیلد email
            if settings.DATABASE_URL.startswith("sqlite"):
                # SQLite نمی‌تواند ستون را حذف کند، باید جدول را بازسازی کرد
                logger.warning("SQLite does not support DROP COLUMN. Manual migration required.")
            else:
                conn.execute(text("""
                    ALTER TABLE users 
                    DROP COLUMN IF EXISTS email
                """))
            
            conn.commit()
            logger.info("Migration v17 downgrade completed: Removed email field from users table")
        except Exception as e:
            conn.rollback()
            logger.error(f"Migration v17 downgrade failed: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    upgrade()

