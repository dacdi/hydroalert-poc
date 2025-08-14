# src/services/telegram_bot_service.py

import os
from src.analysis.classify_rain_intensity import classify_rain_stage
from src.config.config import CACHE_DIR
from src.services.cache_query_service import has_cached_result
from src.utils.naming import cache_path_for_latlon
from src.utils.utils_logger import get_logger

logger = get_logger()


def normalize_layer_key(result: str) -> str:
    """Layer-Namen vereinheitlichen."""
    prefix = "Wassertiefe_"
    if result.startswith(prefix):
        result = result[len(prefix):]
    if result.endswith("_1h"):
        result = result.replace("_1h", "")
    return result


def handle_message_logic(lat: float, lon: float):
    """
    Führt die Analyse aus und liefert Antworttext + KML-Dateipfad.
    Gibt (ergebnis_text, kml_path) zurück oder (fehlermeldung, None) bei Problem.
    """
    logger.info(f"📩 Anfrage für Koordinaten: {lat}, {lon}")

    # 1️⃣ Cache-Prüfung
    if has_cached_result(lat, lon):
        logger.info("✅ Cache-Hit – keine Analyse notwendig.")
        cache_dir = cache_path_for_latlon(lat, lon)
        for fname in os.listdir(cache_dir):
            if fname.endswith(".kml"):
                return "📦 Daten aus Cache gefunden.", os.path.join(cache_dir, fname)
        return "📦 Daten aus Cache gefunden – keine KML-Datei vorhanden.", None

    # 2️⃣ Analyse starten (Cache-Miss)
    try:
        result = classify_rain_stage()
        if not result:
            logger.warning("Kein Ergebnis von classify_rain_stage erhalten.")
            return "⚠️ Keine Auswertung möglich.", None

        if result.lower() == "schummerung":
            logger.info("Schummerung erkannt: keine KML gesendet.")
            return f"📍 Ergebnis: {result}\n⚠️ Keine Kartenausgabe für Schummerung.", None

        layer_key = normalize_layer_key(result)
        logger.info(f"Analyse erfolgreich: {result}")

        kml_filename = f"flood_{layer_key}.kml"
        kml_path = os.path.join(CACHE_DIR, kml_filename)
        if os.path.isfile(kml_path):
            return f"📍 Gefundener Layer: {result}", kml_path
        else:
            logger.warning(f"KML-Datei nicht gefunden für Layer {layer_key}.")
            return f"📍 Gefundener Layer: {result}\n⚠️ KML-Datei nicht gefunden.", None

    except Exception:
        logger.exception("Fehler bei Analyse")
        return "❌ Fehler bei der Analyse.", None


def run_bot():
    """Startet den Telegram-Bot (ruft IO-Adapter auf)."""
    from src.io.telegram_adapter import start_bot
    start_bot(handle_message_logic)
