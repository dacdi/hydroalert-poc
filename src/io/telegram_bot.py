from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


from src.config.config import TELEGRAM_BOT_TOKEN
from src.utils.utils_logger import get_logger

logger = get_logger()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👋 Willkommen bei HydroAlert! Sende mir einen Ort (z. B. 'Stuttgart').")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip().lower()

    if "stuttgart" in user_input:
        # ⬇ Hier wird später die Analyse eingebaut
        result = "📍 Stuttgart: SRI10 – Warnstufe 2"
    else:
        result = f"❌ Ort '{user_input}' nicht gefunden."

    await update.message.reply_text(result)


def run_bot() -> None:
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Telegram-Bot gestartet. Warte auf Nachrichten …")
    app.run_polling()
