import os
import logging
from dotenv import load_dotenv
from src.domain.models import BBox

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


WMS_LAYERS_DIR = "data/wms_layers"
WMS_BASE_URL   = "https://geodienste-wasser.rlp-umwelt.de/geoserver/Sturzflut/wms"
DEFAULT_BBOX   = BBox(432000, 5461000, 452000, 5481000)
DEFAULT_SIZE   = (2000, 2000)

DEFAULT_LAYERS = {
    "Visdom_SRI07_1h_WaterDepth": "Wassertiefe_SRI7_1h",
    "Visdom_SRI10_1h_WaterDepth": "Wassertiefe_SRI10_1h",
    "Visdom_SRI10_4h_WaterDepth": "Wassertiefe_SRI10_4h",
}





