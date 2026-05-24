import os
import random
import string
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "8854508747:AAGP-bcbVFhzYZYteVpJzK3IV0zmFJIkHmw"
user_mails = {}

def send_telegram_with_keyboard(chat_id, text):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
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

@app.route('/', methods=['POST', 'GET'])
def handle_telegram_webhook():
    if request.method == 'POST':
        try:
            data = request.json
            
            # 1. BREVO'DAN GELEN MAILLERİ YAKALAMA
            if data and 'Sender' in data and 'Subject' in data:
                sender = data.get('Sender', {}).get('Address', 'Unknown Sender')
                subject = data.get('Subject', 'No Subject')
                body = data.get('RawTextBody', 'Empty Body')
                to_list = data.get('To', [])
                recipient = to_list.get('Address', '').lower() if to_list else ''
                
                for cid, active_mail in user_mails.items():
                    if active_mail and recipient == active_mail.lower():
                        telegram_message = (
                            f"📩 *New Email Received!*\n\n"
                            f"*To:* `{recipient}`\n"
                            f"*From:* {sender}\n"
                            f"*Subject:* {subject}\n\n"
                            f"*Message / Code:* \n{body}"
                        )
                        send_telegram_with_keyboard(cid, telegram_message)
                return jsonify({"status": "success"}), 200

            # 2. TELEGRAM'DAN GELEN MESAJLARI YAKALAMA
            if data and "message" in data:
                chat_id = str(data["message"]["chat"]["id"])
                text = data["message"].get("text", "")

                if text == "/start":
                    welcome_text = (
                        "👋 *Fake Mail Bot Welcome!*\n\n"
                        "Use buttons below to generate a temporary email address.\n\n"
                        "👇 Press *📧 Generate* to start!"
                    )
                    send_telegram_with_keyboard(chat_id, welcome_text)

                elif text == "📧 Generate" or text == "/generate":
                    random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                    generated_email = f"{random_name}@pusheralsat.xyz"
                    user_mails[chat_id] = generated_email
                    
                    msg = (
                        f"🎲 *Your Temporary Email Address:*\n\n"
                        f"`{generated_email}`\n\n"
                        f"Click to copy. All validation codes and emails will arrive here instantly."
                    )
                    send_telegram_with_keyboard(chat_id, msg)

                elif text == "❌ Delete current email" or text == "/sil":
                    if chat_id in user_mails:
                        del user_mails[chat_id]
                        send_telegram_with_keyboard(chat_id, "❌ Current email address deleted successfully.")
                    else:
                        send_telegram_with_keyboard(chat_id, "⚠️ You don't have an active email address.")

            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "running"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
