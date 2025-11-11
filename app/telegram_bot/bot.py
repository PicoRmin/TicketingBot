"""
Telegram Bot main module
"""

import logging
from typing import Optional

from telegram import Update
from telegram.ext import Application, ContextTypes

from app.telegram_bot.config import BOT_TOKEN
from app.telegram_bot.handlers import api_client, register_handlers

logger = logging.getLogger(__name__)


async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.exception("Exception while handling an update", exc_info=context.error)

    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.\n"
                "An error occurred. Please try again."
            )
        except Exception:
            logger.debug("Failed to send error message to user", exc_info=True)


async def post_init(application: Application):
    """Post initialization tasks"""
    logger.info("Telegram Bot initialized successfully")


async def post_shutdown(application: Application):
    """Post shutdown tasks"""
    await api_client.close()
    logger.info("Telegram Bot shut down")


def create_bot() -> Application:
    """Create and configure Telegram Bot application"""
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    register_handlers(application)
    application.add_error_handler(error_handler)
    return application


# Global bot instance
bot: Optional[Application] = None


async def start_bot():
    """Start the Telegram bot without blocking the event loop"""
    global bot
    if bot is None:
        bot = create_bot()

    if bot.running:
        logger.info("Telegram Bot is already running")
        return

    logger.info("Starting Telegram Bot...")
    await bot.initialize()
    await bot.start()
    await bot.updater.start_polling()
    logger.info("Telegram Bot started and polling for updates")


async def stop_bot():
    """Stop the Telegram bot"""
    global bot
    if not bot:
        return

    logger.info("Stopping Telegram Bot...")
    try:
        # Only stop updater if it's running
        if bot.updater and bot.updater.running:
            await bot.updater.stop()
    except Exception as e:
        logger.warning(f"Error stopping updater: {e}")
    
    try:
        if bot.running:
            await bot.stop()
    except Exception as e:
        logger.warning(f"Error stopping bot: {e}")
    
    try:
        await bot.shutdown()
    except Exception as e:
        logger.warning(f"Error shutting down bot: {e}")
    
    logger.info("Telegram Bot stopped")

