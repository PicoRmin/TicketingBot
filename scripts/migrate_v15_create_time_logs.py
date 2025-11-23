"""
Migration script to create time_logs table
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

def migrate():
    """Create time_logs table"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not Path(db_path).exists():
        print(f"Database file not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if time_logs table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='time_logs'
        """)
        if cursor.fetchone():
            print("Table time_logs already exists. Skipping creation.")
        else:
            # Create time_logs table
            cursor.execute("""
                CREATE TABLE time_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration_minutes INTEGER,
                    description TEXT,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for time_logs
            cursor.execute("CREATE INDEX idx_time_log_ticket ON time_logs(ticket_id)")
            cursor.execute("CREATE INDEX idx_time_log_user ON time_logs(user_id)")
            cursor.execute("CREATE INDEX idx_time_log_active ON time_logs(is_active)")
            cursor.execute("CREATE INDEX idx_time_log_ticket_user ON time_logs(ticket_id, user_id)")
            
            print("✅ Created time_logs table")
        
        conn.commit()
        print("✅ Migration v15 completed successfully")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

