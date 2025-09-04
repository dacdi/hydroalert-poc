# src/use_cases/telegram_bot.py

from argparse import Namespace
from logging import Logger
import os
import glob
from typing import Optional, Tuple

from src.utils.utils_logger import get_logger
from src.io.telegram_adapter import start_bot
from src.io.cache_store import is_cache_available, find_first_kml_in_cache
from src.services.wms_downloader_service import download_layers_for_latlon
from src.services.cache_generation_service import generate_cache_for_location
from src.services.forecast_area_service import RainGridForecaster
from src.services.evaluation_service import evaluate_and_store_for_location
from src.utils.naming import cache_path_for_latlon
from src.config.config import (
    OSM_RADIUS_M,
    SAMPLE_DISTANCE_M,
    GRID_SIZE_M,
    FORECAST_STEP_M,
)

logger: Logger = get_logger()

def _handle(lat: float, lon: float) -> Tuple[str, Optional[str]]:
    """
    Telegram-Logik:
    - Prüft Cache
    - Führt ggf. WMS-Download + Cache-Generierung aus
    - Aktualisiert Forecast
    - Führt Bewertung durch und sendet empfohlenes Layer zurück
    - Gibt Ergebnistext + Datei zurück (wenn vorhanden)
    """
    logger.info("📲 Anfrage für Ort: lat=%.6f, lon=%.6f", lat, lon)
    cache_dir = cache_path_for_latlon(lat, lon)
    prepared_now = False

    if not is_cache_available(lat, lon):
        logger.info("❌ Kein Cache vorhanden → lade WMS + generiere Cache …")
        download_layers_for_latlon(lat=lat, lon=lon, target_dir=cache_dir)
        generate_cache_for_location(
            lat=lat,
            lon=lon,
            radius_m=OSM_RADIUS_M,
            sample_distance_m=SAMPLE_DISTANCE_M,
        )
        prepared_now = True
    else:
        logger.info("✅ Cache vorhanden – nutze vorhandene Daten.")

    # 1) Forecast durchführen
    RainGridForecaster().save_full_rain_forecast_grid(
        lat=lat,
        lon=lon,
        grid_size_m=GRID_SIZE_M,
        step_m=FORECAST_STEP_M,
    )

    # 2) Evaluation ausführen und Layer ermitteln
    record = evaluate_and_store_for_location(lat=lat, lon=lon)
    layer = record.layer

    # 3) Basisstatus aufbauen
    status = (
        "🆕 WMS + Cache erstellt. 🌧️ Forecast aktualisiert."
        if prepared_now else
        "📦 Cache genutzt. 🌧️ Forecast aktualisiert."
    )

    # 4) Kein Regen → kein Layer, keine Datei
    if layer == "none":
        logger.info("🌤️ Kein relevanter Niederschlag – Layer: %s", layer)
        status += "\n🌤️ Kein relevanter Niederschlag vorhergesagt!"
        return status, None

    # 5) Layer ist gesetzt → versuche passende KML zu finden
    status += f"\n🧠 Empfohlener Layer: *{layer}*"
    matches = glob.glob(os.path.join(cache_dir, f"flood_{layer}.kml"))
    layer_file = matches[0] if matches else None

    if not layer_file:
        logger.warning("⚠️ KML-Datei nicht gefunden für Layer: %s", layer)
        status += "\n⚠️ Datei nicht gefunden."
        return status, None

    # 6) Erfolgreich: Layer + Datei
    return status, layer_file



def run_telegram_bot_use_case(args: Namespace) -> None:
    """
    Startet den Telegram-Bot und registriert den Ablauf-Handler.
    """
    logger.info("📡 Starte Telegram-Bot-UseCase …")
    start_bot(_handle)
