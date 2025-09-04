# src/io/telegram_adapter.py
from __future__ import annotations
from typing import Iterable, Awaitable, Callable
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update

from src.domain.actions import BotAction, SendText, SendPhoto, SendDocument
from src.utils.utils_logger import get_logger

logger = get_logger()

async def _render_actions(update: Update, actions: Iterable[BotAction]) -> None:
    if update.message is None:
        logger.debug("No message on update; skip rendering.")
        return
    for act in actions:
        if isinstance(act, SendText):
            await update.message.reply_text(act.text)
        elif isinstance(act, SendPhoto):
            with open(act.path, "rb") as f:
                await update.message.reply_photo(photo=f, caption=act.caption or "")
        elif isinstance(act, SendDocument):
            with open(act.path, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=act.filename or None,
                    caption=act.caption or "",
                )
        else:
            logger.warning("Unknown action type: %r", type(act))

def run(app_token: str, on_text: Callable[[int, str], Awaitable[Iterable[BotAction]]]) -> None:
    """
    Dünner Adapter: synchroner Start. PTB verwaltet den asyncio-Loop selbst.
    """
    app = ApplicationBuilder().token(app_token).build()

    async def _on_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id if update.effective_chat else 0
        logger.info("Start command from chat_id=%s", chat_id)
        # Lokal importieren, um Zyklen zu vermeiden
        from src.use_cases.telegram_bot import handle_start
        actions = await handle_start(chat_id)
        await _render_actions(update, actions)

    async def _on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id if update.effective_chat else 0
        text = (update.message.text or "").strip() if update.message else ""
        logger.debug("Message from chat_id=%s: %r", chat_id, text)
        actions = await on_text(chat_id, text)
        await _render_actions(update, actions)

    app.add_handler(CommandHandler("start", _on_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _on_message))

    logger.info("🚀 Telegram adapter running (polling).")
    app.run_polling()  # <-- blockierend, verwaltet eigenen Event-Loop
