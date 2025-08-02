import os
import logging
from dotenv import load_dotenv


load_dotenv()

TESTORTE_CSV = os.getenv("TESTORTE_CSV")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "output/run.log")

# Log-Level aus Umgebungsvariablen laden und auf Logging-Konstanten mappen
TERMINAL_LOG_LEVEL = getattr(logging, os.getenv("TERMINAL_LOG_LEVEL", "INFO").upper())
FILE_LOG_LEVEL = getattr(logging, os.getenv("FILE_LOG_LEVEL", "DEBUG").upper())

#Telegram Boot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")







