#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی Production
Production setup script
"""
import os
import sys
import secrets
from pathlib import Path

def generate_secret_key(length=64):
    """تولید Secret Key امن"""
    return secrets.token_urlsafe(length)

def check_file_exists(filepath):
    """بررسی وجود فایل"""
    return Path(filepath).exists()

def create_env_file():
    """ایجاد فایل .env از env.example"""
    project_root = Path(__file__).parent.parent
    env_example = project_root / "env.example"
    env_file = project_root / ".env"
    
    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env creation.")
            return
    
    if not env_example.exists():
        print(f"Error: {env_example} not found!")
        return
    
    # خواندن env.example
    with open(env_example, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # تولید Secret Keys
    secret_key = generate_secret_key()
    refresh_secret = generate_secret_key()
    
    # جایگزینی مقادیر
    content = content.replace("your-secret-key-here-change-in-production", secret_key)
    content = content.replace("your-refresh-secret-key-change", refresh_secret)
    content = content.replace("DEBUG=True", "DEBUG=False")
    content = content.replace("ENVIRONMENT=development", "ENVIRONMENT=production")
    
    # اضافه کردن تنظیمات Email اگر وجود ندارد
    if "EMAIL_ENABLED" not in content:
        content += "\n# Email Configuration\n"
        content += "EMAIL_ENABLED=False\n"
        content += "EMAIL_SMTP_HOST=smtp.gmail.com\n"
        content += "EMAIL_SMTP_PORT=587\n"
        content += "EMAIL_SMTP_USER=\n"
        content += "EMAIL_SMTP_PASSWORD=\n"
        content += "EMAIL_SMTP_USE_TLS=True\n"
        content += "EMAIL_SMTP_USE_SSL=False\n"
        content += "EMAIL_FROM_ADDRESS=noreply@iranmehr.com\n"
        content += "EMAIL_FROM_NAME=سیستم تیکتینگ ایرانمهر\n"
    
    # نوشتن .env
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # محدود کردن دسترسی (Linux/Mac)
    if sys.platform != 'win32':
        os.chmod(env_file, 0o600)
    
    print(f"✓ Created .env file with generated secret keys")
    print(f"  SECRET_KEY: {secret_key[:20]}...")
    print(f"  REFRESH_TOKEN_SECRET: {refresh_secret[:20]}...")

def create_directories():
    """ایجاد دایرکتوری‌های لازم"""
    project_root = Path(__file__).parent.parent
    
    directories = [
        project_root / "storage" / "uploads",
        project_root / "logs",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def validate_settings():
    """بررسی تنظیمات Production"""
    try:
        from app.config import settings
        settings.validate_production_settings()
        print("✓ Production settings validation passed")
        return True
    except Exception as e:
        print(f"✗ Production settings validation failed: {e}")
        return False

def main():
    """تابع اصلی"""
    print("=== Production Setup Script ===")
    print("")
    
    # ایجاد دایرکتوری‌ها
    print("Creating required directories...")
    create_directories()
    print("")
    
    # ایجاد .env
    print("Setting up .env file...")
    create_env_file()
    print("")
    
    # بررسی تنظیمات
    print("Validating production settings...")
    if validate_settings():
        print("")
        print("=== Setup Complete ===")
        print("")
        print("Next steps:")
        print("1. Review and update .env file with your settings")
        print("2. Set up database (PostgreSQL recommended)")
        print("3. Run migrations: python scripts/init_db.py")
        print("4. Create admin user: python scripts/create_admin.py")
        print("5. Start the service: python scripts/start_production.sh")
    else:
        print("")
        print("=== Setup Incomplete ===")
        print("Please fix the errors above and run the script again.")
        sys.exit(1)

if __name__ == "__main__":
    main()

