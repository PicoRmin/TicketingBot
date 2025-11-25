#!/bin/bash
# اسکریپت بررسی وضعیت Production
# Production health check script

set -e

PROJECT_DIR="${PROJECT_DIR:-$(dirname "$(readlink -f "$0")")/..}"
API_URL="${API_URL:-http://localhost:8000}"

# رنگ‌ها
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    return 1
}

check_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "=== Production Health Check ==="
echo ""

# بررسی فایل .env
if [ -f "$PROJECT_DIR/.env" ]; then
    check_pass ".env file exists"
    
    # بررسی DEBUG
    if grep -q "DEBUG=False" "$PROJECT_DIR/.env"; then
        check_pass "DEBUG is set to False"
    else
        check_fail "DEBUG is not set to False"
    fi
    
    # بررسی ENVIRONMENT
    if grep -q "ENVIRONMENT=production" "$PROJECT_DIR/.env"; then
        check_pass "ENVIRONMENT is set to production"
    else
        check_warning "ENVIRONMENT is not set to production"
    fi
    
    # بررسی SECRET_KEY
    if grep -q "SECRET_KEY=" "$PROJECT_DIR/.env" && ! grep -q "SECRET_KEY=your-secret-key" "$PROJECT_DIR/.env"; then
        SECRET_KEY=$(grep "SECRET_KEY=" "$PROJECT_DIR/.env" | cut -d '=' -f2-)
        if [ ${#SECRET_KEY} -ge 32 ]; then
            check_pass "SECRET_KEY is set and has sufficient length"
        else
            check_fail "SECRET_KEY is too short (minimum 32 characters)"
        fi
    else
        check_fail "SECRET_KEY is not properly configured"
    fi
else
    check_fail ".env file not found"
fi

# بررسی Health Endpoint
echo ""
echo "=== API Health Check ==="
if command -v curl &> /dev/null; then
    HEALTH_RESPONSE=$(curl -s "$API_URL/health" || echo "ERROR")
    if [ "$HEALTH_RESPONSE" != "ERROR" ]; then
        check_pass "Health endpoint is accessible"
        echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
    else
        check_fail "Health endpoint is not accessible"
    fi
else
    check_warning "curl not found, skipping API health check"
fi

# بررسی Database
echo ""
echo "=== Database Check ==="
if [ -f "$PROJECT_DIR/.env" ]; then
    DATABASE_URL=$(grep "^DATABASE_URL=" "$PROJECT_DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    
    if [[ "$DATABASE_URL" == postgresql://* ]]; then
        # PostgreSQL
        if command -v psql &> /dev/null; then
            DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
            if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
                check_pass "PostgreSQL connection is working"
            else
                check_fail "PostgreSQL connection failed"
            fi
        else
            check_warning "psql not found, skipping PostgreSQL check"
        fi
    elif [[ "$DATABASE_URL" == sqlite* ]]; then
        # SQLite
        DB_FILE=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/\(.*\)/\1/p')
        if [ -f "$PROJECT_DIR/$DB_FILE" ]; then
            check_pass "SQLite database file exists"
        else
            check_fail "SQLite database file not found"
        fi
    fi
fi

# بررسی دایرکتوری‌ها
echo ""
echo "=== Directory Check ==="
if [ -d "$PROJECT_DIR/storage/uploads" ]; then
    check_pass "Uploads directory exists"
else
    check_warning "Uploads directory not found"
fi

if [ -d "$PROJECT_DIR/logs" ]; then
    check_pass "Logs directory exists"
else
    check_warning "Logs directory not found"
fi

# بررسی سرویس (systemd)
echo ""
echo "=== Service Check ==="
if systemctl is-active --quiet ticketing 2>/dev/null; then
    check_pass "Ticketing service is running"
elif systemctl is-active --quiet ticketing.service 2>/dev/null; then
    check_pass "Ticketing service is running"
else
    check_warning "Ticketing service status unknown (may not be configured)"
fi

echo ""
echo "=== Check Complete ==="

