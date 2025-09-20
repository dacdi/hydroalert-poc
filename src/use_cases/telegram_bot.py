# src/use_cases/telegram_bot.py
from __future__ import annotations

import asyncio
import os
from typing import List

from src.domain.actions import BotAction, SendText, SendDocument
from src.analysis.text_parsing import parse_lat_lon
from src.services.state_store import get_pending, set_pending, clear_pending
from src.services.wms_downloader_service import download_layers_for_latlon
from src.services.cache_generation_service import generate_cache_for_location
from src.services.forecast_area_service import RainGridForecaster
from src.services.evaluation_service import evaluate_and_store_for_location
from src.utils.naming import cache_path_for_latlon
from src.config.config import (
    GRID_SIZE_M,
    FORECAST_STEP_M,
    OSM_RADIUS_M,
    SAMPLE_DISTANCE_M,
)
from src.io.llm_client import suggest_user_hint
from src.utils.utils_logger import get_logger

logger = get_logger()


async def handle_start(chat_id: int) -> List[BotAction]:
    logger.debug("handle_start chat_id=%s", chat_id)
    return [
        SendText(
            "Hi! Bitte sende Koordinaten als 'lat, lon' (z. B. 49.123, 8.456). "
            "Danach mit 'ja' bestätigen."
        )
    ]


async def handle_text(chat_id: int, text: str) -> List[BotAction]:
    logger.debug("handle_text chat_id=%s text=%r", chat_id, text)

    # 1) Bestätigungszweig
    if text.lower() in {"ja", "yes", "y"}:
        pending = get_pending(chat_id)
        if not pending:
            return [SendText("Ich habe aktuell nichts zum Bestätigen. Sende bitte Koordinaten.")]
        lat, lon = pending
        clear_pending(chat_id)

        # 1c-neu) Cache-Ordner prüfen → ggf. WMS-Download und Cache-Generierung
        cache_dir = cache_path_for_latlon(lat, lon)
        if not os.path.isdir(cache_dir):
            logger.info("🌐 Starte WMS-Download für lat=%.5f lon=%.5f → %s", lat, lon, cache_dir)
            saved_pngs = download_layers_for_latlon(lat=lat, lon=lon, target_dir=cache_dir)
            logger.info("✅ %d WMS-Layer gespeichert (inkl. meta.json) in %s", len(saved_pngs), cache_dir)

            logger.info("🧩 Generiere Cache (CSV+KML) für %s", cache_dir)
            status_map = generate_cache_for_location(
                lat=lat,
                lon=lon,
                radius_m=OSM_RADIUS_M,
                sample_distance_m=SAMPLE_DISTANCE_M,
                layers=None,  # alle Default-Layer
            )
            logger.debug("Cache-Status: %s", status_map)
        else:
            logger.debug("🔎 Cache-Ordner existiert bereits: %s", cache_dir)

        # 1a-neu) 24h-Raster-CSV (Forecast) erzeugen
        forecaster = RainGridForecaster()
        csv_path = forecaster.save_full_rain_forecast_grid(
            lat=lat,
            lon=lon,
            grid_size_m=GRID_SIZE_M,
            step_m=FORECAST_STEP_M,
        )
        logger.debug("📈 Forecast CSV erzeugt: %s", csv_path)

        # 1b-neu) Prognose auswerten
        record = evaluate_and_store_for_location(lat=lat, lon=lon, csv_path_override=csv_path)
        layer_short = record.layer  # z. B. "Wassertiefe_SRI10_1h"
        logger.info("🧮 Auswertung: layer_short=%s", layer_short)

        if layer_short == "none":
            return [
                SendText(
                    "Kein relevanter Niederschlag in den nächsten 24h erkannt. "
                    "Sende neue Koordinaten, wenn du magst."
                )
            ]

        # 1d-neu) KML aus korrespondierendem Ordner bestimmen; falls fehlt → Layer-spezifisch generieren
        kml_path = os.path.join(cache_dir, f"flood_{layer_short}.kml")
        if not os.path.exists(kml_path):
            logger.info("📦 KML fehlt, generiere gezielt für Layer: %s", layer_short)
            status_map = generate_cache_for_location(
                lat=lat,
                lon=lon,
                radius_m=OSM_RADIUS_M,
                sample_distance_m=SAMPLE_DISTANCE_M,
                layers=[layer_short],
            )
            logger.debug("Cache-Status (nachgeneriert): %s", status_map)
            if not os.path.exists(kml_path):
                logger.warning("KML nach Generierung nicht gefunden: %s | status=%s", kml_path, status_map)
                return [
                    SendText(
                        f"Regenstufe erkannt: {layer_short}. "
                        f"KML konnte nicht erzeugt werden."
                    )
                ]

        return [
            SendText(f"Regenstufe erkannt: {layer_short}. Sende KML …"),
            SendDocument(path=kml_path, filename=f"{layer_short}.kml"),
        ]

    # 2) Parsing-Pfad
    if coords := parse_lat_lon(text):
        lat, lon = coords
        set_pending(chat_id, lat, lon)
        return [SendText(f"Habe: {lat:.5f}, {lon:.5f}. Richtig? Antworte 'ja', sonst sende neue Werte.")]

    # 3) LLM-Hilfetext (non-blocking vom Event-Loop)
    hint = await asyncio.to_thread(suggest_user_hint, text)
    return [SendText(hint)]


def run_bot(app_token: str) -> None:
    """Entry für main.py: synchron starten, PTB managt den Loop."""
    from src.io.telegram_adapter import run

    run(app_token, on_text=handle_text)
