import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "8954675951:AAGCQ8-puBkBLV_BNLnwbNu5U9CfzHnb4t0"
CHAT_ID = "8486336204"

def send_telegram_message(text):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
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
        
        telegram_message = (
            f"📩 *New Email Received!*\n\n"
            f"*To:* `{recipient}`\n"
            f"*From:* {sender}\n"
            f"*Subject:* {subject}\n\n"
            f"*Message / Code:* \n{body}"
        )
        send_telegram_message(telegram_message)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
