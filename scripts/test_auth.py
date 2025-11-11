"""
Test authentication functions
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models import User
from app.core.security import verify_password, get_password_hash

def test_auth():
    """Test authentication functions"""
    db = SessionLocal()
    try:
        # Test password verification with admin user
        user = db.query(User).filter(User.username == 'admin').first()
        if user:
            result = verify_password('admin123', user.password_hash)
            print(f"✅ Admin password verification: {result}")
            
            # Test wrong password
            result_wrong = verify_password('wrong_password', user.password_hash)
            print(f"✅ Wrong password verification: {result_wrong} (should be False)")
        else:
            print("❌ Admin user not found")
    finally:
        db.close()

if __name__ == "__main__":
    test_auth()

