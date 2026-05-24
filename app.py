import os
import random
import string
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "8854508747:AAGP-bcbVFhzYZYteVpJzK3IV0zmFJIkHmw"
CHAT_ID = "8486336204"

user_mails = {}

def send_telegram_with_keyboard(text):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "keyboard": [
                [{"text": "📧 Generate"}, {"text": "❌ Delete current email"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
    }
    requests.post(url, json=payload)

@app.route('/mail-yakala', methods=['POST'])
def handle_inbound_email():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        sender = data.get('Sender', {}).get('Address', 'Unknown Sender')
        subject = data.get('Subject', 'No Subject')
        body = data.get('RawTextBody', 'Empty Body')
        
        to_list = data.get('To', [])
        recipient = to_list.get('Address', '').lower() if to_list else ''
        
        active_mail = user_mails.get(CHAT_ID, "").lower()
        if active_mail and recipient == active_mail:
            telegram_message = (
                f"📩 *New Email Received!*\n\n"
                f"*To:* `{recipient}`\n"
                f"*From:* {sender}\n"
                f"*Subject:* {subject}\n\n"
                f"*Message / Code:* \n{body}"
            )
            send_telegram_with_keyboard(telegram_message)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telegram-webhook', methods=['POST'])
def handle_telegram_webhook():
    try:
        data = request.json
        if "message" in data:
            chat_id = str(data["message"]["chat"]["id"])
            text = data["message"].get("text", "")

            if chat_id != CHAT_ID:
                return jsonify({"status": "ignored"}), 200

            if text == "/start":
                welcome_text = (
                    "👋 *Fake Mail Bot Welcome!*\n\n"
                    "Use buttons below to generate a temporary email address.\n\n"
                    "👇 Press *📧 Generate* to start!"
                )
                send_telegram_with_keyboard(welcome_text)

            elif text == "📧 Generate" or text == "/generate":
                random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                generated_email = f"{random_name}@pusheralsat.xyz"
                user_mails[CHAT_ID] = generated_email
                
                msg = (
                    f"🎲 *Your Temporary Email Address:*\n\n"
                    f"`{generated_email}`\n\n"
                    f"Click to copy. All validation codes and emails will arrive here instantly."
                )
                send_telegram_with_keyboard(msg)

            elif text == "❌ Delete current email" or text == "/sil":
                if CHAT_ID in user_mails:
                    del user_mails[CHAT_ID]
                    send_telegram_with_keyboard("❌ Current email address deleted successfully.")
                else:
                    send_telegram_with_keyboard("⚠️ You don't have an active email address.")

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
