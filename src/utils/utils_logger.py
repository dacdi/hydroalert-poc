# src/utils/utils_logger.py

import logging
import os
from src.config.config import LOG_FILE_PATH, TERMINAL_LOG_LEVEL, FILE_LOG_LEVEL

_logger = None  # Singleton-Loggerinstanz für das gesamte Projekt


def get_logger() -> logging.Logger:
    """
    Gibt den zentral konfigurierten Root-Logger zurück.
    Erstellt beim ersten Aufruf sowohl einen Terminal- als auch einen File-Handler.
    """
    global _logger

    if _logger is not None:
        return _logger

    _logger = logging.getLogger()  # Root-Logger
    _logger.setLevel(logging.DEBUG)  # Basis-Level für alle Handler

    # Terminal-Handler
    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(TERMINAL_LOG_LEVEL)
    terminal_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    terminal_handler.setFormatter(terminal_formatter)
    _logger.addHandler(terminal_handler)

    # File-Handler
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE_PATH, mode="w")
    file_handler.setLevel(FILE_LOG_LEVEL)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d:%(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    _logger.addHandler(file_handler)

    # Externe Bibliotheken auf WARNING setzen, damit keine Tokens im Log landen
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("telethon").setLevel(logging.WARNING)

    return _logger
