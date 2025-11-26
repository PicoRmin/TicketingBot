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
    from telegram.request import HTTPXRequest
    
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

    # Configure request with longer timeout for slow connections
    request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=30,
        write_timeout=30,
        connect_timeout=30,
    )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
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
    import asyncio
    import httpx
    
    global bot
    if bot is None:
        bot = create_bot()

    if bot.running:
        logger.info("Telegram Bot is already running")
        return

    logger.info("Starting Telegram Bot...")
    
    # Test connection to Telegram API first
    try:
        logger.info("Testing connection to Telegram API...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            )
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"Connection successful! Bot: @{bot_info.get('result', {}).get('username', 'unknown')}")
            else:
                logger.warning(f"Telegram API returned status {response.status_code}")
    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to Telegram API: {e}")
        logger.error("Please check your internet connection or proxy settings")
        raise
    except Exception as e:
        logger.warning(f"⚠️ Connection test failed: {e}, but continuing anyway...")
    
    try:
        await bot.initialize()
        await bot.start()
        
        # Start polling in background task to avoid blocking the main event loop
        async def run_polling():
            try:
                # start_polling() in v20 is async and should be awaited
                # But we run it in a background task so it doesn't block
                await bot.updater.start_polling(
                    drop_pending_updates=True,
                    allowed_updates=None  # Get all update types
                )
            except asyncio.CancelledError:
                logger.info("Polling task was cancelled")
            except Exception as e:
                logger.error(f"Error in polling task: {e}", exc_info=True)
        
        # Create background task for polling
        polling_task = asyncio.create_task(run_polling())
        logger.info("Telegram Bot started and polling for updates")
        
        # Store task reference for cleanup if needed
        bot._polling_task = polling_task
        
    except Exception as e:
        logger.error(f"Error during bot initialization: {e}", exc_info=True)
        raise


async def stop_bot():
    """Stop the Telegram bot"""
    import asyncio
    
    global bot
    if not bot:
        return

    logger.info("Stopping Telegram Bot...")
    
    # Cancel polling task if it exists
    if hasattr(bot, '_polling_task') and bot._polling_task:
        try:
            bot._polling_task.cancel()
            try:
                await bot._polling_task
            except asyncio.CancelledError:
                pass
        except Exception as e:
            logger.warning(f"Error cancelling polling task: {e}")
    
    try:
        # Stop updater if it's running
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

