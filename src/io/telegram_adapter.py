# src/io/telegram_adapter.py

from __future__ import annotations

import re
from typing import Dict, Tuple, Optional

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from src.config.config import TELEGRAM_BOT_TOKEN
from src.utils.utils_logger import get_logger
from src.io.llm_client import llm_hint_for

logger = get_logger()

# Einfache, flüchtige Sitzungszustände pro Chat
# {chat_id: {"awaiting_confirm": bool, "lat": float, "lon": float}}
_STATE: Dict[int, Dict[str, object]] = {}


_COORD_RE = re.compile(r"^\s*([+-]?\d{1,2}\.\d+)\s*[,; ]\s*([+-]?\d{1,3}\.\d+)\s*$")


def parse_lat_lon_strict(text: str) -> Optional[Tuple[float, float]]:
    """Parst *strikt* Dezimalgrad mit Dezimalpunkt und prüft Wertebereiche.
    
    Akzeptiert: "48.1351, 11.5820" oder "48.1351 11.5820" etc.
    Liefert None, wenn Format/Wertebereich nicht passen.
    """
    m = _COORD_RE.match(text or "")
    if not m:
        return None
    try:
        lat = float(m.group(1))
        lon = float(m.group(2))
    except ValueError:
        return None
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None
    return round(lat, 5), round(lon, 5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Willkommen bei HydroAlert!\n"
        "Bitte gib Koordinaten im Format `lat, lon` ein (z. B. `48.1351, 11.5820`).\n"
        "Regeln: DezimalPUNKT (.), erst lat, dann lon."
    )


def _clear(chat_id: int) -> None:
    _STATE.pop(chat_id, None)


def _set_pending(chat_id: int, lat: float, lon: float) -> None:
    _STATE[chat_id] = {"awaiting_confirm": True, "lat": lat, "lon": lon}


def _get_pending(chat_id: int) -> Optional[Tuple[float, float]]:
    s = _STATE.get(chat_id)
    if s and s.get("awaiting_confirm") and "lat" in s and "lon" in s:
        return float(s["lat"]), float(s["lon"])  # type: ignore[arg-type]
    return None


def start_bot(message_logic_fn):
    """Startet den Telegram-Bot.
    
    :param message_logic_fn: Funktion, die (lat, lon) → (text, file_path|None) zurückgibt.
    """
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id if update.effective_chat else 0
        user_input = (update.message.text or "").strip()
        logger.debug("📩 Eingehende Nachricht [chat=%s]: %s", chat_id, user_input)

        # Prüfe, ob wir auf eine Bestätigung warten
        pending = _get_pending(chat_id)
        if pending:
            if user_input.lower() == "ja":
                lat, lon = pending
                _clear(chat_id)
                logger.info("✅ Bestätigt: lat=%.5f, lon=%.5f [chat=%s]", lat, lon, chat_id)
                text, file_path = message_logic_fn(lat, lon)

                # Haupttext senden
                await update.message.reply_text(text)

                # (Optional) Datei anhängen
                if file_path:
                    try:
                        with open(file_path, "rb") as f:
                            await update.message.reply_document(
                                document=f,
                                filename=file_path.split("/")[-1],
                                caption="Ergebnisdatei",
                            )
                    except FileNotFoundError:
                        logger.warning("Datei nicht gefunden: %s", file_path)
                        await update.message.reply_text("⚠️ Datei nicht gefunden.")
                return
            else:
                # Nutzer will korrigieren → fallen through zu neuer Parsing-Runde
                logger.debug("↩️ Nutzer korrigiert Eingabe, verwerfe Pending [chat=%s]", chat_id)
                _clear(chat_id)

        # Neue Eingabe → Parse versuch
        parsed = parse_lat_lon_strict(user_input)
        if not parsed:
            # Ungültig → LLM um knappen Tipp bitten
            hint = llm_hint_for(user_input)
            await update.message.reply_text(hint)
            return

        lat, lon = parsed
        _set_pending(chat_id, lat, lon)
        await update.message.reply_text(
            f"Habe: {lat:.5f}, {lon:.5f}. Richtig? Antworte 'ja' oder sende neue Werte."
        )

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Telegram-Bot gestartet. Warte auf Nachrichten …")
    app.run_polling()
