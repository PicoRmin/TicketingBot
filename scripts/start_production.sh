#!/bin/bash
# اسکریپت راه‌اندازی Production
# Production startup script

set -e

PROJECT_DIR="${PROJECT_DIR:-$(dirname "$(readlink -f "$0")")/..}"
VENV_DIR="${VENV_DIR:-$PROJECT_DIR/venv}"

# رنگ‌ها
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# بررسی وجود virtual environment
if [ ! -d "$VENV_DIR" ]; then
    log_error "Virtual environment not found at $VENV_DIR"
    exit 1
fi

# فعال‌سازی virtual environment
source "$VENV_DIR/bin/activate"

# بررسی تنظیمات Production
log_info "Validating production settings..."
python -c "from app.config import settings; settings.validate_production_settings(); print('Settings OK')" || {
    log_error "Production settings validation failed!"
    exit 1
}

# بررسی اتصال دیتابیس
log_info "Checking database connection..."
python -c "from app.database import engine; engine.connect(); print('Database connection OK')" || {
    log_error "Database connection failed!"
    exit 1
}

# بررسی وجود دایرکتوری‌های لازم
log_info "Checking required directories..."
python -c "from app.config import settings; import os; os.makedirs(settings.UPLOAD_DIR, exist_ok=True); os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True); print('Directories OK')"

# راه‌اندازی
log_info "Starting application..."
cd "$PROJECT_DIR"
exec "$VENV_DIR/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info

