# coding: utf-8
# Smartico Big Win -> Telegram Notification
# Supports two endpoints:
#   /webhook/bigwin     - regular Big Win
#   /webhook/bigwin-vip - VIP Big Win (separate bot and chat)

import os
import logging
from flask import Flask, request, jsonify
import requests

# --- Config ------------------------------------------------------------------

TELEGRAM_BOT_TOKEN     = os.getenv("TELEGRAM_BOT_TOKEN",     "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID       = os.getenv("TELEGRAM_CHAT_ID",       "YOUR_CHAT_ID_HERE")
TELEGRAM_VIP_BOT_TOKEN = os.getenv("TELEGRAM_VIP_BOT_TOKEN", "YOUR_VIP_BOT_TOKEN_HERE")
TELEGRAM_VIP_CHAT_ID   = os.getenv("TELEGRAM_VIP_CHAT_ID",   "YOUR_VIP_CHAT_ID_HERE")
PORT                   = int(os.getenv("PORT", 5000))

# --- Logging -----------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- Helpers -----------------------------------------------------------------

def send_telegram_message(bot_token, chat_id, text):
    url = "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Telegram message sent successfully.")
        return True
    except requests.RequestException as e:
        logger.error("Failed to send Telegram message: {}".format(e))
        return False


def get_params():
    return {
        "player_id":               request.args.get("player_id",               "N/A"),
        "win_amount":              request.args.get("win_amount",              "N/A"),
        "total_balance":           request.args.get("total_balance",           "N/A"),
        "last_deposit":            request.args.get("last_deposit",            "N/A"),
        "total_deposit_count":     request.args.get("total_deposit_count",     "N/A"),
        "total_deposit_amount":    request.args.get("total_deposit_amount",    "N/A"),
        "total_withdrawal_count":  request.args.get("total_withdrawal_count",  "N/A"),
        "total_withdrawal_amount": request.args.get("total_withdrawal_amount", "N/A"),
        "net_deposit_amount":      request.args.get("net_deposit_amount",      "N/A"),
    }


def format_message(p, is_vip=False):
    if is_vip:
        title = "\U0001f451 <b>BIG WIN VIP!</b>"
        tag   = "#BigWinVIP #VIP #Smartico"
    else:
        title = "\U0001f3c6 <b>BIG WIN!</b>"
        tag   = "#BigWin #Smartico"
    return (
        "{}\n"
        "----------------\n"
        "\U0001f464 <b>ID:</b> <code>{}</code>\n"
        "\U0001f4b0 <b>Win amount:</b> <b>{}</b>\n"
        "\U0001f3e6 <b>Balance:</b> {}\n"
        "----------------\n"
        "\U0001f4ca <b>Player stats:</b>\n"
        "  \U0001f4b3 Last deposit: {}\n"
        "  \U0001f522 Deposit count: {}\n"
        "  \U0001f4b5 Total deposits: {}\n"
        "  \U0001f504 Withdrawal count: {}\n"
        "  \U0001f4e4 Total withdrawals: {}\n"
        "  \U0001f4c8 Net deposit: {}\n"
        "----------------\n"
        "{}"
    ).format(
        title,
        p["player_id"], p["win_amount"], p["total_balance"],
        p["last_deposit"], p["total_deposit_count"], p["total_deposit_amount"],
        p["total_withdrawal_count"], p["total_withdrawal_amount"],
        p["net_deposit_amount"], tag,
    )

# --- Endpoints ---------------------------------------------------------------

@app.route("/webhook/bigwin", methods=["GET"])
def bigwin_webhook():
    p = get_params()
    logger.info("Big Win | player={} amount={}".format(p["player_id"], p["win_amount"]))
    success = send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, format_message(p, is_vip=False))
    if success:
        return jsonify({"status": "ok", "message": "Notification sent"}), 200
    return jsonify({"status": "error", "message": "Failed to send Telegram notification"}), 500


@app.route("/webhook/bigwin-vip", methods=["GET"])
def bigwin_vip_webhook():
    p = get_params()
    logger.info("Big Win VIP | player={} amount={}".format(p["player_id"], p["win_amount"]))
    success = send_telegram_message(TELEGRAM_VIP_BOT_TOKEN, TELEGRAM_VIP_CHAT_ID, format_message(p, is_vip=True))
    if success:
        return jsonify({"status": "ok", "message": "VIP Notification sent"}), 200
    return jsonify({"status": "error", "message": "Failed to send VIP Telegram notification"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# --- Run ---------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting server on port {}".format(PORT))
    app.run(host="0.0.0.0", port=PORT, debug=False)
