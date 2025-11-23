"""
Migration script to create system_settings table
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from app.config import settings

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)


def main():
    inspector = inspect(engine)
    if 'system_settings' not in inspector.get_table_names():
        print("Creating system_settings table...")
        SQL = """
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT,
            value_type TEXT DEFAULT 'string',
            description TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_by_id INTEGER
        );
        CREATE INDEX IF NOT EXISTS ix_system_settings_key ON system_settings(key);
        """
        with engine.connect() as conn:
            for statement in SQL.split(';')[:-1]:
                if statement.strip():
                    conn.execute(text(statement.strip()))
            conn.commit()
        print("system_settings table created.")
        
        # Initialize default settings
        from app.database import SessionLocal
        from app.services.settings_service import initialize_default_settings
        db = SessionLocal()
        try:
            initialize_default_settings(db)
            print("Default settings initialized.")
        finally:
            db.close()
    else:
        print("system_settings table already exists.")


if __name__ == "__main__":
    main()

