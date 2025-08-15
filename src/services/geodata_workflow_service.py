# src/services/geodata_workflow_service.py

import os
from typing import Optional, Tuple
from glob import glob

from src.utils.utils_logger import get_logger
from src.utils.naming import cache_path_for_latlon
from src.services.wms_downloader_service import download_layers_for_latlon
from src.services.cache_generation_service import generate_cache_for_location
from src.services.forecast_area_service import RainGridForecaster
from src.config.config import (
    OSM_RADIUS_M,
    SAMPLE_DISTANCE_M,
    GRID_SIZE_M,
    FORECAST_STEP_M,
)

logger = get_logger()


def _find_any_kml(cache_dir: str) -> Optional[str]:
    matches = sorted(glob(os.path.join(cache_dir, "flood_*.kml")))
    return matches[0] if matches else None


def run_full_pipeline_for_location(lat: float, lon: float) -> Tuple[str, Optional[str]]:
    """
    Orchestriert den End-to-End-Flow für einen Ort:
      - Cache-Ordner prüfen
      - Falls fehlt: WMS-Layer laden und Cache (CSV/KML) generieren
      - Immer: 24h-Forecast-Raster aktualisieren (CSV)
    Gibt (status_text, optional_kml_path) zurück.
    """
    logger.info("🧭 Workflow start: lat=%.6f, lon=%.6f", lat, lon)

    cache_dir = cache_path_for_latlon(lat, lon)
    os.makedirs(cache_dir, exist_ok=True)
    prepared_now = False

    # 1) Sicherstellen, dass Basisdaten vorliegen (Ordnerinhalt genügt als Kriterium)
    if not os.listdir(cache_dir):
        logger.info("❌ Cache leer → lade WMS-Layer …")
        download_layers_for_latlon(lat=lat, lon=lon, target_dir=cache_dir)

        logger.info("🔧 Generiere Cache (CSV/KML) …")
        generate_cache_for_location(
            lat=lat,
            lon=lon,
            radius_m=OSM_RADIUS_M,
            sample_distance_m=SAMPLE_DISTANCE_M,
        )
        prepared_now = True
    else:
        logger.info("✅ Cache vorhandenen Inhalt erkannt: %s", cache_dir)

    # 2) Forecast immer aktualisieren
    logger.info("🔮 Aktualisiere Forecast-Raster (24h) …")
    RainGridForecaster().save_full_rain_forecast_grid(
        lat=lat,
        lon=lon,
        grid_size_m=GRID_SIZE_M,
        step_m=FORECAST_STEP_M,
    )

    # 3) Optional: KML-Pfad zurückgeben, falls vorhanden
    kml_path = _find_any_kml(cache_dir)
    status = (
        "🆕 WMS + Cache erstellt. 🌧️ Forecast aktualisiert."
        if prepared_now else
        "📦 Cache genutzt. 🌧️ Forecast aktualisiert."
    )
    logger.info("✅ Workflow done: %s", status)
    return status, kml_path
