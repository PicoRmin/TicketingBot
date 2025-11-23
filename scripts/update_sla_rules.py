"""
Script to update or recreate SLA rules based on new requirements
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

def update_sla_rules():
    """Update or recreate SLA rules based on new requirements"""
    db = SessionLocal()
    
    try:
        # New SLA rules based on requirements
        # ساعت کاری: 9 صبح تا 17 (شنبه تا پنج‌شنبه)
        # حداقل تایم: 30 دقیقه
        # حداکثر تایم: 24 ساعت (1440 دقیقه)
        
        new_sla_rules = [
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
        
        # Get existing rules
        existing_rules = db.query(SLARule).all()
        existing_names = {rule.name for rule in existing_rules}
        
        updated_count = 0
        created_count = 0
        deleted_count = 0
        
        # Update or create rules
        for rule_data in new_sla_rules:
            existing_rule = db.query(SLARule).filter(SLARule.name == rule_data["name"]).first()
            
            if existing_rule:
                # Update existing rule
                for key, value in rule_data.items():
                    if key != "name":  # Don't update name
                        setattr(existing_rule, key, value)
                print(f"✅ Updated SLA rule: {rule_data['name']}")
                updated_count += 1
            else:
                # Create new rule
                sla_rule = SLARule(**rule_data)
                db.add(sla_rule)
                print(f"✅ Created SLA rule: {rule_data['name']}")
                created_count += 1
        
        # Delete old rules that are not in the new list
        new_names = {rule["name"] for rule in new_sla_rules}
        for existing_rule in existing_rules:
            if existing_rule.name not in new_names:
                print(f"🗑️  Deleting old SLA rule: {existing_rule.name}")
                db.delete(existing_rule)
                deleted_count += 1
        
        db.commit()
        
        print("\n" + "="*60)
        print(f"✅ به‌روزرسانی قوانین SLA با موفقیت انجام شد!")
        print(f"   - به‌روزرسانی شده: {updated_count}")
        print(f"   - ایجاد شده: {created_count}")
        if deleted_count > 0:
            print(f"   - حذف شده: {deleted_count}")
        print("="*60)
        print("\n📋 خلاصه قوانین:")
        print("   🔴 بحرانی: 30 دقیقه پاسخ، 2 ساعت حل")
        print("   🟠 بالا: 1 ساعت پاسخ، 4 ساعت حل")
        print("   🟡 متوسط: 2 ساعت پاسخ، 8 ساعت حل")
        print("   🟢 پایین: 4 ساعت پاسخ، 24 ساعت حل")
        print("\n⏰ ساعت کاری: 9 صبح تا 17 (شنبه تا پنج‌شنبه)")
        print("   ⚠️  توجه: محاسبه ساعت کاری در نسخه‌های بعدی اضافه خواهد شد.")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطا در به‌روزرسانی قوانین SLA: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_sla_rules()

