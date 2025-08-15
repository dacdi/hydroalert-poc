# src/use_cases/telegram_bot.py

from argparse import Namespace
from logging import Logger
from src.utils.utils_logger import get_logger
from src.io.telegram_adapter import start_bot
from src.services.geodata_workflow_service import run_full_pipeline_for_location

logger: Logger = get_logger()


def _handle(lat: float, lon: float):
    """Handler, den der IO-Adapter aufruft: delegiert an den Workflow-Service."""
    return run_full_pipeline_for_location(lat, lon)


def run_telegram_bot_use_case(args: Namespace) -> None:
    """
    Startet den Telegram-Bot.
    - IO-Adapter parst Text → (lat, lon)
    - Use-Case reicht an Workflow-Service weiter
    """
    logger.info("📲 Starte Telegram-Bot …")
    start_bot(_handle)
