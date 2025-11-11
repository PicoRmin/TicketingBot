"""
Script to create admin user
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models.user import User
from app.core.enums import UserRole, Language
from app.core.security import get_password_hash

def create_admin(username: str = "admin", password: str = "admin123", full_name: str = "مدیر سیستم"):
    """Create admin user"""
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == username).first()
        if existing_admin:
            print(f"❌ User with username '{username}' already exists!")
            return False
        
        # Create admin user
        password_hash = get_password_hash(password)
        
        admin = User(
            username=username,
            full_name=full_name,
            password_hash=password_hash,
            role=UserRole.ADMIN,
            language=Language.FA,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Full Name: {full_name}")
        print(f"\n⚠️  Please change the password after first login!")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
        full_name = sys.argv[3] if len(sys.argv) > 3 else "مدیر سیستم"
        create_admin(username, password, full_name)
    else:
        create_admin()

