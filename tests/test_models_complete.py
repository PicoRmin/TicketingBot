"""
تست‌های کامل برای تمام مدل‌های دیتابیس
Complete unit tests for all database models
"""
import pytest
from datetime import datetime, timedelta
from app.models import (
    User, Ticket, Branch, Department, Attachment, Comment,
    TicketHistory, RefreshToken, SystemSettings, BranchInfrastructure,
    SLARule, SLALog, AutomationRule, TimeLog, CustomField, TicketCustomFieldValue
)
from app.core.enums import (
    UserRole, Language, TicketCategory, TicketStatus, TicketPriority,
    CustomFieldType
)
from app.core.security import get_password_hash, verify_password


class TestUserModel:
    """تست‌های مدل User"""
    
    def test_user_creation(self, db):
        """تست ایجاد کاربر"""
        user = User(
            username="testuser",
            full_name="کاربر تست",
            password_hash=get_password_hash("testpass123"),
            role=UserRole.USER,
            language=Language.FA,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.full_name == "کاربر تست"
        assert user.role == UserRole.USER
        assert user.language == Language.FA
        assert user.is_active is True
        assert verify_password("testpass123", user.password_hash)
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_email(self, db):
        """تست فیلد email کاربر"""
        user = User(
            username="emailuser",
            full_name="کاربر ایمیل",
            password_hash=get_password_hash("pass123"),
            role=UserRole.USER,
            email="test@example.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.email == "test@example.com"
    
    def test_user_telegram_chat_id(self, db):
        """تست فیلد telegram_chat_id"""
        user = User(
            username="telegramuser",
            full_name="کاربر تلگرام",
            password_hash=get_password_hash("pass123"),
            role=UserRole.USER,
            telegram_chat_id="123456789"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.telegram_chat_id == "123456789"
    
    def test_user_branch_relationship(self, db, test_branch):
        """تست رابطه کاربر با شعبه"""
        user = User(
            username="branchuser",
            full_name="کاربر شعبه",
            password_hash=get_password_hash("pass123"),
            role=UserRole.USER,
            branch_id=test_branch.id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.branch_id == test_branch.id
        assert user.branch.id == test_branch.id
        assert user in test_branch.users
    
    def test_user_department_relationship(self, db, test_department):
        """تست رابطه کاربر با دپارتمان"""
        user = User(
            username="deptuser",
            full_name="کاربر دپارتمان",
            password_hash=get_password_hash("pass123"),
            role=UserRole.USER,
            department_id=test_department.id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.department_id == test_department.id
        assert user.department.id == test_department.id


class TestTicketModel:
    """تست‌های مدل Ticket"""
    
    def test_ticket_creation(self, db, test_user):
        """تست ایجاد تیکت"""
        ticket = Ticket(
            ticket_number="T-20250123-0001",
            title="تیکت تست",
            description="توضیحات تیکت تست",
            category=TicketCategory.SOFTWARE,
            status=TicketStatus.PENDING,
            priority=TicketPriority.HIGH,
            user_id=test_user.id
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        assert ticket.id is not None
        assert ticket.ticket_number == "T-20250123-0001"
        assert ticket.title == "تیکت تست"
        assert ticket.category == TicketCategory.SOFTWARE
        assert ticket.status == TicketStatus.PENDING
        assert ticket.priority == TicketPriority.HIGH
        assert ticket.user_id == test_user.id
        assert ticket.created_at is not None
    
    def test_ticket_user_relationship(self, db, test_user):
        """تست رابطه تیکت با کاربر"""
        ticket = Ticket(
            ticket_number="T-20250123-0002",
            title="تیکت تست 2",
            description="توضیحات",
            category=TicketCategory.INTERNET,
            status=TicketStatus.PENDING,
            priority=TicketPriority.MEDIUM,
            user_id=test_user.id
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        assert ticket.user.id == test_user.id
        assert ticket in test_user.tickets
    
    def test_ticket_assigned_to_relationship(self, db, test_user, test_admin):
        """تست رابطه تیکت با کارشناس مسئول"""
        ticket = Ticket(
            ticket_number="T-20250123-0003",
            title="تیکت تست 3",
            description="توضیحات",
            category=TicketCategory.EQUIPMENT,
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.CRITICAL,
            user_id=test_user.id,
            assigned_to_id=test_admin.id
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        assert ticket.assigned_to_id == test_admin.id
        assert ticket.assigned_to.id == test_admin.id
    
    def test_ticket_branch_relationship(self, db, test_user, test_branch):
        """تست رابطه تیکت با شعبه"""
        ticket = Ticket(
            ticket_number="T-20250123-0004",
            title="تیکت تست 4",
            description="توضیحات",
            category=TicketCategory.OTHER,
            status=TicketStatus.PENDING,
            priority=TicketPriority.LOW,
            user_id=test_user.id,
            branch_id=test_branch.id
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        assert ticket.branch_id == test_branch.id
        assert ticket.branch.id == test_branch.id
    
    def test_ticket_status_transitions(self, db, test_user):
        """تست تغییر وضعیت تیکت"""
        ticket = Ticket(
            ticket_number="T-20250123-0005",
            title="تیکت تست 5",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            status=TicketStatus.PENDING,
            priority=TicketPriority.MEDIUM,
            user_id=test_user.id
        )
        db.add(ticket)
        db.commit()
        
        # تغییر به IN_PROGRESS
        ticket.status = TicketStatus.IN_PROGRESS
        db.commit()
        db.refresh(ticket)
        assert ticket.status == TicketStatus.IN_PROGRESS
        
        # تغییر به RESOLVED
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)
        assert ticket.status == TicketStatus.RESOLVED
        assert ticket.resolved_at is not None
        
        # تغییر به CLOSED
        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)
        assert ticket.status == TicketStatus.CLOSED
        assert ticket.closed_at is not None


class TestSLAModel:
    """تست‌های مدل‌های SLA"""
    
    def test_sla_rule_creation(self, db):
        """تست ایجاد قانون SLA"""
        sla_rule = SLARule(
            name="SLA تست",
            description="قانون SLA برای تست",
            priority=TicketPriority.HIGH,
            category=TicketCategory.SOFTWARE,
            response_time_minutes=60,
            resolution_time_minutes=240,
            response_warning_minutes=30,
            resolution_warning_minutes=60,
            escalation_enabled=True,
            escalation_after_minutes=120,
            is_active=True
        )
        db.add(sla_rule)
        db.commit()
        db.refresh(sla_rule)
        
        assert sla_rule.id is not None
        assert sla_rule.name == "SLA تست"
        assert sla_rule.response_time_minutes == 60
        assert sla_rule.escalation_enabled is True
        assert sla_rule.is_active is True
    
    def test_sla_log_creation(self, db, test_ticket):
        """تست ایجاد لاگ SLA"""
        # ابتدا یک قانون SLA ایجاد می‌کنیم
        sla_rule = SLARule(
            name="SLA تست",
            response_time_minutes=60,
            resolution_time_minutes=240,
            is_active=True
        )
        db.add(sla_rule)
        db.commit()
        db.refresh(sla_rule)
        
        # ایجاد لاگ SLA
        target_response = datetime.utcnow() + timedelta(minutes=60)
        target_resolution = datetime.utcnow() + timedelta(minutes=240)
        
        sla_log = SLALog(
            ticket_id=test_ticket.id,
            sla_rule_id=sla_rule.id,
            target_response_time=target_response,
            target_resolution_time=target_resolution,
            response_status="on_time",
            resolution_status="warning"
        )
        db.add(sla_log)
        db.commit()
        db.refresh(sla_log)
        
        assert sla_log.id is not None
        assert sla_log.ticket_id == test_ticket.id
        assert sla_log.sla_rule_id == sla_rule.id
        assert sla_log.response_status == "on_time"
        assert sla_log.resolution_status == "warning"
        assert sla_log.escalated is False
    
    def test_sla_log_relationships(self, db, test_ticket):
        """تست روابط لاگ SLA"""
        sla_rule = SLARule(
            name="SLA تست",
            response_time_minutes=60,
            resolution_time_minutes=240,
            is_active=True
        )
        db.add(sla_rule)
        db.commit()
        db.refresh(sla_rule)
        
        target_response = datetime.utcnow() + timedelta(minutes=60)
        target_resolution = datetime.utcnow() + timedelta(minutes=240)
        
        sla_log = SLALog(
            ticket_id=test_ticket.id,
            sla_rule_id=sla_rule.id,
            target_response_time=target_response,
            target_resolution_time=target_resolution
        )
        db.add(sla_log)
        db.commit()
        db.refresh(sla_log)
        
        assert sla_log.ticket.id == test_ticket.id
        assert sla_log.sla_rule.id == sla_rule.id
        assert sla_log in test_ticket.sla_logs
        assert sla_log in sla_rule.sla_logs


class TestCustomFieldModel:
    """تست‌های مدل Custom Field"""
    
    def test_custom_field_creation(self, db):
        """تست ایجاد فیلد سفارشی"""
        custom_field = CustomField(
            name="test_field",
            label="فیلد تست",
            label_en="Test Field",
            field_type=CustomFieldType.TEXT,
            description="توضیحات فیلد تست",
            category=TicketCategory.SOFTWARE,
            is_required=True,
            is_visible_to_user=True,
            is_editable_by_user=True,
            display_order=1,
            is_active=True
        )
        db.add(custom_field)
        db.commit()
        db.refresh(custom_field)
        
        assert custom_field.id is not None
        assert custom_field.name == "test_field"
        assert custom_field.field_type == CustomFieldType.TEXT
        assert custom_field.is_required is True
        assert custom_field.is_active is True
    
    def test_custom_field_with_config(self, db):
        """تست فیلد سفارشی با تنظیمات"""
        config = {
            "options": [
                {"value": "opt1", "label": "گزینه 1"},
                {"value": "opt2", "label": "گزینه 2"}
            ]
        }
        
        custom_field = CustomField(
            name="select_field",
            label="فیلد انتخاب",
            field_type=CustomFieldType.SELECT,
            config=config,
            is_active=True
        )
        db.add(custom_field)
        db.commit()
        db.refresh(custom_field)
        
        assert custom_field.config == config
        assert len(custom_field.config["options"]) == 2
    
    def test_ticket_custom_field_value(self, db, test_ticket):
        """تست مقدار فیلد سفارشی تیکت"""
        # ایجاد فیلد سفارشی
        custom_field = CustomField(
            name="test_field",
            label="فیلد تست",
            field_type=CustomFieldType.TEXT,
            is_active=True
        )
        db.add(custom_field)
        db.commit()
        db.refresh(custom_field)
        
        # ایجاد مقدار
        value = TicketCustomFieldValue(
            ticket_id=test_ticket.id,
            custom_field_id=custom_field.id,
            value="مقدار تست"
        )
        db.add(value)
        db.commit()
        db.refresh(value)
        
        assert value.id is not None
        assert value.ticket_id == test_ticket.id
        assert value.custom_field_id == custom_field.id
        assert value.value == "مقدار تست"


class TestCommentModel:
    """تست‌های مدل Comment"""
    
    def test_comment_creation(self, db, test_user, test_ticket):
        """تست ایجاد کامنت"""
        comment = Comment(
            ticket_id=test_ticket.id,
            user_id=test_user.id,
            comment="این یک کامنت تست است",
            is_internal=False
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        assert comment.id is not None
        assert comment.comment == "این یک کامنت تست است"
        assert comment.is_internal is False
        assert comment.ticket_id == test_ticket.id
        assert comment.user_id == test_user.id
    
    def test_comment_relationships(self, db, test_user, test_ticket):
        """تست روابط کامنت"""
        comment = Comment(
            ticket_id=test_ticket.id,
            user_id=test_user.id,
            comment="کامنت تست",
            is_internal=False
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        assert comment.ticket.id == test_ticket.id
        assert comment.user.id == test_user.id
        assert comment in test_ticket.comments
        assert comment in test_user.comments


class TestTimeLogModel:
    """تست‌های مدل TimeLog"""
    
    def test_time_log_creation(self, db, test_user, test_ticket):
        """تست ایجاد لاگ زمان"""
        time_log = TimeLog(
            ticket_id=test_ticket.id,
            user_id=test_user.id,
            start_time=datetime.utcnow(),
            duration_minutes=30,
            description="کار روی تیکت"
        )
        db.add(time_log)
        db.commit()
        db.refresh(time_log)
        
        assert time_log.id is not None
        assert time_log.ticket_id == test_ticket.id
        assert time_log.user_id == test_user.id
        assert time_log.duration_minutes == 30
        assert time_log.description == "کار روی تیکت"
        assert time_log.start_time is not None


class TestAutomationRuleModel:
    """تست‌های مدل AutomationRule"""
    
    def test_automation_rule_creation(self, db):
        """تست ایجاد قانون اتوماسیون"""
        automation_rule = AutomationRule(
            name="قانون تست",
            description="قانون اتوماسیون تست",
            is_active=True,
            conditions={"status": "pending"},
            actions={"assign_to": 1}
        )
        db.add(automation_rule)
        db.commit()
        db.refresh(automation_rule)
        
        assert automation_rule.id is not None
        assert automation_rule.name == "قانون تست"
        assert automation_rule.is_active is True
        assert automation_rule.conditions == {"status": "pending"}
        assert automation_rule.actions == {"assign_to": 1}


class TestBranchInfrastructureModel:
    """تست‌های مدل BranchInfrastructure"""
    
    def test_branch_infrastructure_creation(self, db, test_branch):
        """تست ایجاد زیرساخت شعبه"""
        infrastructure = BranchInfrastructure(
            branch_id=test_branch.id,
            infrastructure_type="internet",
            name="اینترنت",
            description="اتصال اینترنت شعبه",
            status="active"
        )
        db.add(infrastructure)
        db.commit()
        db.refresh(infrastructure)
        
        assert infrastructure.id is not None
        assert infrastructure.branch_id == test_branch.id
        assert infrastructure.infrastructure_type == "internet"
        assert infrastructure.status == "active"


class TestSystemSettingsModel:
    """تست‌های مدل SystemSettings"""
    
    def test_system_settings_creation(self, db):
        """تست ایجاد تنظیمات سیستم"""
        settings = SystemSettings(
            key="test_setting",
            value="test_value",
            description="تنظیمات تست"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
        assert settings.id is not None
        assert settings.key == "test_setting"
        assert settings.value == "test_value"
        assert settings.description == "تنظیمات تست"

