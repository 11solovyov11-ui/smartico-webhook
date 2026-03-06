# coding: utf-8
# Smartico Big Win -> Telegram Notification
#
# Smartico WebHook URL (regular):
# https://smartico-webhook-production.up.railway.app/webhook/bigwin?player_id={{state.user_ext_id}}&win_amount={{state.casino_last_win_amount}}&total_balance={{state.acc_total_balance}}&last_deposit={{state.acc_last_deposit_amount}}&total_deposit_count={{state.acc_total_deposit_count}}&total_deposit_amount={{state.acc_total_deposit_amount}}&total_withdrawal_count={{state.acc_total_withdrawal_count}}&total_withdrawal_amount={{state.acc_total_withdrawal_amount}}&net_deposit_amount={{state.acc_net_deposit_amount}}
#
# Smartico WebHook URL (VIP):
# https://smartico-webhook-production.up.railway.app/webhook/bigwin-vip?player_id={{state.user_ext_id}}&win_amount={{state.casino_last_win_amount}}&total_balance={{state.acc_total_balance}}&last_deposit={{state.acc_last_deposit_amount}}&total_deposit_count={{state.acc_total_deposit_count}}&total_deposit_amount={{state.acc_total_deposit_amount}}&total_withdrawal_count={{state.acc_total_withdrawal_count}}&total_withdrawal_amount={{state.acc_total_withdrawal_amount}}&net_deposit_amount={{state.acc_net_deposit_amount}}

import os
import logging
from flask import Flask, request, jsonify
import requests

TELEGRAM_BOT_TOKEN     = os.getenv("TELEGRAM_BOT_TOKEN",     "")
TELEGRAM_CHAT_ID       = os.getenv("TELEGRAM_CHAT_ID",       "")
TELEGRAM_VIP_BOT_TOKEN = os.getenv("TELEGRAM_VIP_BOT_TOKEN", "")
TELEGRAM_VIP_CHAT_ID   = os.getenv("TELEGRAM_VIP_CHAT_ID",   "")
PORT                   = int(os.getenv("PORT", 5000))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)


def send_telegram_message(bot_token, chat_id, text):
    url = "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error("Failed: {}".format(e))
        return False


def get_params():
    return {
        "player_id":               request.args.get("state.user_ext_id",               "N/A"),
        "win_amount":              request.args.get("state.casino_last_win_amount",     "N/A"),
        "total_balance":           request.args.get("state.acc_total_balance",          "N/A"),
        "last_deposit":            request.args.get("state.acc_last_deposit_amount",    "N/A"),
        "total_deposit_count":     request.args.get("state.acc_total_deposit_count",    "N/A"),
        "total_deposit_amount":    request.args.get("state.acc_total_deposit_amount",   "N/A"),
        "total_withdrawal_count":  request.args.get("state.acc_total_withdrawal_count", "N/A"),
        "total_withdrawal_amount": request.args.get("state.acc_total_withdrawal_amount","N/A"),
        "net_deposit_amount":      request.args.get("state.acc_net_deposit_amount",     "N/A"),
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


@app.route("/webhook/bigwin", methods=["GET"])
def bigwin_webhook():
    p = get_params()
    success = send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, format_message(p, is_vip=False))
    if success:
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 500


@app.route("/webhook/bigwin-vip", methods=["GET"])
def bigwin_vip_webhook():
    p = get_params()
    success = send_telegram_message(TELEGRAM_VIP_BOT_TOKEN, TELEGRAM_VIP_CHAT_ID, format_message(p, is_vip=True))
    if success:
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
