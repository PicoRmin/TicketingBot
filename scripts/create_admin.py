"""
Script to create admin user
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models import User, Branch
from app.core.enums import UserRole, Language
from app.core.security import get_password_hash

def create_admin(username: str = "admin", password: str = "admin123", full_name: str = "مدیر سیستم", role: str = UserRole.CENTRAL_ADMIN.value, branch: str | None = None):
    """Create admin user"""
    db = SessionLocal()
    try:
        try:
            role_enum = UserRole(role)
        except ValueError:
            print(f"❌ Invalid role '{role}'. Available roles: {[r.value for r in UserRole]}")
            return False

        branch_id = None
        if branch:
            branch_obj = None
            if branch.isdigit():
                branch_obj = db.query(Branch).filter(Branch.id == int(branch)).first()
            if not branch_obj:
                branch_obj = db.query(Branch).filter(Branch.code == branch).first()
            if not branch_obj:
                print(f"❌ Branch '{branch}' not found (use branch ID or code).")
                return False
            branch_id = branch_obj.id

        if role_enum == UserRole.BRANCH_ADMIN and branch_id is None:
            print("❌ Branch admin must be assigned to a branch (provide branch ID or code).")
            return False

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
            role=role_enum,
            language=Language.FA,
            is_active=True,
            branch_id=branch_id,
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Full Name: {full_name}")
        print(f"   Role: {role_enum.value}")
        if branch_id:
            print(f"   Branch ID: {branch_id}")
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
        role = sys.argv[4] if len(sys.argv) > 4 else UserRole.CENTRAL_ADMIN.value
        branch = sys.argv[5] if len(sys.argv) > 5 else None
        create_admin(username, password, full_name, role, branch)
    else:
        create_admin()

