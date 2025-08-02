from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


from src.config.config import TELEGRAM_BOT_TOKEN
from src.utils.utils_logger import get_logger
from src.analysis.classify_rain_intensity import classify_rain_stage

logger = get_logger()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👋 Willkommen bei HydroAlert! Sende mir einen Ort (z. B. 'Stuttgart').")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip().lower()
    logger.info(f"📩 Eingehende Nachricht: {user_input}")

    try:
        result = classify_rain_stage()
        response = f"📍 Analyse für: {user_input}\n📊 Ergebnis: {result}"
        await update.message.reply_text(response)
        logger.info(f"✅ Analyse erfolgreich gesendet: {result}")
    except Exception as e:
        logger.exception("❌ Fehler bei der Regenanalyse")
        await update.message.reply_text("❌ Leider ist ein Fehler bei der Analyse aufgetreten.")



def run_bot() -> None:
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Telegram-Bot gestartet. Warte auf Nachrichten …")
    app.run_polling()
