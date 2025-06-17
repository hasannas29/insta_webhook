from flask import Flask, request
import requests
import openai
import os

app = Flask(__name__)

VERIFY_TOKEN = "nasifogullari_token"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        return "Token yanlış!", 403

    elif request.method == "POST":
        data = request.get_json()
        try:
            for entry in data.get("entry", []):
                for messaging in entry.get("messaging", []):
                    sender_id = messaging["sender"]["id"]
                    if "message" in messaging:
                        message_text = messaging["message"].get("text")
                        if message_text:
                            cevap = ask_gpt(message_text)
                            send_message(sender_id, cevap)
        except Exception as e:
            print("HATA:", e)
        return "OK", 200

def ask_gpt(metin):
    cevap = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Kısa, samimi, yardımcı bir Instagram DM asistanısın."},
            {"role": "user", "content": metin}
        ]
    )
    return cevap.choices[0].message.content.strip()

def send_message(kime, mesaj):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    data = {
        "recipient": {"id": kime},
        "message": {"text": mesaj}
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, json=data, headers=headers)
    print("Mesaj gönderildi:", r.text)

if __name__ == "__main__":
    app.run(port=5000)
