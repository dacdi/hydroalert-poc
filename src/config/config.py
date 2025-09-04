# src/config/config.py

import os
import logging
from dotenv import load_dotenv
from src.domain.models import BBox

load_dotenv()

def _log_level(name: str, fallback: int) -> int:
    try:
        return getattr(logging, name.upper())
    except Exception:
        return fallback

# ------------------------
# Pfade & Dateien
# ------------------------
TESTORTE_CSV   = os.getenv("TESTORTE_CSV", "data/testorte.csv")
LOG_FILE_PATH  = os.getenv("LOG_FILE_PATH", "output/run.log")
RAIN_GRID_PATH = os.getenv("RAIN_GRID_PATH", "output/rain_grid_24h.csv")
WMS_LAYERS_DIR = os.getenv("WMS_LAYERS_DIR", "data/wms_layers")
CACHE_DIR      = os.getenv("CACHE_DIR", "data/cache")

# ------------------------
# Logging
# ------------------------
TERMINAL_LOG_LEVEL = _log_level(os.getenv("TERMINAL_LOG_LEVEL", "INFO"), logging.INFO)
FILE_LOG_LEVEL     = _log_level(os.getenv("FILE_LOG_LEVEL", "DEBUG"), logging.DEBUG)

# ------------------------
# Tokens / Secrets
# ------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ------------------------
# WMS-Defaults (fix aus Config; nicht im Code verstreut)
# ------------------------
WMS_BASE_URL = os.getenv(
    "WMS_BASE_URL",
    "https://geodienste-wasser.rlp-umwelt.de/geoserver/Sturzflut/wms",
)

# Standard-BBox (EPSG:25832), z. B. Region Neustadt
DEFAULT_BBOX = BBox(432000, 5461000, 452000, 5481000)

# PNG-Größe für WMS-GetMap
DEFAULT_SIZE = (
    int(os.getenv("WMS_WIDTH",  "2000")),
    int(os.getenv("WMS_HEIGHT", "2000")),
)

# vordefinierte Layer: {voller Layername: Kurzname/Dateiname}
DEFAULT_LAYERS = {
    "Visdom_SRI07_1h_WaterDepth": "Wassertiefe_SRI7_1h",
    "Visdom_SRI10_1h_WaterDepth": "Wassertiefe_SRI10_1h",
    "Visdom_SRI10_4h_WaterDepth": "Wassertiefe_SRI10_4h",
}

# Schwellenwerte (Single Source of Truth)
RAIN_THRESHOLDS = {
    "SRI7_THRESHOLD_mm_h": 13.0,
    "SRI10_THRESHOLD_mm_h": 23.0,
    "SRI10_4H_SUM_THRESHOLD_mm": 42.0,
}

OSM_RADIUS_M = 2000.0          # Straßennetz-Umkreis für Overpass
SAMPLE_DISTANCE_M = 2.5       # Punktabstand fürs Sampling entlang der Straßen

# Forecast-Defaults
GRID_SIZE_M = 2000.0       # volle Kantenlänge des Quadrats (Meter)
FORECAST_STEP_M = 200.0   # Rasterabstand (Meter)

FORECAST_API_URL = os.getenv("FORECAST_API_URL", "https://api.open-meteo.com/v1/forecast")
FORECAST_HTTP_TIMEOUT_S = float(os.getenv("FORECAST_HTTP_TIMEOUT_S", "15"))
