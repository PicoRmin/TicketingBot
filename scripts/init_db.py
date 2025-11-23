"""
Script to initialize database and create tables
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import engine, Base
# Import all models to ensure they are registered with Base
from app.models import User, Ticket, Attachment, Branch, Comment, TicketHistory, RefreshToken, SystemSettings  # noqa
from sqlalchemy.orm import Session
from app.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Create all tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")

        # Initialize default settings
        db: Session = SessionLocal()
        try:
            from app.services.settings_service import initialize_default_settings
            initialize_default_settings(db)
            logger.info("✅ Default settings initialized!")
        except Exception as e:
            logger.warning(f"Could not initialize default settings: {e}")
        finally:
            db.close()
        
        # Seed default branches if table is empty
        db: Session = SessionLocal()
        try:
            if db.query(Branch).count() == 0:
                logger.info("Seeding default branches...")
                branches = [
                    # Karaj
                    {"name": "گلشهر", "name_en": "Golshahr", "code": "karaj-golshahr"},
                    {"name": "گوهردشت", "name_en": "Gohardasht", "code": "karaj-gohardasht"},
                    {"name": "طالقانی", "name_en": "Taleghani", "code": "karaj-taleghani"},
                    # Tehran
                    {"name": "دفتر مرکزی", "name_en": "Head Office", "code": "tehran-central"},
                    {"name": "هفت تیر", "name_en": "Haft Tir", "code": "tehran-haft_tir"},
                    {"name": "دولت", "name_en": "Dolat", "code": "tehran-dolat"},
                    {"name": "سعادت آباد", "name_en": "Saadat Abad", "code": "tehran-saadat_abad"},
                    {"name": "شهرک غرب", "name_en": "Shahrak-e Gharb", "code": "tehran-shahrak_gharb"},
                    {"name": "پاسداران", "name_en": "Pasdaran", "code": "tehran-pasdaran"},
                    {"name": "نیاوران", "name_en": "Niavaran", "code": "tehran-niavaran"},
                    {"name": "پیروزی", "name_en": "Piroozi", "code": "tehran-piroozi"},
                    {"name": "نارمک", "name_en": "Narmak", "code": "tehran-narmak"},
                    {"name": "تهرانپارس", "name_en": "Tehranpars", "code": "tehran-tehranpars"},
                    {"name": "انقلاب", "name_en": "Enghelab", "code": "tehran-enghelab"},
                    {"name": "ستارخان", "name_en": "Sattarkhan", "code": "tehran-sattarkhan"},
                    {"name": "جنت آباد", "name_en": "Janat Abad", "code": "tehran-janat_abad"},
                ]
                for b in branches:
                    db.add(Branch(**b))
                db.commit()
                logger.info("✅ Default branches seeded")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    init_db()

