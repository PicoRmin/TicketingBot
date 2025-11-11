"""
Telegram Bot configuration
"""
from app.config import settings

# Telegram Bot settings
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
WEBHOOK_URL = getattr(settings, "TELEGRAM_WEBHOOK_URL", None)
WEBHOOK_SECRET = getattr(settings, "TELEGRAM_WEBHOOK_SECRET", None)

# API settings
API_BASE_URL = getattr(settings, "API_BASE_URL", "http://localhost:8000")

