"""
Script to list all branches with their IDs
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models import Branch


def list_all_branches():
    """List all branches with their IDs"""
    db = SessionLocal()
    try:
        branches = db.query(Branch).order_by(Branch.id).all()
        
        if not branches:
            print("❌ هیچ شعبه‌ای در دیتابیس وجود ندارد.")
            return
        
        print("\n" + "="*60)
        print("📋 لیست شعب")
        print("="*60)
        print(f"{'ID':<5} {'نام':<30} {'کد':<15} {'وضعیت':<10}")
        print("-"*60)
        
        for branch in branches:
            status = "✅ فعال" if branch.is_active else "❌ غیرفعال"
            print(f"{branch.id:<5} {branch.name:<30} {branch.code:<15} {status:<10}")
        
        print("="*60)
        print(f"\n📊 مجموع: {len(branches)} شعبه")
        print("\n💡 برای استفاده در API:")
        print("   GET /api/branches")
        print("   یا از Swagger: http://127.0.0.1:8000/docs")
        
    finally:
        db.close()


if __name__ == "__main__":
    list_all_branches()

