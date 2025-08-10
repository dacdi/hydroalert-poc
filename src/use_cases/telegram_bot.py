from argparse import Namespace
from logging import Logger

from src.io.telegram_bot import run_bot
from src.utils.utils_logger import get_logger

logger: Logger = get_logger()


def run_telegram_bot_use_case(args: Namespace) -> None:
    """Start the Telegram bot."""
    logger.info("📲 Starte Telegram-Bot …")
    run_bot()
