import os
import logging
from dotenv import load_dotenv


load_dotenv()

TESTORTE_CSV = os.getenv("TESTORTE_CSV")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "output/run.log")
RAIN_GRID_PATH = os.getenv("RAIN_GRID_PATH", "output/rain_grid_24h.csv")
WMS_LAYERS_DIR = os.getenv("WMS_LAYERS_DIR", "data/wms_layers")
CACHE_DIR = os.getenv("CACHE_DIR", "data/cache")

# Log-Level aus Umgebungsvariablen laden und auf Logging-Konstanten mappen
TERMINAL_LOG_LEVEL = getattr(logging, os.getenv("TERMINAL_LOG_LEVEL", "INFO").upper())
FILE_LOG_LEVEL = getattr(logging, os.getenv("FILE_LOG_LEVEL", "DEBUG").upper())

#Telegram Boot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")







