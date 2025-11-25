#!/bin/bash
# اسکریپت Backup برای سیستم تیکتینگ ایرانمهر
# Backup script for Iranmehr Ticketing System

set -e  # Exit on error

# تنظیمات
BACKUP_DIR="${BACKUP_DIR:-/var/backups/ticketing}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${RETENTION_DAYS:-7}"
PROJECT_DIR="${PROJECT_DIR:-$(dirname "$(dirname "$(readlink -f "$0")")")}"

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# تابع لاگ
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# بررسی وجود دایرکتوری backup
if [ ! -d "$BACKUP_DIR" ]; then
    log_info "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

log_info "Starting backup process..."

# Backup Database (PostgreSQL)
if command -v pg_dump &> /dev/null; then
    # خواندن DATABASE_URL از .env
    if [ -f "$PROJECT_DIR/.env" ]; then
        DATABASE_URL=$(grep "^DATABASE_URL=" "$PROJECT_DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
        
        if [[ "$DATABASE_URL" == postgresql://* ]]; then
            log_info "Backing up PostgreSQL database..."
            
            # استخراج اطلاعات از DATABASE_URL
            DB_USER=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
            DB_PASS=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
            DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
            DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
            DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
            
            # Backup
            export PGPASSWORD="$DB_PASS"
            if pg_dump -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"; then
                log_info "PostgreSQL backup completed: db_$DATE.sql.gz"
            else
                log_error "PostgreSQL backup failed!"
            fi
            unset PGPASSWORD
        fi
    fi
fi

# Backup Database (SQLite)
if [ -f "$PROJECT_DIR/ticketing.db" ]; then
    log_info "Backing up SQLite database..."
    if cp "$PROJECT_DIR/ticketing.db" "$BACKUP_DIR/db_$DATE.db" && gzip "$BACKUP_DIR/db_$DATE.db"; then
        log_info "SQLite backup completed: db_$DATE.db.gz"
    else
        log_error "SQLite backup failed!"
    fi
fi

# Backup uploads
UPLOAD_DIR="${UPLOAD_DIR:-$PROJECT_DIR/storage/uploads}"
if [ -d "$UPLOAD_DIR" ] && [ "$(ls -A $UPLOAD_DIR 2>/dev/null)" ]; then
    log_info "Backing up uploads directory..."
    if tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C "$(dirname "$UPLOAD_DIR")" "$(basename "$UPLOAD_DIR")" 2>/dev/null; then
        log_info "Uploads backup completed: uploads_$DATE.tar.gz"
    else
        log_warning "Uploads backup failed or directory is empty"
    fi
fi

# حذف backup‌های قدیمی
log_info "Cleaning up old backups (older than $RETENTION_DAYS days)..."
DELETED=$(find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ "$DELETED" -gt 0 ]; then
    log_info "Deleted $DELETED old backup file(s)"
else
    log_info "No old backups to delete"
fi

# گزارش نهایی
log_info "Backup process completed at $(date)"
log_info "Backup location: $BACKUP_DIR"
log_info "Recent backups:"
ls -lh "$BACKUP_DIR" | tail -5 | awk '{print "  " $9 " (" $5 ")"}'

# بررسی فضای دیسک
DISK_USAGE=$(df -h "$BACKUP_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    log_warning "Disk usage is ${DISK_USAGE}% - consider cleaning up old backups"
fi

exit 0

