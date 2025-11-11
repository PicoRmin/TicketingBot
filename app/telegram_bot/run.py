"""
Module runner for starting the Telegram bot via:
    python -m app.telegram_bot.run
"""
import asyncio

from app.telegram_bot.bot import start_bot


def main() -> None:
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()

