from flask import Flask, request
import requests
import openai
import os

app = Flask(__name__)

# Doğrulama için kullanılacak token
VERIFY_TOKEN = "nasifogullari_token"

# Ortam değişkenlerinden access token ve OpenAI API key'i al
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/', methods=['GET'])
def home():
    return "Webhook endpoint is working", 200

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
        print("\n=== Gelen Veri ===\n", data)
        try:
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]
                        message_text = messaging_event["message"].get("text")
                        if message_text:
                            reply = ask_gpt(message_text)
                            send_message(sender_id, reply)
        except Exception as e:
            print("\n!!! HATA !!!\n", str(e))
        return "OK", 200

def ask_gpt(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir Instagram destek asistanısın. Kısa, samimi, net cevaplar ver."},
                {"role": "user", "content": message}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print("\n[OpenAI Hatası]", str(e))
        return "Şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."

def send_message(user_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    data = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=data, headers=headers)
        print("\n=== Facebook Yanıtı ===\n", response.status_code, response.text)
    except Exception as e:
        print("\n[Facebook API Hatası]", str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
