"""
Migration script to create automation_rules table
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

def migrate():
    """Create automation_rules table"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not Path(db_path).exists():
        print(f"Database file not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if automation_rules table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='automation_rules'
        """)
        if cursor.fetchone():
            print("Table automation_rules already exists. Skipping creation.")
        else:
            # Create automation_rules table
            cursor.execute("""
                CREATE TABLE automation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    description TEXT,
                    rule_type VARCHAR(50) NOT NULL,
                    conditions TEXT,
                    actions TEXT NOT NULL,
                    priority INTEGER NOT NULL DEFAULT 100,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes for automation_rules
            cursor.execute("CREATE INDEX idx_automation_rules_name ON automation_rules(name)")
            cursor.execute("CREATE INDEX idx_automation_rules_type ON automation_rules(rule_type)")
            cursor.execute("CREATE INDEX idx_automation_type_active ON automation_rules(rule_type, is_active)")
            cursor.execute("CREATE INDEX idx_automation_priority ON automation_rules(priority)")
            
            print("✅ Created automation_rules table")
        
        conn.commit()
        print("✅ Migration v14 completed successfully")
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

