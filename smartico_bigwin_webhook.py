"""
Smartico Big Win → Telegram Notification
=========================================
Сервер принимает GET-запрос от Smartico (Journey Web Hook)
и пересылает уведомление о Big Win в Telegram-чат/канал.

Запуск:
    pip install flask requests
    python smartico_bigwin_webhook.py

Настройка переменных окружения (или замени значения напрямую):
    TELEGRAM_BOT_TOKEN  — токен бота от @BotFather
    TELEGRAM_CHAT_ID    — ID чата/канала для уведомлений
    WEBHOOK_SECRET      — секретный ключ для защиты эндпоинта (опционально)
    PORT                — порт сервера (по умолчанию 5000)
"""

import os
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify
import requests

# ─── Конфигурация ────────────────────────────────────────────────────────────

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID",   "YOUR_CHAT_ID_HERE")
WEBHOOK_SECRET     = os.getenv("WEBHOOK_SECRET",      "")   # оставь пустым, если не нужен
PORT               = int(os.getenv("PORT",            5000))

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# ─── Логирование ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ─── Хелперы ─────────────────────────────────────────────────────────────────

def send_telegram_message(text: str) -> bool:
    """Отправляет сообщение в Telegram. Возвращает True при успехе."""
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       text,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Telegram message sent successfully.")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


def format_big_win_message(player_id: str, player_name: str,
                            win_amount: str, game: str,
                            event_time: str) -> str:
    """Формирует текст уведомления для Telegram."""
    return (
        "🏆 <b>BIG WIN!</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Игрок:</b> {player_name} (ID: <code>{player_id}</code>)\n"
        f"💰 <b>Сумма выигрыша:</b> <b>{win_amount}</b>\n"
        f"🎮 <b>Игра:</b> {game}\n"
        f"🕐 <b>Время:</b> {event_time}\n"
        "━━━━━━━━━━━━━━━━\n"
        "#BigWin #Smartico"
    )

# ─── Эндпоинты ───────────────────────────────────────────────────────────────

@app.route("/webhook/bigwin", methods=["GET"])
def bigwin_webhook():
    """
    Эндпоинт, который Smartico вызывает как Web Hook (GET).

    Ожидаемые query-параметры (настраиваются в Smartico Journey):
        player_id    — ID игрока
        player_name  — имя игрока
        win_amount   — сумма выигрыша
        game         — название игры
        event_time   — время события (ISO или Unix timestamp; если пусто — берём текущее)
        secret       — секретный ключ (если WEBHOOK_SECRET задан)
    """

    # ── Проверка секрета ──────────────────────────────────────────────────
    if WEBHOOK_SECRET:
        incoming_secret = request.args.get("secret", "")
        if incoming_secret != WEBHOOK_SECRET:
            logger.warning("Webhook received with invalid secret.")
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # ── Получение параметров ──────────────────────────────────────────────
    player_id   = request.args.get("player_id",   "N/A")
    player_name = request.args.get("player_name", "Unknown")
    win_amount  = request.args.get("win_amount",  "N/A")
    game        = request.args.get("game",        "N/A")
    raw_time    = request.args.get("event_time",  "")

    # ── Парсинг времени ───────────────────────────────────────────────────
    if raw_time:
        try:
            # Пробуем Unix timestamp
            ts = float(raw_time)
            event_time = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        except ValueError:
            event_time = raw_time  # уже строка
    else:
        event_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    logger.info(
        f"Big Win received | player={player_name}({player_id}) "
        f"amount={win_amount} game={game} time={event_time}"
    )

    # ── Отправка в Telegram ───────────────────────────────────────────────
    message = format_big_win_message(player_id, player_name, win_amount, game, event_time)
    success = send_telegram_message(message)

    if success:
        return jsonify({"status": "ok", "message": "Notification sent"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to send Telegram notification"}), 500


@app.route("/health", methods=["GET"])
def health():
    """Проверка работоспособности сервера."""
    return jsonify({"status": "ok"}), 200


# ─── Запуск ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info(f"Starting Smartico Big Win Webhook server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
