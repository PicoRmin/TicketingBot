"""
تست‌های یکپارچه‌سازی برای عملیات فایل
Integration tests for file operations
"""
import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db, SessionLocal
from app.core.enums import UserRole, Language
from app.core.security import create_access_token
from app.models import User, Ticket, Attachment
from app.services import user_service, ticket_service
from app.schemas.user import UserCreate
from app.schemas.ticket import TicketCreate
from app.core.enums import TicketCategory, TicketPriority
import io

# Override get_db dependency for testing
def override_get_db():
    """Override get_db for testing"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_with_token(test_db):
    """Create a test user and return access token"""
    user_data = UserCreate(
        username="filetest",
        full_name="File Test User",
        password="testpass123",
        role=UserRole.USER,
        language=Language.FA
    )
    user = user_service.create_user(test_db, user_data)
    
    token = create_access_token(data={"sub": user.username, "user_id": user.id, "role": user.role.value})
    return token, user


@pytest.fixture
def test_ticket_for_file(test_db, test_user_with_token):
    """Create a test ticket for file operations"""
    token, user = test_user_with_token
    ticket_data = TicketCreate(
        title="تیکت تست فایل",
        description="توضیحات",
        category=TicketCategory.SOFTWARE,
        priority=TicketPriority.MEDIUM
    )
    ticket = ticket_service.create_ticket(test_db, ticket_data, user.id)
    return ticket, token, user


@pytest.fixture
def temp_storage_dir():
    """Create a temporary storage directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestFileUpload:
    """تست‌های آپلود فایل"""
    
    def test_upload_file_success(self, test_user_with_token, test_ticket_for_file):
        """تست آپلود موفق فایل"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_for_file
        
        # ایجاد فایل تست
        file_content = b"This is a test file content"
        file_name = "test_file.txt"
        
        files = {
            "file": (file_name, io.BytesIO(file_content), "text/plain")
        }
        data = {
            "ticket_id": ticket.id
        }
        
        response = client.post(
            "/api/files/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["filename"] == file_name
        assert data["ticket_id"] == ticket.id
    
    def test_upload_file_invalid_type(self, test_user_with_token, test_ticket_for_file):
        """تست آپلود فایل با نوع نامعتبر"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_for_file
        
        # ایجاد فایل با پسوند نامعتبر
        file_content = b"Malicious content"
        file_name = "malicious.exe"
        
        files = {
            "file": (file_name, io.BytesIO(file_content), "application/x-msdownload")
        }
        
        response = client.post(
            f"/api/files/upload?ticket_id={ticket.id}",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # باید خطا بدهد (نوع فایل نامعتبر)
        assert response.status_code in [400, 422]
    
    def test_upload_file_too_large(self, test_user_with_token, test_ticket_for_file):
        """تست آپلود فایل با اندازه بیش از حد"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_for_file
        
        # ایجاد فایل بزرگ (10MB)
        file_content = b"x" * (10 * 1024 * 1024)
        file_name = "large_file.txt"
        
        files = {
            "file": (file_name, io.BytesIO(file_content), "text/plain")
        }
        
        response = client.post(
            f"/api/files/upload?ticket_id={ticket.id}",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # باید خطا بدهد (فایل خیلی بزرگ)
        assert response.status_code in [400, 413]
    
    def test_upload_file_unauthorized(self, test_ticket_for_file):
        """تست آپلود فایل بدون احراز هویت"""
        ticket, _, _ = test_ticket_for_file
        
        file_content = b"Test content"
        file_name = "test.txt"
        
        files = {
            "file": (file_name, io.BytesIO(file_content), "text/plain")
        }
        
        response = client.post(
            f"/api/files/upload?ticket_id={ticket.id}",
            files=files
        )
        
        assert response.status_code == 401


class TestFileDownload:
    """تست‌های دانلود فایل"""
    
    def test_download_file_success(self, test_user_with_token, test_ticket_for_file):
        """تست دانلود موفق فایل"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_for_file
        
        # ابتدا یک فایل آپلود می‌کنیم
        file_content = b"Test file content for download"
        file_name = "download_test.txt"
        
        files = {
            "file": (file_name, io.BytesIO(file_content), "text/plain")
        }
        data = {
            "ticket_id": ticket.id
        }
        
        upload_response = client.post(
            "/api/files/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert upload_response.status_code == 201
        file_id = upload_response.json()["id"]
        
        # دانلود فایل
        response = client.get(
            f"/api/files/{file_id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain"
        assert file_content in response.content
    
    def test_download_file_not_found(self, test_user_with_token):
        """تست دانلود فایل ناموجود"""
        token, user = test_user_with_token
        
        response = client.get(
            "/api/files/99999/download",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    def test_download_file_unauthorized(self):
        """تست دانلود فایل بدون احراز هویت"""
        response = client.get("/api/files/1/download")
        assert response.status_code == 401


class TestFileList:
    """تست‌های لیست فایل‌ها"""
    
    def test_get_ticket_files(self, test_user_with_token, test_ticket_for_file):
        """تست دریافت لیست فایل‌های تیکت"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_for_file
        
        # آپلود چند فایل
        for i in range(3):
            file_content = f"File {i} content".encode()
            file_name = f"file_{i}.txt"
            
            files = {
                "file": (file_name, io.BytesIO(file_content), "text/plain")
            }
            
            client.post(
                f"/api/files/upload?ticket_id={ticket.id}",
                files=files,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # دریافت لیست فایل‌ها
        response = client.get(
            f"/api/files/ticket/{ticket.id}/list",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        assert all(f["ticket_id"] == ticket.id for f in data)


class TestFileDelete:
    """تست‌های حذف فایل"""
    
    def test_delete_file_admin_only(self, test_admin_with_token, test_ticket_for_file):
        """تست حذف فایل (فقط ادمین)"""
        admin_token, admin = test_admin_with_token
        ticket, user_token, user = test_ticket_for_file
        
        # آپلود فایل
        file_content = b"File to delete"
        file_name = "delete_test.txt"
        
        files = {
            "file": (file_name, io.BytesIO(file_content), "text/plain")
        }
        
        upload_response = client.post(
            f"/api/files/upload?ticket_id={ticket.id}",
            files=files,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        file_id = upload_response.json()["id"]
        
        # حذف فایل (توسط ادمین)
        response = client.delete(
            f"/api/files/{file_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
        
        # بررسی حذف
        get_response = client.get(
            f"/api/files/{file_id}/download",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert get_response.status_code == 404
    
    def test_user_cannot_delete_file(self, test_user_with_token, test_ticket_for_file):
        """تست که کاربر عادی نمی‌تواند فایل حذف کند"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_for_file
        
        # آپلود فایل
        file_content = b"File content"
        file_name = "test.txt"
        
        files = {
            "file": (file_name, io.BytesIO(file_content), "text/plain")
        }
        data = {
            "ticket_id": ticket.id
        }
        
        upload_response = client.post(
            "/api/files/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        file_id = upload_response.json()["id"]
        
        # تلاش برای حذف (باید خطا بدهد)
        response = client.delete(
            f"/api/files/{file_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403


class TestFileValidation:
    """تست‌های اعتبارسنجی فایل"""
    
    def test_allowed_file_types(self, test_user_with_token, test_ticket_for_file):
        """تست انواع فایل مجاز"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_for_file
        
        allowed_types = [
            ("test.txt", "text/plain"),
            ("test.pdf", "application/pdf"),
            ("test.jpg", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("test.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ]
        
        for file_name, content_type in allowed_types:
            file_content = b"Test content"
            files = {
                "file": (file_name, io.BytesIO(file_content), content_type)
            }
            
            response = client.post(
                f"/api/files/upload?ticket_id={ticket.id}",
                files=files,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # باید موفق باشد
            assert response.status_code == 201, f"Failed for {file_name}"
    
    def test_file_size_limits(self, test_user_with_token, test_ticket_for_file):
        """تست محدودیت اندازه فایل"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_for_file
        
        # فایل کوچک (1KB) - باید موفق باشد
        small_file = b"x" * 1024
        files = {
            "file": ("small.txt", io.BytesIO(small_file), "text/plain")
        }
        
        response = client.post(
            f"/api/files/upload?ticket_id={ticket.id}",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201

