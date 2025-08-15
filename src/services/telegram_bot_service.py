# src/services/telegram_bot_service.py

import os
from argparse import Namespace
from typing import Optional, Tuple

from src.utils.naming import cache_path_for_latlon
from src.utils.utils_logger import get_logger
from src.use_cases.download_layers import run_download_layers_use_case
from src.use_cases.generate_cache import run_generate_cache_use_case

logger = get_logger()


def handle_message_logic(lat: float, lon: float) -> Tuple[str, Optional[str]]:
    """
    Minimal-Workflow:
      1) Prüfen, ob der Cache-Ordner für (lat, lon) existiert.
      2) Wenn ja: Nachricht zurückgeben (keine weiteren Aktionen).
      3) Wenn nein: WMS-Download-Use-Case starten und anschließend den Generate-Cache-Use-Case.
    """
    logger.info("📩 Anfrage für Koordinaten: %.6f, %.6f", lat, lon)

    cache_dir = cache_path_for_latlon(lat, lon)
    logger.debug("🗂️ Ziel-Cache-Verzeichnis: %s", cache_dir)

    # 1) Ordner vorhanden?
    if os.path.isdir(cache_dir):
        logger.info("✅ Cache-Ordner existiert: %s", cache_dir)
        return "📦 Daten vorhanden (Cache-Ordner existiert).", None

    # 2) Ordner fehlt → Download + Cache-Generierung anstoßen
    logger.info("❌ Kein Cache-Ordner – starte WMS-Download …")
    try:
        run_download_layers_use_case(Namespace(lat=lat, lon=lon))
        logger.info("⬇️ WMS-Download abgeschlossen.")
    except Exception:
        logger.exception("❌ Fehler beim WMS-Download")
        return "❌ Fehler beim Laden der WMS-Layer.", None

    logger.info("🔧 Starte Cache-Generierung …")
    try:
        run_generate_cache_use_case(Namespace(lat=lat, lon=lon))
        logger.info("✅ Cache-Generierung abgeschlossen.")
    except Exception:
        logger.exception("❌ Fehler bei der Cache-Generierung")
        return "❌ Fehler bei der Cache-Generierung.", None

    return "✅ WMS-Layer geladen und Cache erzeugt.", None


def run_bot() -> None:
    """Startet den Telegram-Bot (ruft IO-Adapter auf)."""
    from src.io.telegram_adapter import start_bot
    start_bot(handle_message_logic)
