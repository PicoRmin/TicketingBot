"""
تست‌های کامل برای تمام سرویس‌ها
Complete unit tests for all services
"""
import pytest
from datetime import datetime, timedelta
from app.services import (
    ticket_service, user_service, branch_service, department_service,
    comment_service, sla_service, custom_field_service, time_tracker_service
)
import asyncio
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.branch import BranchCreate, BranchUpdate
from app.schemas.department import DepartmentCreate
from app.schemas.comment import CommentCreate
from app.schemas.sla import SLARuleCreate, SLARuleUpdate
from app.schemas.custom_field import CustomFieldCreate
from app.core.enums import (
    TicketStatus, TicketPriority, TicketCategory, UserRole, Language,
    CustomFieldType
)


class TestTicketService:
    """تست‌های سرویس تیکت"""
    
    def test_create_ticket(self, db, test_user):
        """تست ایجاد تیکت"""
        ticket_data = TicketCreate(
            title="تیکت تست",
            description="توضیحات تست",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.HIGH
        )
        
        ticket = ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        assert ticket.id is not None
        assert ticket.title == "تیکت تست"
        assert ticket.user_id == test_user.id
        assert ticket.ticket_number.startswith("T-")
        assert ticket.status == TicketStatus.PENDING
    
    def test_get_ticket(self, db, test_ticket):
        """تست دریافت تیکت"""
        ticket = ticket_service.get_ticket(db, test_ticket.id)
        
        assert ticket is not None
        assert ticket.id == test_ticket.id
        assert ticket.ticket_number == test_ticket.ticket_number
    
    def test_get_ticket_not_found(self, db):
        """تست دریافت تیکت ناموجود"""
        ticket = ticket_service.get_ticket(db, 99999)
        assert ticket is None
    
    def test_update_ticket_status(self, db, test_ticket):
        """تست به‌روزرسانی وضعیت تیکت"""
        updated = ticket_service.update_ticket_status(
            db, test_ticket, TicketStatus.IN_PROGRESS
        )
        
        assert updated.status == TicketStatus.IN_PROGRESS
        assert updated.updated_at is not None
    
    def test_assign_ticket(self, db, test_ticket, test_admin):
        """تست تخصیص تیکت"""
        updated = ticket_service.assign_ticket(
            db, test_ticket, test_admin.id
        )
        
        assert updated.assigned_to_id == test_admin.id
        assert updated.status == TicketStatus.IN_PROGRESS
    
    def test_get_all_tickets_with_filters(self, db, test_user):
        """تست دریافت تیکت‌ها با فیلتر"""
        # ایجاد چند تیکت
        for i in range(5):
            ticket_data = TicketCreate(
                title=f"تیکت {i}",
                description=f"توضیحات {i}",
                category=TicketCategory.SOFTWARE,
                priority=TicketPriority.HIGH if i % 2 == 0 else TicketPriority.LOW
            )
            ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # تست بدون فیلتر
        tickets, total = ticket_service.get_all_tickets(db, skip=0, limit=10)
        assert total >= 5
        
        # تست با فیلتر وضعیت
        tickets, total = ticket_service.get_all_tickets(
            db, skip=0, limit=10, status=TicketStatus.PENDING
        )
        assert all(t.status == TicketStatus.PENDING for t in tickets)
        
        # تست با فیلتر اولویت
        tickets, total = ticket_service.get_all_tickets(
            db, skip=0, limit=10, priority=TicketPriority.HIGH
        )
        assert all(t.priority == TicketPriority.HIGH for t in tickets)
        
        # تست با فیلتر دسته‌بندی
        tickets, total = ticket_service.get_all_tickets(
            db, skip=0, limit=10, category=TicketCategory.SOFTWARE
        )
        assert all(t.category == TicketCategory.SOFTWARE for t in tickets)
    
    def test_get_all_tickets_pagination(self, db, test_user):
        """تست Pagination تیکت‌ها"""
        # ایجاد 10 تیکت
        for i in range(10):
            ticket_data = TicketCreate(
                title=f"تیکت {i}",
                description=f"توضیحات {i}",
                category=TicketCategory.SOFTWARE,
                priority=TicketPriority.MEDIUM
            )
            ticket_service.create_ticket(db, ticket_data, test_user.id)
        
        # تست صفحه اول
        tickets, total = ticket_service.get_all_tickets(db, skip=0, limit=5)
        assert len(tickets) == 5
        assert total >= 10
        
        # تست صفحه دوم
        tickets, total = ticket_service.get_all_tickets(db, skip=5, limit=5)
        assert len(tickets) == 5


class TestUserService:
    """تست‌های سرویس کاربر"""
    
    def test_create_user(self, db):
        """تست ایجاد کاربر"""
        user_data = UserCreate(
            username="newuser",
            full_name="کاربر جدید",
            password="password123",
            role=UserRole.USER,
            language=Language.FA
        )
        
        user = user_service.create_user(db, user_data)
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.role == UserRole.USER
        assert user.language == Language.FA
    
    def test_get_user(self, db, test_user):
        """تست دریافت کاربر"""
        user = user_service.get_user(db, test_user.id)
        
        assert user is not None
        assert user.username == "testuser"
        assert user.id == test_user.id
    
    def test_get_user_by_username(self, db, test_user):
        """تست دریافت کاربر با username"""
        user = user_service.get_user_by_username(db, "testuser")
        
        assert user is not None
        assert user.username == "testuser"
    
    def test_update_user(self, db, test_user):
        """تست به‌روزرسانی کاربر"""
        user_data = UserUpdate(
            full_name="نام جدید",
            language=Language.EN
        )
        
        updated = user_service.update_user(db, test_user, user_data)
        
        assert updated.full_name == "نام جدید"
        assert updated.language == Language.EN


class TestBranchService:
    """تست‌های سرویس شعبه"""
    
    def test_create_branch(self, db):
        """تست ایجاد شعبه"""
        branch_data = BranchCreate(
            name="شعبه جدید",
            name_en="New Branch",
            code="NEW",
            is_active=True
        )
        
        branch = branch_service.create_branch(db, branch_data)
        
        assert branch.id is not None
        assert branch.name == "شعبه جدید"
        assert branch.code == "NEW"
        assert branch.is_active is True
    
    def test_get_branch(self, db, test_branch):
        """تست دریافت شعبه"""
        branch = branch_service.get_branch(db, test_branch.id)
        
        assert branch is not None
        assert branch.id == test_branch.id
        assert branch.name == "شعبه تست"
    
    def test_list_branches(self, db):
        """تست لیست شعب"""
        # ایجاد چند شعبه
        for i in range(3):
            branch_data = BranchCreate(
                name=f"شعبه {i}",
                name_en=f"Branch {i}",
                code=f"BR{i}",
                is_active=True
            )
            branch_service.create_branch(db, branch_data)
        
        branches = branch_service.list_branches(db)
        assert len(branches) >= 3


class TestDepartmentService:
    """تست‌های سرویس دپارتمان"""
    
    def test_create_department(self, db):
        """تست ایجاد دپارتمان"""
        dept_data = DepartmentCreate(
            name="دپارتمان جدید",
            code="NEW-DEPT",
            is_active=True
        )
        
        dept = department_service.create_department(db, dept_data)
        
        assert dept.id is not None
        assert dept.name == "دپارتمان جدید"
        assert dept.code == "NEW-DEPT"
    
    def test_get_department(self, db, test_department):
        """تست دریافت دپارتمان"""
        dept = department_service.get_department(db, test_department.id)
        
        assert dept is not None
        assert dept.id == test_department.id


class TestCommentService:
    """تست‌های سرویس کامنت"""
    
    def test_create_comment(self, db, test_user, test_ticket):
        """تست ایجاد کامنت"""
        comment_data = CommentCreate(
            ticket_id=test_ticket.id,
            comment="این یک کامنت تست است",
            is_internal=False
        )
        
        comment = comment_service.create_comment(db, test_user.id, comment_data)
        
        assert comment.id is not None
        assert comment.comment == "این یک کامنت تست است"
        assert comment.ticket_id == test_ticket.id
        assert comment.user_id == test_user.id
        assert comment.is_internal is False
    
    def test_get_ticket_comments(self, db, test_user, test_ticket):
        """تست دریافت کامنت‌های تیکت"""
        import asyncio
        # ایجاد چند کامنت
        for i in range(3):
            comment_data = CommentCreate(
                ticket_id=test_ticket.id,
                comment=f"کامنت {i}",
                is_internal=False
            )
            asyncio.run(comment_service.create_comment(db, test_user.id, comment_data))
        
        comments = comment_service.list_ticket_comments(db, test_ticket.id)
        assert len(comments) >= 3


class TestSLAService:
    """تست‌های سرویس SLA"""
    
    def test_create_sla_rule(self, db):
        """تست ایجاد قانون SLA"""
        sla_data = SLARuleCreate(
            name="SLA تست",
            description="قانون SLA برای تست",
            priority=TicketPriority.HIGH,
            response_time_minutes=60,
            resolution_time_minutes=240,
            is_active=True
        )
        
        sla_rule = sla_service.create_sla_rule(db, sla_data)
        
        assert sla_rule.id is not None
        assert sla_rule.name == "SLA تست"
        assert sla_rule.response_time_minutes == 60
        assert sla_rule.is_active is True
    
    def test_find_matching_sla_rule(self, db):
        """تست یافتن قانون SLA مناسب"""
        # ایجاد قانون SLA
        sla_data = SLARuleCreate(
            name="SLA اولویت بالا",
            priority=TicketPriority.HIGH,
            response_time_minutes=30,
            resolution_time_minutes=120,
            is_active=True
        )
        sla_rule = sla_service.create_sla_rule(db, sla_data)
        
        # جستجوی قانون مناسب
        found = sla_service.find_matching_sla_rule(
            db,
            TicketPriority.HIGH,
            TicketCategory.SOFTWARE
        )
        
        assert found is not None
        assert found.id == sla_rule.id
    
    def test_create_sla_log(self, db, test_ticket):
        """تست ایجاد لاگ SLA"""
        # ایجاد قانون SLA
        sla_data = SLARuleCreate(
            name="SLA تست",
            response_time_minutes=60,
            resolution_time_minutes=240,
            is_active=True
        )
        sla_rule = sla_service.create_sla_rule(db, sla_data)
        
        # ایجاد لاگ
        sla_log = sla_service.create_sla_log(db, test_ticket, sla_rule)
        
        assert sla_log.id is not None
        assert sla_log.ticket_id == test_ticket.id
        assert sla_log.sla_rule_id == sla_rule.id
        assert sla_log.target_response_time is not None
        assert sla_log.target_resolution_time is not None
    
    def test_list_sla_logs(self, db, test_ticket):
        """تست لیست لاگ‌های SLA"""
        # ایجاد چند لاگ
        sla_data = SLARuleCreate(
            name="SLA تست",
            response_time_minutes=60,
            resolution_time_minutes=240,
            is_active=True
        )
        sla_rule = sla_service.create_sla_rule(db, sla_data)
        
        for i in range(3):
            sla_log = sla_service.create_sla_log(db, test_ticket, sla_rule)
            sla_log.response_status = "on_time" if i % 2 == 0 else "warning"
            db.commit()
        
        # تست لیست بدون فیلتر
        logs, total = sla_service.list_sla_logs(db, skip=0, limit=10)
        assert total >= 3
        
        # تست با فیلتر وضعیت
        logs, total = sla_service.list_sla_logs(
            db, skip=0, limit=10, response_status="on_time"
        )
        assert all(log.response_status == "on_time" for log in logs)


class TestCustomFieldService:
    """تست‌های سرویس فیلدهای سفارشی"""
    
    def test_create_custom_field(self, db):
        """تست ایجاد فیلد سفارشی"""
        field_data = CustomFieldCreate(
            name="test_field",
            label="فیلد تست",
            field_type=CustomFieldType.TEXT,
            category=TicketCategory.SOFTWARE,
            is_required=True,
            is_active=True
        )
        
        field = custom_field_service.create_custom_field(db, field_data)
        
        assert field.id is not None
        assert field.name == "test_field"
        assert field.field_type == CustomFieldType.TEXT
        assert field.is_required is True
    
    def test_get_custom_fields_for_ticket(self, db, test_ticket):
        """تست دریافت فیلدهای سفارشی برای تیکت"""
        # ایجاد فیلد سفارشی
        field_data = CustomFieldCreate(
            name="test_field",
            label="فیلد تست",
            field_type=CustomFieldType.TEXT,
            category=test_ticket.category,
            is_active=True
        )
        field = custom_field_service.create_custom_field(db, field_data)
        
        # دریافت فیلدهای مناسب برای تیکت
        fields = custom_field_service.get_custom_fields_for_ticket(db, test_ticket)
        
        assert len(fields) >= 1
        assert any(f.id == field.id for f in fields)


class TestTimeTrackerService:
    """تست‌های سرویس Time Tracker"""
    
    def test_start_time_log(self, db, test_user, test_ticket):
        """تست شروع ثبت زمان"""
        time_log = time_tracker_service.start_time_log(
            db, test_ticket.id, test_user.id, "شروع کار"
        )
        
        assert time_log.id is not None
        assert time_log.ticket_id == test_ticket.id
        assert time_log.user_id == test_user.id
        assert time_log.start_time is not None
        assert time_log.end_time is None
    
    def test_stop_time_log(self, db, test_user, test_ticket):
        """تست توقف ثبت زمان"""
        # شروع
        time_log = time_tracker_service.start_time_log(
            db, test_ticket.id, test_user.id, "شروع کار"
        )
        
        # توقف
        stopped = time_tracker_service.stop_time_log(db, time_log.id)
        
        assert stopped.end_time is not None
        assert stopped.duration_minutes is not None
        assert stopped.duration_minutes > 0
    
    def test_get_ticket_time_logs(self, db, test_user, test_ticket):
        """تست دریافت لاگ‌های زمان تیکت"""
        # ایجاد چند لاگ
        for i in range(3):
            time_tracker_service.start_time_log(
                db, test_ticket.id, test_user.id, f"کار {i}"
            )
        
        logs = time_tracker_service.get_ticket_time_logs(db, test_ticket.id)
        assert len(logs) >= 3

