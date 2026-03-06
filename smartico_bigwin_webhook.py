"""
Smartico Big Win → Telegram Notification
=========================================
Поддерживает два эндпоинта:
  /webhook/bigwin      — обычный Big Win
  /webhook/bigwin-vip  — Big Win VIP (отдельный бот и чат)
"""

import os
import logging
from flask import Flask, request, jsonify
import requests

# ─── Конфигурация ────────────────────────────────────────────────────────────

# Обычный Big Win
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID",   "YOUR_CHAT_ID_HERE")

# VIP Big Win
TELEGRAM_VIP_BOT_TOKEN = os.getenv("TELEGRAM_VIP_BOT_TOKEN", "YOUR_VIP_BOT_TOKEN_HERE")
TELEGRAM_VIP_CHAT_ID   = os.getenv("TELEGRAM_VIP_CHAT_ID",   "YOUR_VIP_CHAT_ID_HERE")

PORT = int(os.getenv("PORT", 5000))

# ─── Логирование ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ─── Хелперы ─────────────────────────────────────────────────────────────────

def send_telegram_message(bot_token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Telegram message sent successfully.")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


def get_params():
    """Извлекает общие параметры из GET-запроса."""
    return {
        "player_id":              request.args.get("player_id",              "N/A"),
        "win_amount":             request.args.get("win_amount",             "N/A"),
        "total_balance":          request.args.get("total_balance",          "N/A"),
        "last_deposit":           request.args.get("last_deposit",           "N/A"),
        "total_deposit_count":    request.args.get("total_deposit_count",    "N/A"),
        "total_deposit_amount":   request.args.get("total_deposit_amount",   "N/A"),
        "total_withdrawal_count": request.args.get("total_withdrawal_count", "N/A"),
        "total_withdrawal_amount":request.args.get("total_withdrawal_amount","N/A"),
        "net_deposit_amount":     request.args.get("net_deposit_amount",     "N/A"),
    }


def format_message(p: dict, is_vip: bool = False) -> str:
    title = "👑 <b>BIG WIN VIP!</b>" if is_vip else "🏆 <b>BIG WIN!</b>"
    tag   = "#BigWinVIP #VIP #Smartico" if is_vip else "#BigWin #Smartico"
    return (
        f"{title}\n"
        "━━━━━━━━━━━━━━━━\n"
        f"👤 <b>ID игрока:</b> <code>{p['player_id']}</code>\n"
        f"💰 <b>Сумма выигрыша:</b> <b>{p['win_amount']}</b>\n"
        f"🏦 <b>Баланс:</b> {p['total_balance']}\n"
        "━━━━━━━━━━━━━━━━\n"
        "📊 <b>Статистика игрока:</b>\n"
        f"  💳 Последний депозит: {p['last_deposit']}\n"
        f"  🔢 Кол-во депозитов: {p['total_deposit_count']}\n"
        f"  💵 Сумма депозитов: {p['total_deposit_amount']}\n"
        f"  🔄 Кол-во выводов: {p['total_withdrawal_count']}\n"
        f"  📤 Сумма выводов: {p['total_withdrawal_amount']}\n"
        f"  📈 Нетто депозит: {p['net_deposit_amount']}\n"
        "━━━━━━━━━━━━━━━━\n"
        f"{tag}"
    )

# ─── Эндпоинты ───────────────────────────────────────────────────────────────

@app.route("/webhook/bigwin", methods=["GET"])
def bigwin_webhook():
    p = get_params()
    logger.info(f"Big Win | player={p['player_id']} amount={p['win_amount']}")
    success = send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, format_message(p, is_vip=False))
    if success:
        return jsonify({"status": "ok", "message": "Notification sent"}), 200
    return jsonify({"status": "error", "message": "Failed to send Telegram notification"}), 500


@app.route("/webhook/bigwin-vip", methods=["GET"])
def bigwin_vip_webhook():
    p = get_params()
    logger.info(f"Big Win VIP | player={p['player_id']} amount={p['win_amount']}")
    success = send_telegram_message(TELEGRAM_VIP_BOT_TOKEN, TELEGRAM_VIP_CHAT_ID, format_message(p, is_vip=True))
    if success:
        return jsonify({"status": "ok", "message": "VIP Notification sent"}), 200
    return jsonify({"status": "error", "message": "Failed to send VIP Telegram notification"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ─── Запуск ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info(f"Starting Smartico Big Win Webhook server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)


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


def format_big_win_message(player_id: str, win_amount: str,
                            last_deposit: str, total_deposit_count: str,
                            total_deposit_amount: str, total_withdrawal_count: str,
                            total_withdrawal_amount: str, net_deposit_amount: str,
                            total_balance: str) -> str:
    """Формирует текст уведомления для Telegram."""
    return (
        "🏆 <b>BIG WIN!</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        f"👤 <b>ID игрока:</b> <code>{player_id}</code>\n"
        f"💰 <b>Сумма выигрыша:</b> <b>{win_amount}</b>\n"
        f"🏦 <b>Баланс:</b> {total_balance}\n"
        "━━━━━━━━━━━━━━━━\n"
        "📊 <b>Статистика игрока:</b>\n"
        f"  💳 Последний депозит: {last_deposit}\n"
        f"  🔢 Кол-во депозитов: {total_deposit_count}\n"
        f"  💵 Сумма депозитов: {total_deposit_amount}\n"
        f"  🔄 Кол-во выводов: {total_withdrawal_count}\n"
        f"  📤 Сумма выводов: {total_withdrawal_amount}\n"
        f"  📈 Нетто депозит: {net_deposit_amount}\n"
        "━━━━━━━━━━━━━━━━\n"
        "#BigWin #Smartico"
    )

# ─── Эндпоинты ───────────────────────────────────────────────────────────────

@app.route("/webhook/bigwin", methods=["GET"])
def bigwin_webhook():
    """
    Эндпоинт, который Smartico вызывает как Web Hook (GET).

    Ожидаемые query-параметры (настраиваются в Smartico Journey):
        player_id                — ID игрока (state.user_ext_id)
        win_amount               — сумма выигрыша (state.casino_last_win_amount)
        last_deposit             — последний депозит (state.acc_last_deposit_amount)
        total_deposit_count      — кол-во депозитов (state.acc_total_deposit_count)
        total_deposit_amount     — сумма депозитов (state.acc_total_deposit_amount)
        total_withdrawal_count   — кол-во выводов (state.acc_total_withdrawal_count)
        total_withdrawal_amount  — сумма выводов (state.acc_total_withdrawal_amount)
        net_deposit_amount       — нетто депозит (state.acc_net_deposit_amount)
    """

    # ── Проверка секрета ──────────────────────────────────────────────────
    if WEBHOOK_SECRET:
        incoming_secret = request.args.get("secret", "")
        if incoming_secret != WEBHOOK_SECRET:
            logger.warning("Webhook received with invalid secret.")
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # ── Получение параметров ──────────────────────────────────────────────
    player_id               = request.args.get("player_id",               "N/A")
    win_amount              = request.args.get("win_amount",              "N/A")
    last_deposit            = request.args.get("last_deposit",            "N/A")
    total_deposit_count     = request.args.get("total_deposit_count",     "N/A")
    total_deposit_amount    = request.args.get("total_deposit_amount",    "N/A")
    total_withdrawal_count  = request.args.get("total_withdrawal_count",  "N/A")
    total_withdrawal_amount = request.args.get("total_withdrawal_amount", "N/A")
    net_deposit_amount      = request.args.get("net_deposit_amount",      "N/A")
    total_balance           = request.args.get("total_balance",           "N/A")

    logger.info(f"Big Win received | player={player_id} amount={win_amount}")

    # ── Отправка в Telegram ───────────────────────────────────────────────
    message = format_big_win_message(
        player_id, win_amount,
        last_deposit, total_deposit_count, total_deposit_amount,
        total_withdrawal_count, total_withdrawal_amount, net_deposit_amount,
        total_balance
    )
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
