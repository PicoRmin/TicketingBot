"""
Migration script to create departments table and add priority/assignment fields to tickets
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

def migrate():
    """Create departments table and update tickets table"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not Path(db_path).exists():
        print(f"Database file not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if departments table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='departments'
        """)
        if cursor.fetchone():
            print("Table departments already exists. Skipping creation.")
        else:
            # Create departments table
            cursor.execute("""
                CREATE TABLE departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    name_en VARCHAR(255),
                    code VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes for departments
            cursor.execute("CREATE INDEX idx_departments_code ON departments(code)")
            cursor.execute("CREATE INDEX idx_departments_name ON departments(name)")
            
            print("✅ Created departments table")
        
        # Check if priority column exists in tickets
        cursor.execute("PRAGMA table_info(tickets)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'priority' not in columns:
            # Add priority column (default: medium)
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium'
            """)
            cursor.execute("CREATE INDEX idx_ticket_priority ON tickets(priority)")
            print("✅ Added priority column to tickets")
        
        if 'department_id' not in columns:
            # Add department_id column
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN department_id INTEGER
            """)
            cursor.execute("""
                CREATE INDEX idx_ticket_department ON tickets(department_id)
            """)
            print("✅ Added department_id column to tickets")
        
        if 'assigned_to_id' not in columns:
            # Add assigned_to_id column
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN assigned_to_id INTEGER
            """)
            cursor.execute("""
                CREATE INDEX idx_ticket_assigned ON tickets(assigned_to_id)
            """)
            print("✅ Added assigned_to_id column to tickets")
        
        if 'estimated_resolution_hours' not in columns:
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN estimated_resolution_hours INTEGER
            """)
            print("✅ Added estimated_resolution_hours column to tickets")
        
        if 'actual_resolution_hours' not in columns:
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN actual_resolution_hours INTEGER
            """)
            print("✅ Added actual_resolution_hours column to tickets")
        
        if 'satisfaction_rating' not in columns:
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN satisfaction_rating INTEGER
            """)
            print("✅ Added satisfaction_rating column to tickets")
        
        if 'satisfaction_comment' not in columns:
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN satisfaction_comment TEXT
            """)
            print("✅ Added satisfaction_comment column to tickets")
        
        if 'cost' not in columns:
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN cost NUMERIC(10, 2)
            """)
            print("✅ Added cost column to tickets")
        
        if 'first_response_at' not in columns:
            cursor.execute("""
                ALTER TABLE tickets 
                ADD COLUMN first_response_at TIMESTAMP
            """)
            print("✅ Added first_response_at column to tickets")
        
        # Check if department_id exists in users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in cursor.fetchall()]
        
        if 'department_id' not in user_columns:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN department_id INTEGER
            """)
            cursor.execute("""
                CREATE INDEX idx_users_department ON users(department_id)
            """)
            print("✅ Added department_id column to users")
        
        # Create composite indexes
        try:
            cursor.execute("""
                CREATE INDEX idx_ticket_status_priority 
                ON tickets(status, priority)
            """)
            print("✅ Created composite index for status and priority")
        except sqlite3.OperationalError:
            print("⚠️  Composite index may already exist, skipping...")
        
        conn.commit()
        print("✅ Migration v12 completed successfully")
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

