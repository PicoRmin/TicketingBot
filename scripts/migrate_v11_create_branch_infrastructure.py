"""
Migration script to create branch_infrastructure table
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

def migrate():
    """Create branch_infrastructure table"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not Path(db_path).exists():
        print(f"Database file not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='branch_infrastructure'
        """)
        if cursor.fetchone():
            print("Table branch_infrastructure already exists. Skipping migration.")
            return True
        
        # Create branch_infrastructure table
        cursor.execute("""
            CREATE TABLE branch_infrastructure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_id INTEGER NOT NULL,
                infrastructure_type VARCHAR(50) NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                ip_address VARCHAR(50),
                hostname VARCHAR(255),
                model VARCHAR(255),
                serial_number VARCHAR(255),
                service_type VARCHAR(100),
                service_url VARCHAR(512),
                status VARCHAR(50) NOT NULL DEFAULT 'active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                created_by_id INTEGER,
                updated_by_id INTEGER,
                FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (updated_by_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_branch_infrastructure_branch_id ON branch_infrastructure(branch_id)")
        cursor.execute("CREATE INDEX idx_branch_infrastructure_type ON branch_infrastructure(infrastructure_type)")
        
        conn.commit()
        print("✅ Migration v11 completed: Created branch_infrastructure table")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

