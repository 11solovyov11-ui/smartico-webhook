# coding: utf-8
import os
import logging
from flask import Flask, request, jsonify
import requests

# --- Config ------------------------------------------------------------------

TELEGRAM_BOT_TOKEN        = os.getenv("TELEGRAM_BOT_TOKEN",        "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID          = os.getenv("TELEGRAM_CHAT_ID",          "YOUR_CHAT_ID_HERE")
TELEGRAM_VIP_BOT_TOKEN    = os.getenv("TELEGRAM_VIP_BOT_TOKEN",    "YOUR_VIP_BOT_TOKEN_HERE")
TELEGRAM_VIP_CHAT_ID      = os.getenv("TELEGRAM_VIP_CHAT_ID",      "YOUR_VIP_CHAT_ID_HERE")
TELEGRAM_DEPOSIT_BOT_TOKEN = os.getenv("TELEGRAM_DEPOSIT_BOT_TOKEN", "YOUR_DEPOSIT_BOT_TOKEN_HERE")
TELEGRAM_DEPOSIT_CHAT_ID   = os.getenv("TELEGRAM_DEPOSIT_CHAT_ID",   "YOUR_DEPOSIT_CHAT_ID_HERE")
PORT                       = int(os.getenv("PORT", 5000))

TELEGRAM_API_URL     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
TELEGRAM_VIP_API_URL = f"https://api.telegram.org/bot{TELEGRAM_VIP_BOT_TOKEN}/sendMessage"
TELEGRAM_DEP_API_URL = f"https://api.telegram.org/bot{TELEGRAM_DEPOSIT_BOT_TOKEN}/sendMessage"

# --- Logging -----------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- Helpers -----------------------------------------------------------------

def send_telegram_message(api_url, chat_id, text):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(api_url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Telegram message sent successfully.")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


def format_big_win_message(player_id, win_amount, last_deposit, total_deposit_count,
                            total_deposit_amount, total_withdrawal_count, total_withdrawal_amount,
                            net_deposit_amount, total_balance, is_vip=False):
    if is_vip:
        header = "\U0001f451 <b>BIG WIN VIP!</b>"
        footer = "#BigWinVIP #VIP #Smartico"
    else:
        header = "\U0001f3c6 <b>BIG WIN!</b>"
        footer = "#BigWin #Smartico"
    return (
        f"{header}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f464 <b>ID \u0438\u0433\u0440\u043e\u043a\u0430:</b> <code>{player_id}</code>\n"
        f"\U0001f4b0 <b>\u0421\u0443\u043c\u043c\u0430 \u0432\u044b\u0438\u0433\u0440\u044b\u0448\u0430:</b> <b>{win_amount}</b>\n"
        f"\U0001f3e6 <b>\u0411\u0430\u043b\u0430\u043d\u0441:</b> {total_balance}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4ca <b>\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u0438\u0433\u0440\u043e\u043a\u0430:</b>\n"
        f"  \U0001f4b3 \u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 \u0434\u0435\u043f\u043e\u0437\u0438\u0442: {last_deposit}\n"
        f"  \U0001f522 \u041a\u043e\u043b-\u0432\u043e \u0434\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0432: {total_deposit_count}\n"
        f"  \U0001f4b5 \u0421\u0443\u043c\u043c\u0430 \u0434\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0432: {total_deposit_amount}\n"
        f"  \U0001f504 \u041a\u043e\u043b-\u0432\u043e \u0432\u044b\u0432\u043e\u0434\u043e\u0432: {total_withdrawal_count}\n"
        f"  \U0001f4e4 \u0421\u0443\u043c\u043c\u0430 \u0432\u044b\u0432\u043e\u0434\u043e\u0432: {total_withdrawal_amount}\n"
        f"  \U0001f4c8 \u041d\u0435\u0442\u0442\u043e \u0434\u0435\u043f\u043e\u0437\u0438\u0442: {net_deposit_amount}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"{footer}"
    )


def format_big_deposit_message(player_id, balance, last_deposit, deposit_count,
                                deposit_amount, withdrawal_count, withdrawal_amount, net_deposit):
    return (
        f"\U0001f4b8 <b>BIG DEPOSIT!</b>\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f464 <b>ID \u0438\u0433\u0440\u043e\u043a\u0430:</b> <code>{player_id}</code>\n"
        f"\U0001f3e6 <b>\u0411\u0430\u043b\u0430\u043d\u0441:</b> {balance}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4ca <b>\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u0438\u0433\u0440\u043e\u043a\u0430:</b>\n"
        f"  \U0001f4b3 \u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 \u0434\u0435\u043f\u043e\u0437\u0438\u0442: {last_deposit}\n"
        f"  \U0001f522 \u041a\u043e\u043b-\u0432\u043e \u0434\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0432: {deposit_count}\n"
        f"  \U0001f4b5 \u0421\u0443\u043c\u043c\u0430 \u0434\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0432: {deposit_amount}\n"
        f"  \U0001f504 \u041a\u043e\u043b-\u0432\u043e \u0432\u044b\u0432\u043e\u0434\u043e\u0432: {withdrawal_count}\n"
        f"  \U0001f4e4 \u0421\u0443\u043c\u043c\u0430 \u0432\u044b\u0432\u043e\u0434\u043e\u0432: {withdrawal_amount}\n"
        f"  \U0001f4c8 \u041d\u0435\u0442\u0442\u043e \u0434\u0435\u043f\u043e\u0437\u0438\u0442: {net_deposit}\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"#BigDeposit #Smartico"
    )

# --- Endpoints ---------------------------------------------------------------

@app.route("/webhook/bigwin", methods=["GET"])
def bigwin_webhook():
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
    message = format_big_win_message(
        player_id, win_amount, last_deposit, total_deposit_count,
        total_deposit_amount, total_withdrawal_count, total_withdrawal_amount,
        net_deposit_amount, total_balance, is_vip=False
    )
    success = send_telegram_message(TELEGRAM_API_URL, TELEGRAM_CHAT_ID, message)
    if success:
        return jsonify({"status": "ok", "message": "Notification sent"}), 200
    return jsonify({"status": "error", "message": "Failed to send Telegram notification"}), 500


@app.route("/webhook/bigwin-vip", methods=["GET"])
def bigwin_vip_webhook():
    player_id               = request.args.get("player_id",               "N/A")
    win_amount              = request.args.get("win_amount",              "N/A")
    last_deposit            = request.args.get("last_deposit",            "N/A")
    total_deposit_count     = request.args.get("total_deposit_count",     "N/A")
    total_deposit_amount    = request.args.get("total_deposit_amount",    "N/A")
    total_withdrawal_count  = request.args.get("total_withdrawal_count",  "N/A")
    total_withdrawal_amount = request.args.get("total_withdrawal_amount", "N/A")
    net_deposit_amount      = request.args.get("net_deposit_amount",      "N/A")
    total_balance           = request.args.get("total_balance",           "N/A")
    logger.info(f"Big Win VIP received | player={player_id} amount={win_amount}")
    message = format_big_win_message(
        player_id, win_amount, last_deposit, total_deposit_count,
        total_deposit_amount, total_withdrawal_count, total_withdrawal_amount,
        net_deposit_amount, total_balance, is_vip=True
    )
    success = send_telegram_message(TELEGRAM_VIP_API_URL, TELEGRAM_VIP_CHAT_ID, message)
    if success:
        return jsonify({"status": "ok", "message": "VIP Notification sent"}), 200
    return jsonify({"status": "error", "message": "Failed to send VIP Telegram notification"}), 500


@app.route("/webhook/bigdeposit", methods=["GET"])
def bigdeposit_webhook():
    player_id         = request.args.get("player_id",         "N/A")
    balance           = request.args.get("balance",           "N/A")
    last_deposit      = request.args.get("last_deposit",      "N/A")
    deposit_count     = request.args.get("deposit_count",     "N/A")
    deposit_amount    = request.args.get("deposit_amount",    "N/A")
    withdrawal_count  = request.args.get("withdrawal_count",  "N/A")
    withdrawal_amount = request.args.get("withdrawal_amount", "N/A")
    net_deposit       = request.args.get("net_deposit",       "N/A")
    logger.info(f"Big Deposit received | player={player_id} balance={balance}")
    message = format_big_deposit_message(
        player_id, balance, last_deposit, deposit_count,
        deposit_amount, withdrawal_count, withdrawal_amount, net_deposit
    )
    success = send_telegram_message(TELEGRAM_DEP_API_URL, TELEGRAM_DEPOSIT_CHAT_ID, message)
    if success:
        return jsonify({"status": "ok", "message": "Deposit notification sent"}), 200
    return jsonify({"status": "error", "message": "Failed to send deposit notification"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    logger.info(f"Starting Smartico Big Win Webhook server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
