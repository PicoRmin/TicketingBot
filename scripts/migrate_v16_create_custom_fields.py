"""
Migration v16: Create Custom Fields tables
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def upgrade():
    """Create custom_fields and ticket_custom_field_values tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Create custom_fields table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS custom_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                label VARCHAR(255) NOT NULL,
                label_en VARCHAR(255),
                field_type VARCHAR(50) NOT NULL,
                description TEXT,
                config TEXT,
                category VARCHAR(50),
                department_id INTEGER,
                branch_id INTEGER,
                is_required BOOLEAN NOT NULL DEFAULT 0,
                is_visible_to_user BOOLEAN NOT NULL DEFAULT 1,
                is_editable_by_user BOOLEAN NOT NULL DEFAULT 1,
                default_value TEXT,
                display_order INTEGER NOT NULL DEFAULT 0,
                help_text TEXT,
                placeholder VARCHAR(255),
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
                FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL
            )
        """))
        
        # Create indexes for custom_fields
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_custom_field_active ON custom_fields(is_active)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_custom_field_category ON custom_fields(category)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_custom_field_department ON custom_fields(department_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_custom_field_branch ON custom_fields(branch_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_custom_field_type ON custom_fields(field_type)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_custom_field_order ON custom_fields(display_order)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_custom_field_name ON custom_fields(name)"))
        
        # Create ticket_custom_field_values table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ticket_custom_field_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                custom_field_id INTEGER NOT NULL,
                value TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
                FOREIGN KEY (custom_field_id) REFERENCES custom_fields(id) ON DELETE CASCADE,
                UNIQUE(ticket_id, custom_field_id)
            )
        """))
        
        # Create indexes for ticket_custom_field_values
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ticket_custom_field_value_ticket ON ticket_custom_field_values(ticket_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ticket_custom_field_value_field ON ticket_custom_field_values(custom_field_id)"))
        
        conn.commit()
        logger.info("Migration v16 completed: Created custom_fields and ticket_custom_field_values tables")


def downgrade():
    """Drop custom_fields and ticket_custom_field_values tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS ticket_custom_field_values"))
        conn.execute(text("DROP TABLE IF EXISTS custom_fields"))
        conn.commit()
        logger.info("Migration v16 downgraded: Dropped custom_fields and ticket_custom_field_values tables")


if __name__ == "__main__":
    upgrade()

