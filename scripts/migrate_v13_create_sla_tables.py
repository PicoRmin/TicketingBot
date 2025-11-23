"""
Migration script to create SLA tables
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

def migrate():
    """Create SLA tables"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not Path(db_path).exists():
        print(f"Database file not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if sla_rules table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sla_rules'
        """)
        if cursor.fetchone():
            print("Table sla_rules already exists. Skipping creation.")
        else:
            # Create sla_rules table
            cursor.execute("""
                CREATE TABLE sla_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    description TEXT,
                    priority VARCHAR(20),
                    category VARCHAR(20),
                    department_id INTEGER,
                    response_time_minutes INTEGER NOT NULL,
                    resolution_time_minutes INTEGER NOT NULL,
                    response_warning_minutes INTEGER NOT NULL DEFAULT 30,
                    resolution_warning_minutes INTEGER NOT NULL DEFAULT 60,
                    escalation_enabled BOOLEAN NOT NULL DEFAULT 0,
                    escalation_after_minutes INTEGER,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
                )
            """)
            
            # Create indexes for sla_rules
            cursor.execute("CREATE INDEX idx_sla_rules_name ON sla_rules(name)")
            cursor.execute("CREATE INDEX idx_sla_rules_priority ON sla_rules(priority)")
            cursor.execute("CREATE INDEX idx_sla_rules_category ON sla_rules(category)")
            cursor.execute("CREATE INDEX idx_sla_rules_department ON sla_rules(department_id)")
            cursor.execute("CREATE INDEX idx_sla_priority_category ON sla_rules(priority, category)")
            cursor.execute("CREATE INDEX idx_sla_active ON sla_rules(is_active)")
            
            print("✅ Created sla_rules table")
        
        # Check if sla_logs table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sla_logs'
        """)
        if cursor.fetchone():
            print("Table sla_logs already exists. Skipping creation.")
        else:
            # Create sla_logs table
            cursor.execute("""
                CREATE TABLE sla_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    sla_rule_id INTEGER NOT NULL,
                    target_response_time TIMESTAMP NOT NULL,
                    target_resolution_time TIMESTAMP NOT NULL,
                    actual_response_time TIMESTAMP,
                    actual_resolution_time TIMESTAMP,
                    response_status VARCHAR(20),
                    resolution_status VARCHAR(20),
                    escalated BOOLEAN NOT NULL DEFAULT 0,
                    escalated_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
                    FOREIGN KEY (sla_rule_id) REFERENCES sla_rules(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for sla_logs
            cursor.execute("CREATE INDEX idx_sla_log_ticket ON sla_logs(ticket_id)")
            cursor.execute("CREATE INDEX idx_sla_log_rule ON sla_logs(sla_rule_id)")
            cursor.execute("CREATE INDEX idx_sla_log_status ON sla_logs(response_status, resolution_status)")
            cursor.execute("CREATE INDEX idx_sla_log_escalated ON sla_logs(escalated)")
            
            print("✅ Created sla_logs table")
        
        conn.commit()
        print("✅ Migration v13 completed successfully")
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


