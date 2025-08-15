# src/use_cases/telegram_bot.py

from argparse import Namespace
from logging import Logger
from src.services.telegram_bot_service import run_bot
from src.utils.utils_logger import get_logger

logger: Logger = get_logger()


def run_telegram_bot_use_case(args: Namespace) -> None:
    """
    Startet den Telegram-Bot.

    Minimal-Flow:
    - Nutzer sendet lat,lon (Parsing im IO-Adapter).
    - Service prüft nur Ordner-Existenz:
        * wenn vorhanden → kurze Nachricht
        * wenn nicht vorhanden → WMS-Download für diesen Ort starten
    """
    logger.info("📲 Starte Telegram-Bot …")
    run_bot()
