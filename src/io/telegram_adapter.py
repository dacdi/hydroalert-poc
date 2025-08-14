# src/io/telegram_adapter.py

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from src.config.config import TELEGRAM_BOT_TOKEN
from src.utils.utils_logger import get_logger

logger = get_logger()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sendet die Begrüßungsnachricht an den Nutzer."""
    await update.message.reply_text(
        "👋 Willkommen bei HydroAlert! Ich erstelle Sturzregenvorhersagen für Neustadt."
    )


def start_bot(message_logic_fn):
    """
    Startet den Telegram-Bot.

    Args:
        message_logic_fn: Funktion, die (antwort_text, kml_path) zurückgibt.
    """

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_input = update.message.text.strip()
        logger.debug(f"Eingehende Nachricht von {update.effective_user.username}: {user_input}")

        text, kml_path = message_logic_fn(user_input)

        # Haupttext senden
        await update.message.reply_text(text)

        # Falls vorhanden, KML-Datei senden
        if kml_path:
            try:
                with open(kml_path, "rb") as file:
                    await update.message.reply_document(
                        document=file,
                        filename=kml_path.split("/")[-1],
                        caption="Hier die KML-Datei."
                    )
                logger.info(f"KML-Datei gesendet: {kml_path}")
            except FileNotFoundError:
                logger.warning(f"KML-Datei nicht gefunden: {kml_path}")
                await update.message.reply_text("⚠️ KML-Datei nicht gefunden.")

    # Bot konfigurieren
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Telegram-Bot gestartet. Warte auf Nachrichten …")
    app.run_polling()
