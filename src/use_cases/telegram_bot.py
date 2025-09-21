# src/use_cases/telegram_bot.py
from __future__ import annotations

import asyncio
import os
from typing import List, Dict, Tuple, Optional

from src.domain.actions import BotAction, SendText, SendDocument
from src.analysis.text_parsing import parse_lat_lon
from src.services.state_store import get_pending, set_pending, clear_pending
from src.services.wms_downloader_service import download_layers_for_latlon
from src.services.cache_generation_service import generate_cache_for_location
from src.services.forecast_area_service import RainGridForecaster
from src.services.evaluation_service import evaluate_and_store_for_location
from src.services.dummy_data_service import generate_dummy_for_location
from src.utils.naming import cache_path_for_latlon
from src.config.config import GRID_SIZE_M, FORECAST_STEP_M, OSM_RADIUS_M, SAMPLE_DISTANCE_M
from src.io.llm_client import suggest_user_hint, explain_hydroalert
from src.utils.utils_logger import get_logger

logger = get_logger()

# One-shot Dummy-Info pro Chat (in-memory)
# chat_id -> variant (nur: SRI7, SRI10, SRI10_4h)
_DUMMY_PENDING: Dict[int, str] = {}
_VALID_VARIANTS = {"sri7", "sri10", "sri10_4h"}
_CANONICAL_VARIANT = {"sri7": "SRI7", "sri10": "SRI10", "sri10_4h": "SRI10_4h"}

# Einfache Willkommens-Guard, damit die Welcome-Nachricht nur einmal pro Chat gesendet wird
_WELCOME_SENT: Dict[int, bool] = {}


def _welcome_message() -> str:
    return (
        "👋 Willkommen! Ich bin HydroAlert – das Vorhersagemodul für Flut-/Gefahrenkarten "
        "in Rheinland-Pfalz.\n\n"
        "• So nutzt du mich: Sende Koordinaten im Format `lat, lon` (z. B. `49.123, 8.456`).\n"
        "• Ich liefere dir dazu die **aktuellen Regen-/Überflutungs-Hinweise** und passende KML.\n"
        "• Dummy-Test: Schreibe z. B. `49.12, 8.45 dummy SRI7`, um einen simulierten SRI7-Fall zu prüfen "
        "(auch `SRI10`, `SRI10_4h`).\n"
        "• Architektur: Schreibe `architektur`, und ich erkläre dir meinen Software-Aufbau.\n\n"
        "ℹ️ Hinweis: HydroAlert deckt aktuell nur Rheinland-Pfalz ab – bitte nutze GPS-Koordinaten innerhalb von RLP.\n"
        "Hilfe jederzeit: /hilfe"
    )


def _parse_coords_with_dummy(text: str) -> Optional[Tuple[float, float, Optional[str]]]:
    """
    Versucht 'lat, lon [dummy VARIANT]' zu parsen.
    VARIANT ∈ {SRI7, SRI10, SRI10_4h} (case-insensitive)
    Rückgabe: (lat, lon, variant|None) oder None.
    """
    coords = parse_lat_lon(text)
    if not coords:
        return None
    lat, lon = coords

    lower = text.lower()
    if "dummy" in lower:
        parts = lower.split()
        try:
            idx = parts.index("dummy")
            variant = parts[idx + 1] if idx + 1 < len(parts) else None
            if variant:
                v = variant.lower()
                if v in _VALID_VARIANTS:
                    normalized = _CANONICAL_VARIANT[v]
                    return lat, lon, normalized
            return lat, lon, None
        except ValueError:
            return lat, lon, None
        except Exception:
            return lat, lon, None

    return lat, lon, None


async def handle_start(chat_id: int) -> List[BotAction]:
    logger.debug("handle_start chat_id=%s", chat_id)
    _WELCOME_SENT[chat_id] = True
    return [SendText(_welcome_message())]


async def handle_text(chat_id: int, text: str) -> List[BotAction]:
    logger.debug("handle_text chat_id=%s text=%r", chat_id, text)
    stripped = text.strip()
    lower = stripped.lower()

    # 0) Start/Willkommen und Hilfe/Architektur
    if lower.startswith("/start"):
        _WELCOME_SENT[chat_id] = True
        return [SendText(_welcome_message())]

    if lower.startswith("/hilfe"):
        try:
            overview = await asyncio.to_thread(explain_hydroalert, "Kurzer Überblick zu HydroAlert")
        except Exception:
            logger.exception("explain_hydroalert failed")
            overview = (
                "HydroAlert verknüpft WMS-Gefahrenlayer mit Regenvorhersagen (RLP-Scope).\n"
                "Format: 49.123, 8.456 • Dummy: 'lat, lon dummy SRI7' • Architektur: 'architektur'."
            )
        return [SendText(overview)]

    if lower == "architektur" or lower.startswith("/architektur"):
        # Reuse des LLM mit fokussierter Nutzerfrage
        try:
            arch = await asyncio.to_thread(
                explain_hydroalert, "Beschreibe knapp die Software-Architektur von HydroAlert (Stichpunkte)."
            )
        except Exception:
            logger.exception("explain_hydroalert (architektur) failed")
            arch = (
                "Clean Architecture (config/domain/io/analysis/services/use_cases/utils). "
                "Services orchestrieren I/O + Analysis; Use-Cases bedienen CLI/Telegram. "
                "Dummy- und Forecast-Pfade teilen sich die gleiche Auswertelogik."
            )
        return [SendText(arch)]

    # 1) Bestätigungszweig
    if lower in {"ja", "yes", "y"}:
        pending = get_pending(chat_id)
        if not pending:
            return [SendText("Ich habe aktuell nichts zum Bestätigen. Sende bitte Koordinaten.")]
        lat, lon = pending
        clear_pending(chat_id)

        cache_dir = cache_path_for_latlon(lat, lon)
        if not os.path.isdir(cache_dir):
            logger.info("🌐 Starte WMS-Download für lat=%.5f lon=%.5f → %s", lat, lon, cache_dir)
            saved_pngs = download_layers_for_latlon(lat=lat, lon=lon, target_dir=cache_dir)
            logger.info("✅ %d WMS-Layer gespeichert (inkl. meta.json) in %s", len(saved_pngs), cache_dir)

            logger.info("🧩 Generiere Cache (CSV+KML) für %s", cache_dir)
            status_map = generate_cache_for_location(
                lat=lat, lon=lon, radius_m=OSM_RADIUS_M, sample_distance_m=SAMPLE_DISTANCE_M, layers=None
            )
            logger.debug("Cache-Status: %s", status_map)
        else:
            logger.debug("🔎 Cache-Ordner existiert bereits: %s", cache_dir)

        if chat_id in _DUMMY_PENDING:
            variant = _DUMMY_PENDING.pop(chat_id)
            logger.info("🧪 Dummy aktiv (one-shot): variant=%s", variant)
            csv_path = generate_dummy_for_location(lat=lat, lon=lon, variant=variant)
        else:
            logger.info("🌧️ Echter Forecast (Standard).")
            forecaster = RainGridForecaster()
            csv_path = forecaster.save_full_rain_forecast_grid(
                lat=lat, lon=lon, grid_size_m=GRID_SIZE_M, step_m=FORECAST_STEP_M
            )
        logger.debug("📈 CSV gewählt: %s", csv_path)

        record = evaluate_and_store_for_location(lat=lat, lon=lon, csv_path_override=csv_path)
        layer_short = record.layer
        logger.info("🧮 Auswertung: layer_short=%s", layer_short)

        if layer_short == "none":
            return [SendText("Kein relevanter Niederschlag in den nächsten 24h erkannt. Sende neue Koordinaten, wenn du magst.")]

        kml_path = os.path.join(cache_dir, f"flood_{layer_short}.kml")
        if not os.path.exists(kml_path):
            logger.info("📦 KML fehlt, generiere gezielt für Layer: %s", layer_short)
            status_map = generate_cache_for_location(
                lat=lat, lon=lon, radius_m=OSM_RADIUS_M, sample_distance_m=SAMPLE_DISTANCE_M, layers=[layer_short]
            )
            logger.debug("Cache-Status (nachgeneriert): %s", status_map)
            if not os.path.exists(kml_path):
                logger.warning("KML nach Generierung nicht gefunden: %s | status=%s", kml_path, status_map)
                return [SendText(f"Regenstufe erkannt: {layer_short}. KML konnte nicht erzeugt werden.")]

        return [SendText(f"Regenstufe erkannt: {layer_short}. Sende KML …"), SendDocument(path=kml_path, filename=f"{layer_short}.kml")]

    # 2) Parsing-Zweig
    parsed = _parse_coords_with_dummy(stripped)
    if parsed:
        lat, lon, variant = parsed
        set_pending(chat_id, lat, lon)
        if variant:
            _DUMMY_PENDING[chat_id] = variant
            return [SendText(
                f"Habe: {lat:.5f}, {lon:.5f} (Dummy: {variant}). Richtig? Antworte 'ja'.\n"
                "👉 Hinweis: HydroAlert deckt aktuell nur Rheinland-Pfalz ab."
            )]
        return [SendText(
            f"Habe: {lat:.5f}, {lon:.5f}. Richtig? Antworte 'ja', sonst sende neue Werte. "
            "Optional: 'dummy SRI7' (auch SRI10, SRI10_4h).\n"
            "👉 Hinweis: HydroAlert deckt aktuell nur Rheinland-Pfalz ab."
        )]

    # 3) LLM-Fallback
    hint = await asyncio.to_thread(suggest_user_hint, text)
    # Sende Welcome einmal automatisch, falls Chat neu ist und der Text keine Koordinaten war
    if not _WELCOME_SENT.get(chat_id, False):
        _WELCOME_SENT[chat_id] = True
        return [SendText(_welcome_message()), SendText(hint)]
    return [SendText(hint)]


def run_bot(app_token: str) -> None:
    """Entry für main.py: synchron starten, PTB managt den Loop."""
    from src.io.telegram_adapter import run
    run(app_token, on_text=handle_text)
