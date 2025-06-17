from flask import Flask, request
import requests
import openai
import os

app = Flask(__name__)

VERIFY_TOKEN = "nasifogullari_token"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        return "Token yanlış!", 403

    elif request.method == 'POST':
        data = request.get_json()
        try:
            for entry in data["entry"]:
                for msg in entry["messaging"]:
                    if "message" in msg:
                        sender_id = msg["sender"]["id"]
                        message_text = msg["message"].get("text")
                        if message_text:
                            cevap = ask_gpt(message_text)
                            send_message(sender_id, cevap)
        except Exception as e:
            print("HATA:", e)
        return "OK", 200

def ask_gpt(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sen bir Instagram müşteri destek asistanısın. Kısa, samimi ve net cevaplar ver."},
            {"role": "user", "content": message}
        ]
    )
    return response["choices"][0]["message"]["content"]

def send_message(user_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    data = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=data, headers=headers)

# ✅ BU KISIM ZORUNLU: Render için portu 0.0.0.0'da aç
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
