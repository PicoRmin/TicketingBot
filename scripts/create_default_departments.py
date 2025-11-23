"""
Script to create default departments
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Department
from app.config import settings

def create_default_departments():
    """Create default departments"""
    db = SessionLocal()
    
    try:
        # Check if departments already exist
        existing = db.query(Department).count()
        if existing > 0:
            print(f"⚠️  {existing} department(s) already exist. Skipping creation.")
            return
        
        departments = [
            {
                "name": "دپارتمان IT",
                "name_en": "IT Department",
                "code": "it_department",
                "description": "دپارتمان فناوری اطلاعات - مسئول حل مشکلات نرم‌افزاری، سخت‌افزاری، شبکه و سرورها",
                "is_active": True
            },
            {
                "name": "دپارتمان مالی",
                "name_en": "Finance Department",
                "code": "finance_department",
                "description": "دپارتمان مالی - مسئول حل مشکلات سیستم مالی و نرم‌افزار حسابداری",
                "is_active": True
            },
            {
                "name": "دپارتمان شبکه",
                "name_en": "Network Department",
                "code": "network_department",
                "description": "دپارتمان شبکه - مسئول حل مشکلات اینترنت، شبکه داخلی و امنیت شبکه",
                "is_active": True
            },
            {
                "name": "دپارتمان عمومی",
                "name_en": "General Department",
                "code": "general_department",
                "description": "دپارتمان عمومی - مسئول تیکت‌های عمومی و سایر موارد",
                "is_active": True
            }
        ]
        
        for dept_data in departments:
            # Check if department with this code already exists
            existing_dept = db.query(Department).filter(Department.code == dept_data["code"]).first()
            if existing_dept:
                print(f"⚠️  Department '{dept_data['code']}' already exists. Skipping...")
                continue
            
            department = Department(**dept_data)
            db.add(department)
            print(f"✅ Created department: {dept_data['name']} ({dept_data['code']})")
        
        db.commit()
        print(f"\n✅ Successfully created {len(departments)} default departments")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating departments: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_default_departments()

