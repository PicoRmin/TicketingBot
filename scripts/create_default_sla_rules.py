"""
Script to create default SLA rules based on priorities
ساعت کاری: 9 صبح تا 17 (شنبه تا پنج‌شنبه)
حداقل تایم: 30 دقیقه
حداکثر تایم: 24 ساعت
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import SLARule
from app.core.enums import TicketPriority, TicketCategory
from app.config import settings

def create_default_sla_rules():
    """Create default SLA rules based on priorities"""
    db = SessionLocal()
    
    try:
        # Check if SLA rules already exist
        existing = db.query(SLARule).count()
        if existing > 0:
            print(f"⚠️  {existing} SLA rule(s) already exist. Skipping creation.")
            print("💡 برای ایجاد مجدد، ابتدا قوانین موجود را حذف کنید.")
            return
        
        # Default SLA rules based on requirements
        # ساعت کاری: 9 صبح تا 17 (شنبه تا پنج‌شنبه)
        # حداقل تایم: 30 دقیقه
        # حداکثر تایم: 24 ساعت (1440 دقیقه)
        
        sla_rules = [
            {
                "name": "SLA - اولویت بحرانی (Critical)",
                "description": "قانون SLA برای تیکت‌های با اولویت بحرانی - 30 دقیقه پاسخ، 2 ساعت حل",
                "priority": TicketPriority.CRITICAL,
                "category": None,
                "department_id": None,
                "response_time_minutes": 30,  # 30 دقیقه (حداقل)
                "resolution_time_minutes": 120,  # 2 ساعت
                "response_warning_minutes": 10,  # 10 دقیقه قبل از مهلت
                "resolution_warning_minutes": 30,  # 30 دقیقه قبل از مهلت
                "escalation_enabled": True,
                "escalation_after_minutes": 60,  # 1 ساعت بعد
                "is_active": True
            },
            {
                "name": "SLA - اولویت بالا (High)",
                "description": "قانون SLA برای تیکت‌های با اولویت بالا - 1 ساعت پاسخ، 4 ساعت حل",
                "priority": TicketPriority.HIGH,
                "category": None,
                "department_id": None,
                "response_time_minutes": 60,  # 1 ساعت
                "resolution_time_minutes": 240,  # 4 ساعت
                "response_warning_minutes": 20,  # 20 دقیقه قبل از مهلت
                "resolution_warning_minutes": 60,  # 1 ساعت قبل از مهلت
                "escalation_enabled": True,
                "escalation_after_minutes": 180,  # 3 ساعت بعد
                "is_active": True
            },
            {
                "name": "SLA - اولویت متوسط (Medium)",
                "description": "قانون SLA برای تیکت‌های با اولویت متوسط - 2 ساعت پاسخ، 8 ساعت حل",
                "priority": TicketPriority.MEDIUM,
                "category": None,
                "department_id": None,
                "response_time_minutes": 120,  # 2 ساعت
                "resolution_time_minutes": 480,  # 8 ساعت
                "response_warning_minutes": 30,  # 30 دقیقه قبل از مهلت
                "resolution_warning_minutes": 120,  # 2 ساعت قبل از مهلت
                "escalation_enabled": True,
                "escalation_after_minutes": 360,  # 6 ساعت بعد
                "is_active": True
            },
            {
                "name": "SLA - اولویت پایین (Low)",
                "description": "قانون SLA برای تیکت‌های با اولویت پایین - 4 ساعت پاسخ، 24 ساعت حل",
                "priority": TicketPriority.LOW,
                "category": None,
                "department_id": None,
                "response_time_minutes": 240,  # 4 ساعت
                "resolution_time_minutes": 1440,  # 24 ساعت (حداکثر)
                "response_warning_minutes": 60,  # 1 ساعت قبل از مهلت
                "resolution_warning_minutes": 240,  # 4 ساعت قبل از مهلت
                "escalation_enabled": True,
                "escalation_after_minutes": 720,  # 12 ساعت بعد
                "is_active": True
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for rule_data in sla_rules:
            # Check if rule with this name already exists
            existing_rule = db.query(SLARule).filter(SLARule.name == rule_data["name"]).first()
            if existing_rule:
                print(f"⚠️  SLA rule '{rule_data['name']}' already exists. Skipping...")
                skipped_count += 1
                continue
            
            sla_rule = SLARule(**rule_data)
            db.add(sla_rule)
            print(f"✅ Created SLA rule: {rule_data['name']}")
            print(f"   - زمان پاسخ: {rule_data['response_time_minutes']} دقیقه ({rule_data['response_time_minutes'] // 60 if rule_data['response_time_minutes'] >= 60 else rule_data['response_time_minutes']} {'ساعت' if rule_data['response_time_minutes'] >= 60 else 'دقیقه'})")
            print(f"   - زمان حل: {rule_data['resolution_time_minutes']} دقیقه ({rule_data['resolution_time_minutes'] // 60} ساعت)")
            created_count += 1
        
        db.commit()
        
        print("\n" + "="*60)
        print(f"✅ ایجاد قوانین SLA با موفقیت انجام شد!")
        print(f"   - ایجاد شده: {created_count}")
        if skipped_count > 0:
            print(f"   - رد شده (موجود): {skipped_count}")
        print("="*60)
        print("\n📋 خلاصه قوانین ایجاد شده:")
        print("   🔴 بحرانی: 30 دقیقه پاسخ، 2 ساعت حل")
        print("   🟠 بالا: 1 ساعت پاسخ، 4 ساعت حل")
        print("   🟡 متوسط: 2 ساعت پاسخ، 8 ساعت حل")
        print("   🟢 پایین: 4 ساعت پاسخ، 24 ساعت حل")
        print("\n⏰ ساعت کاری: 9 صبح تا 17 (شنبه تا پنج‌شنبه)")
        print("   ⚠️  توجه: محاسبه ساعت کاری در نسخه‌های بعدی اضافه خواهد شد.")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطا در ایجاد قوانین SLA: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_default_sla_rules()
