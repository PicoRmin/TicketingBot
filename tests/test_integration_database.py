"""
تست‌های یکپارچه‌سازی برای عملیات دیتابیس
Integration tests for database operations
"""
import pytest
from sqlalchemy.orm import Session
from app.models import (
    User, Ticket, Branch, Department, Comment, Attachment,
    TicketHistory, SLARule, SLALog, CustomField, TicketCustomFieldValue,
    TimeLog, AutomationRule
)
from app.core.enums import (
    UserRole, Language, TicketCategory, TicketStatus, TicketPriority,
    CustomFieldType
)
from app.services import (
    ticket_service, user_service, branch_service, department_service,
    sla_service, custom_field_service, time_tracker_service
)
import asyncio
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.schemas.user import UserCreate
from app.schemas.branch import BranchCreate
from app.schemas.comment import CommentCreate
from app.schemas.sla import SLARuleCreate
from app.schemas.custom_field import CustomFieldCreate
from datetime import datetime, timedelta


class TestDatabaseTransactions:
    """تست‌های تراکنش‌های دیتابیس"""
    
    def test_create_ticket_with_sla(self, db, test_user):
        """تست ایجاد تیکت با SLA"""
        # ایجاد قانون SLA
        sla_data = SLARuleCreate(
            name="SLA تست",
            priority=TicketPriority.HIGH,
            category=TicketCategory.SOFTWARE,
            response_time_minutes=60,
            resolution_time_minutes=240,
            is_active=True
        )
        sla_rule = sla_service.create_sla_rule(db, sla_data)
        
        # ایجاد تیکت
        ticket_data = TicketCreate(
            title="تیکت تست",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.HIGH
        )
        ticket = ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # بررسی ایجاد لاگ SLA
        sla_log = sla_service.get_ticket_sla_log(db, ticket.id)
        assert sla_log is not None
        assert sla_log.sla_rule_id == sla_rule.id
        assert sla_log.ticket_id == ticket.id
    
    def test_ticket_status_history(self, db, test_user):
        """تست تاریخچه تغییر وضعیت تیکت"""
        # ایجاد تیکت
        ticket_data = TicketCreate(
            title="تیکت تست",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.MEDIUM
        )
        ticket = ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # تغییر وضعیت
        ticket_service.update_ticket_status(db, ticket, TicketStatus.IN_PROGRESS)
        
        # بررسی تاریخچه
        from app.services.ticket_history_service import get_ticket_history
        history = get_ticket_history(db, ticket.id)
        assert len(history) >= 1
        assert any(h.status == TicketStatus.IN_PROGRESS.value for h in history)
    
    def test_ticket_with_comments(self, db, test_user):
        """تست تیکت با کامنت‌ها"""
        # ایجاد تیکت
        ticket_data = TicketCreate(
            title="تیکت تست",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.MEDIUM
        )
        ticket = ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # ایجاد چند کامنت
        from app.services import comment_service
        for i in range(3):
            comment_data = CommentCreate(
                ticket_id=ticket.id,
                comment=f"کامنت {i}",
                is_internal=False
            )
            asyncio.run(comment_service.create_comment(db, test_user.id, comment_data))
        
        # بررسی کامنت‌ها
        comments = comment_service.list_ticket_comments(db, ticket.id)
        assert len(comments) == 3
    
    def test_ticket_with_custom_fields(self, db, test_user):
        """تست تیکت با فیلدهای سفارشی"""
        # ایجاد فیلد سفارشی
        field_data = CustomFieldCreate(
            name="test_field",
            label="فیلد تست",
            field_type=CustomFieldType.TEXT,
            category=TicketCategory.SOFTWARE,
            is_active=True
        )
        custom_field = custom_field_service.create_custom_field(db, field_data)
        
        # ایجاد تیکت
        ticket_data = TicketCreate(
            title="تیکت تست",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.MEDIUM
        )
        ticket = ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # تنظیم مقدار فیلد سفارشی
        from app.services.custom_field_service import set_ticket_custom_field_value
        value = set_ticket_custom_field_value(
            db, ticket.id, custom_field.id, "مقدار تست"
        )
        
        assert value is not None
        assert value.value == "مقدار تست"
        assert value.ticket_id == ticket.id
        assert value.custom_field_id == custom_field.id
    
    def test_user_with_branch_and_department(self, db):
        """تست کاربر با شعبه و دپارتمان"""
        # ایجاد شعبه
        branch_data = BranchCreate(
            name="شعبه تست",
            name_en="Test Branch",
            code="TEST",
            is_active=True
        )
        branch = branch_service.create_branch(db, branch_data)
        
        # ایجاد دپارتمان
        dept_data = DepartmentCreate(
            name="دپارتمان تست",
            code="TEST-DEPT",
            is_active=True
        )
        dept = department_service.create_department(db, dept_data)
        
        # ایجاد کاربر
        user_data = UserCreate(
            username="testuser",
            full_name="کاربر تست",
            password="pass123",
            role=UserRole.USER,
            language=Language.FA
        )
        user = user_service.create_user(db, user_data)
        
        # تخصیص شعبه و دپارتمان
        from app.services.user_service import update_user
        from app.schemas.user import UserUpdate
        user_update = UserUpdate(branch_id=branch.id, department_id=dept.id)
        updated_user = user_service.update_user(db, user, user_update)
        
        assert updated_user.branch_id == branch.id
        assert updated_user.department_id == dept.id
        assert updated_user.branch.id == branch.id
        assert updated_user.department.id == dept.id
    
    def test_ticket_assignment_flow(self, db, test_user, test_admin):
        """تست جریان تخصیص تیکت"""
        # ایجاد تیکت
        ticket_data = TicketCreate(
            title="تیکت تست",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.HIGH
        )
        ticket = ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # تخصیص تیکت
        ticket_service.assign_ticket(db, ticket, test_admin.id)
        
        # بررسی
        assert ticket.assigned_to_id == test_admin.id
        assert ticket.status == TicketStatus.IN_PROGRESS
        
        # بررسی تاریخچه
        from app.services.ticket_history_service import get_ticket_history
        history = get_ticket_history(db, ticket.id)
        assert any(h.status == TicketStatus.IN_PROGRESS.value for h in history)
    
    def test_time_tracking_flow(self, db, test_user):
        """تست جریان ثبت زمان"""
        # ایجاد تیکت
        ticket_data = TicketCreate(
            title="تیکت تست",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.MEDIUM
        )
        ticket = ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # شروع ثبت زمان
        time_log = time_tracker_service.start_time_log(
            db, ticket.id, test_user.id, "شروع کار"
        )
        
        assert time_log.id is not None
        assert time_log.ticket_id == ticket.id
        assert time_log.user_id == test_user.id
        assert time_log.start_time is not None
        assert time_log.end_time is None
        
        # توقف ثبت زمان
        stopped = time_tracker_service.stop_time_log(db, time_log.id)
        
        assert stopped.end_time is not None
        assert stopped.duration_minutes is not None
        assert stopped.duration_minutes > 0
        
        # بررسی لاگ‌های زمان تیکت
        logs = time_tracker_service.get_ticket_time_logs(db, ticket.id)
        assert len(logs) >= 1
        assert any(log.id == time_log.id for log in logs)


class TestDatabaseRelationships:
    """تست‌های روابط دیتابیس"""
    
    def test_user_tickets_relationship(self, db, test_user):
        """تست رابطه کاربر با تیکت‌ها"""
        # ایجاد چند تیکت
        for i in range(5):
            ticket_data = TicketCreate(
                title=f"تیکت {i}",
                description=f"توضیحات {i}",
                category=TicketCategory.SOFTWARE,
                priority=TicketPriority.MEDIUM
            )
            ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # بررسی روابط
        db.refresh(test_user)
        assert len(test_user.tickets) >= 5
        assert all(t.user_id == test_user.id for t in test_user.tickets)
    
    def test_ticket_comments_relationship(self, db, test_user, test_ticket):
        """تست رابطه تیکت با کامنت‌ها"""
        # ایجاد چند کامنت
        from app.services import comment_service
        for i in range(3):
            comment_data = CommentCreate(
                ticket_id=test_ticket.id,
                comment=f"کامنت {i}",
                is_internal=False
            )
            asyncio.run(comment_service.create_comment(db, test_user.id, comment_data))
        
        # بررسی روابط
        db.refresh(test_ticket)
        assert len(test_ticket.comments) == 3
        assert all(c.ticket_id == test_ticket.id for c in test_ticket.comments)
    
    def test_branch_users_relationship(self, db, test_branch):
        """تست رابطه شعبه با کاربران"""
        # ایجاد چند کاربر
        for i in range(3):
            user_data = UserCreate(
                username=f"user{i}",
                full_name=f"کاربر {i}",
                password="pass123",
                role=UserRole.USER,
                language=Language.FA
            )
            user = user_service.create_user(db, user_data)
            from app.services.user_service import update_user
            from app.schemas.user import UserUpdate
            user_service.update_user(db, user, UserUpdate(branch_id=test_branch.id))
        
        # بررسی روابط
        db.refresh(test_branch)
        assert len(test_branch.users) >= 3
        assert all(u.branch_id == test_branch.id for u in test_branch.users)


class TestDatabaseConstraints:
    """تست‌های محدودیت‌های دیتابیس"""
    
    def test_unique_username(self, db):
        """تست یکتایی username"""
        user_data1 = UserCreate(
            username="testuser",
            full_name="کاربر 1",
            password="pass123",
            role=UserRole.USER,
            language=Language.FA
        )
        user1 = user_service.create_user(db, user_data1)
        
        # تلاش برای ایجاد کاربر با username تکراری
        user_data2 = UserCreate(
            username="testuser",
            full_name="کاربر 2",
            password="pass123",
            role=UserRole.USER,
            language=Language.FA
        )
        
        with pytest.raises(Exception):  # باید خطا بدهد
            user_service.create_user(db, user_data2)
    
    def test_foreign_key_constraints(self, db, test_user):
        """تست محدودیت‌های Foreign Key"""
        # تلاش برای ایجاد تیکت با user_id نامعتبر
        ticket = Ticket(
            ticket_number="T-20250123-0001",
            title="تیکت تست",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            status=TicketStatus.PENDING,
            priority=TicketPriority.MEDIUM,
            user_id=99999  # کاربر نامعتبر
        )
        
        db.add(ticket)
        with pytest.raises(Exception):  # باید خطا بدهد
            db.commit()


class TestDatabaseCascades:
    """تست‌های Cascade در دیتابیس"""
    
    def test_delete_user_cascades_tickets(self, db, test_user):
        """تست حذف کاربر و تیکت‌های مرتبط"""
        # ایجاد چند تیکت
        for i in range(3):
            ticket_data = TicketCreate(
                title=f"تیکت {i}",
                description=f"توضیحات {i}",
                category=TicketCategory.SOFTWARE,
                priority=TicketPriority.MEDIUM
            )
            ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # شمارش تیکت‌ها قبل از حذف
        tickets_before = db.query(Ticket).filter(Ticket.user_id == test_user.id).count()
        assert tickets_before == 3
        
        # حذف کاربر
        db.delete(test_user)
        db.commit()
        
        # بررسی حذف تیکت‌ها
        tickets_after = db.query(Ticket).filter(Ticket.user_id == test_user.id).count()
        assert tickets_after == 0

