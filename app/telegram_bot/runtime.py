"""
Shared runtime objects for the Telegram bot.
"""
from app.telegram_bot.api_client import APIClient

# Global asynchronous HTTP client used across handlers.
api_client = APIClient()

__all__ = ["api_client"]

