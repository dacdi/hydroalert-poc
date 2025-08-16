# src/io/telegram_adapter.py

import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from src.config.config import TELEGRAM_BOT_TOKEN
from src.utils.utils_logger import get_logger

logger = get_logger()


def parse_lat_lon_from_text(text: str):
    """
    Extrahiert lat/lon aus einem Textstring.
    Erwartet z.B.: '49.35, 8.15' oder '49.35 8.15'
    """
    match = re.search(r"(-?\d+(?:\.\d+)?)\D+(-?\d+(?:\.\d+)?)", text)
    if match:
        try:
            lat = float(match.group(1))
            lon = float(match.group(2))
            return lat, lon
        except ValueError:
            return None, None
    return None, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Willkommen bei HydroAlert!\n"
        "Bitte gib Koordinaten im Format `lat, lon` ein (z. B. `49.35, 8.15`)."
    )


def start_bot(message_logic_fn):
    """
    Startet den Telegram-Bot.
    :param message_logic_fn: Funktion, die (lat, lon) → (text, file_path|None) zurückgibt.
    """
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_input = (update.message.text or "").strip()
        logger.debug("📩 Eingehende Nachricht: %s", user_input)

        lat, lon = parse_lat_lon_from_text(user_input)
        if lat is None or lon is None:
            await update.message.reply_text("⚠️ Bitte Koordinaten im Format 'lat, lon' eingeben.")
            return

        text, file_path = message_logic_fn(lat, lon)

        # Haupttext senden
        await update.message.reply_text(text)

        # (Optional) Datei anhängen – aktuell liefern wir None zurück
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    await update.message.reply_document(
                        document=f,
                        filename=file_path.split("/")[-1],
                        caption="Ergebnisdatei"
                    )
            except FileNotFoundError:
                logger.warning("Datei nicht gefunden: %s", file_path)
                await update.message.reply_text("⚠️ Datei nicht gefunden.")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Telegram-Bot gestartet. Warte auf Nachrichten …")
    app.run_polling()
