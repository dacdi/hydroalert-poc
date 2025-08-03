import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from src.config.config import TELEGRAM_BOT_TOKEN
from src.utils.utils_logger import get_logger
from src.analysis.classify_rain_intensity import classify_rain_stage

logger = get_logger()
# Pfad zum Cache-Verzeichnis
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Willkommen bei HydroAlert! Ich erstelle Sturzregenvorhersage für Neustadt."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip().lower()
    logger.info(f"📩 Eingehende Nachricht: {user_input}")

    try:
        result = classify_rain_stage()
        if not result:
            await update.message.reply_text(
                "⚠️ Keine Auswertung möglich."
            )
            logger.warning("Kein Ergebnis von classify_rain_stage erhalten.")
            return

        # Kein Map-Output bei Schummerung
        if result.lower() == 'schummerung':
            await update.message.reply_text(
                f"📍 Ergebnis: {result}\n⚠️ Keine Kartenausgabe für Schummerung."
            )
            logger.info("Schummerung erkannt: keine KML gesendet.")
            return

        # Dynamisches Kürzen: entferne Präfix 'Wassertiefe_' falls vorhanden
        layer_key = result
        prefix = 'Wassertiefe_'
        if layer_key.startswith(prefix):
            layer_key = layer_key[len(prefix):]
        # Standardisiere SRI7_1h zu SRI7
        if layer_key.endswith('_1h'):
            layer_key = layer_key.replace('_1h', '')

        # Textantwort senden
        await update.message.reply_text(
            f"📍 Gefundener Layer: {result}"
        )
        logger.info(f"Analyse erfolgreich: {result}")

        # KML-Datei senden
        kml_filename = f"flood_{layer_key}.kml"
        kml_path = os.path.join(CACHE_DIR, kml_filename)
        if os.path.isfile(kml_path):
            with open(kml_path, 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename=kml_filename,
                    caption=f"Hier die KML-Datei für Layer {layer_key}."
                )
            logger.info(f"KML-Datei gesendet: {kml_filename}")
        else:
            await update.message.reply_text(
                f"⚠️ KML-Datei für Layer {layer_key} nicht gefunden."
            )
            logger.warning(f"KML-Datei nicht gefunden für Layer {layer_key}.")

    except Exception:
        logger.exception("Fehler bei Analyse oder Dateiversand")
        await update.message.reply_text(
            "❌ Fehler bei der Analyse oder beim Senden der KML-Datei."
        )


def run_bot() -> None:
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🚀 Telegram-Bot gestartet. Warte auf Nachrichten …")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
