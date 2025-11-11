# راهنمای فاز ۵: سیستم فایل / Phase 5: File Management Guide

## ✅ کارهای انجام شده

### ۱. ایجاد مدل Attachment
- ✅ مدل Attachment با تمام فیلدها
- ✅ روابط با Ticket و User
- ✅ Indexes برای performance
- ✅ جدول attachments در database ایجاد شده

### ۲. ایجاد File Schemas
- ✅ `FileResponse` - Schema برای پاسخ API
- ✅ `FileUploadResponse` - Schema برای پاسخ آپلود

### ۳. ایجاد File Service
- ✅ `validate_file` - اعتبارسنجی نوع و اندازه فایل
- ✅ `save_file` - ذخیره فایل در storage
- ✅ `create_attachment` - ایجاد رکورد در database
- ✅ `get_attachment` - دریافت فایل بر اساس ID
- ✅ `get_ticket_attachments` - لیست فایل‌های یک تیکت
- ✅ `delete_attachment` - حذف فایل و رکورد
- ✅ `can_user_access_attachment` - بررسی دسترسی

### ۴. ایجاد File API Endpoints
- ✅ `POST /api/files/upload` - آپلود فایل
- ✅ `GET /api/files/{file_id}` - دانلود فایل
- ✅ `GET /api/files/ticket/{ticket_id}/list` - لیست فایل‌های یک تیکت
- ✅ `DELETE /api/files/{file_id}` - حذف فایل (فقط ادمین)

### ۵. ویژگی‌های پیاده‌سازی شده
- ✅ اعتبارسنجی نوع فایل (تصاویر و اسناد)
- ✅ اعتبارسنجی اندازه فایل (حداکثر ۱۰ مگابایت)
- ✅ ذخیره فایل‌ها در storage/uploads/{ticket_id}/
- ✅ نام فایل یکتا با UUID
- ✅ مدیریت دسترسی (کاربران فقط فایل‌های تیکت‌های خود)
- ✅ حذف فایل از storage و database

## 🚀 تست API

### تست با Swagger UI

1. **اجرای Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **باز کردن Swagger UI**:
   - آدرس: http://localhost:8000/docs

3. **تست آپلود فایل**:
   - ابتدا Login کنید و Token دریافت کنید
   - یک تیکت ایجاد کنید (یا از تیکت موجود استفاده کنید)
   - کلیک روی "Authorize" و Token را وارد کنید
   - کلیک روی `POST /api/files/upload`
   - وارد کردن:
     - `ticket_id`: شناسه تیکت
     - `file`: انتخاب فایل (تصویر یا سند)
   - کلیک روی "Execute"
   - مشاهده اطلاعات فایل آپلود شده

4. **تست لیست فایل‌های تیکت**:
   - کلیک روی `GET /api/files/ticket/{ticket_id}/list`
   - وارد کردن `ticket_id`
   - کلیک روی "Execute"
   - مشاهده لیست فایل‌های تیکت

5. **تست دانلود فایل**:
   - کلیک روی `GET /api/files/{file_id}`
   - وارد کردن `file_id`
   - کلیک روی "Execute"
   - فایل دانلود می‌شود

### تست با curl

```bash
# 1. Login و دریافت Token
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# 2. ایجاد تیکت (اگر ندارید)
TICKET_ID=$(curl -X POST "http://localhost:8000/api/tickets" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "تست فایل",
    "description": "تست آپلود فایل",
    "category": "software"
  }' | jq -r '.id')

# 3. آپلود فایل
curl -X POST "http://localhost:8000/api/files/upload?ticket_id=$TICKET_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/file.jpg"

# 4. لیست فایل‌های تیکت
curl -X GET "http://localhost:8000/api/files/ticket/$TICKET_ID/list" \
  -H "Authorization: Bearer $TOKEN"

# 5. دانلود فایل
curl -X GET "http://localhost:8000/api/files/1" \
  -H "Authorization: Bearer $TOKEN" \
  -o downloaded_file.jpg
```

## 📁 ساختار فایل‌های ایجاد شده

```
app/
├── models/
│   └── attachment.py       ✅ Attachment model
├── schemas/
│   └── file.py             ✅ File schemas
├── services/
│   └── file_service.py     ✅ File business logic
└── api/
    └── files.py             ✅ File endpoints

storage/
└── uploads/
    └── {ticket_id}/
        └── {uuid}.{ext}     ✅ Uploaded files
```

## 🔍 API Endpoints

### POST /api/files/upload
- **Description**: آپلود فایل و پیوست به تیکت
- **Authentication**: Required
- **Query Parameters**: `ticket_id` (required)
- **Request**: Multipart form data with `file`
- **Response**: `FileUploadResponse` (201 Created)
- **Access**: کاربران می‌توانند به تیکت‌های خود فایل اضافه کنند

### GET /api/files/{file_id}
- **Description**: دانلود فایل
- **Authentication**: Required
- **Response**: File download
- **Access**: 
  - کاربران: فقط فایل‌های تیکت‌های خود
  - ادمین: همه فایل‌ها

### GET /api/files/ticket/{ticket_id}/list
- **Description**: لیست فایل‌های یک تیکت
- **Authentication**: Required
- **Response**: `List[FileResponse]`
- **Access**: 
  - کاربران: فقط تیکت‌های خود
  - ادمین: همه تیکت‌ها

### DELETE /api/files/{file_id}
- **Description**: حذف فایل
- **Authentication**: Required (Admin only)
- **Response**: 204 No Content
- **Access**: فقط ادمین

## 📋 انواع فایل‌های مجاز

### تصاویر
- image/jpeg
- image/png
- image/gif
- image/webp

### اسناد
- application/pdf
- application/msword (Word .doc)
- application/vnd.openxmlformats-officedocument.wordprocessingml.document (Word .docx)
- text/plain

### محدودیت‌ها
- **حداکثر اندازه**: ۱۰ مگابایت
- **ذخیره‌سازی**: `storage/uploads/{ticket_id}/{uuid}.{ext}`

## 🔐 مدیریت دسترسی

### قوانین دسترسی

1. **آپلود فایل**:
   - کاربران می‌توانند به تیکت‌های خود فایل اضافه کنند
   - باید دسترسی به تیکت داشته باشند

2. **دانلود فایل**:
   - کاربران فقط می‌توانند فایل‌های تیکت‌های خود را دانلود کنند
   - ادمین‌ها می‌توانند همه فایل‌ها را دانلود کنند

3. **حذف فایل**:
   - فقط ادمین‌ها می‌توانند فایل‌ها را حذف کنند

## ✅ چک‌لیست

- [x] مدل Attachment ایجاد شده
- [x] Schemas ایجاد شده
- [x] Service ایجاد شده
- [x] API Endpoints ایجاد شده
- [x] اعتبارسنجی نوع فایل
- [x] اعتبارسنجی اندازه فایل
- [x] ذخیره فایل در storage
- [x] مدیریت دسترسی
- [x] Router اضافه شده به main.py
- [x] جدول attachments ایجاد شده

## 🐛 عیب‌یابی

### مشکل: 413 Request Entity Too Large
**راه‌حل**: فایل بزرگتر از ۱۰ مگابایت است. اندازه فایل را کاهش دهید.

### مشکل: 400 Bad Request - File type not allowed
**راه‌حل**: نوع فایل مجاز نیست. فقط تصاویر و اسناد مجاز هستند.

### مشکل: 404 Not Found - File not found
**راه‌حل**: 
- مطمئن شوید که file_id صحیح است
- یا فایل از storage حذف شده است

### مشکل: 403 Forbidden
**راه‌حل**: 
- کاربر سعی می‌کند به فایل تیکتی که به آن دسترسی ندارد دسترسی پیدا کند
- یا کاربر عادی سعی می‌کند فایل را حذف کند (فقط ادمین)

## 🎯 مراحل بعدی

پس از تکمیل فاز ۵، می‌توانید به فاز ۶ بروید:
- **فاز ۶**: ربات تلگرام (Telegram Bot)

---

**تاریخ تکمیل**: 2024-11-11

