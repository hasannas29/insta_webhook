from flask import Flask, request
import openai
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = "nasifogullari_token"
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
            print("✅ WEBHOOK DOĞRULANDI")
            return request.args.get("hub.challenge"), 200
        print("❌ WEBHOOK DOĞRULAMA BAŞARISIZ")
        return "Verification token mismatch", 403

    if request.method == 'POST':
        try:
            print("📥 RAW DATA:", request.data)
            data = request.get_json()
            print("📦 PARSED JSON:", data)

            if data.get("object") == "instagram":
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        print("🔁 Değişiklik:", change)

                        if change.get("field") == "messages":
                            sender_id = change["value"]["sender"]["id"]
                            user_message = change["value"]["message"]["text"]
                            
                            print("👤 Gönderen:", sender_id)
                            print("💬 Mesaj:", user_message)

                            # GPT'ye gönder
                            reply = get_gpt_response(user_message)
                            print("🤖 GPT CEVABI:", reply)

                            # İsteğe bağlı: gerçek gönderim
                            # send_message(sender_id, reply)

            return "ok", 200

        except Exception as e:
            print("❌ HATA:", str(e))
            return "error", 500


def get_gpt_response(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen Nas Ajans'ın reklam danışmanısın. Kısa, net, ikna edici cevaplar ver."},
                {"role": "user", "content": message}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print("❌ GPT HATASI:", e)
        return "Cevap verilemedi."


def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print("📤 MESAJ GÖNDERİLDİ:", response.status_code, response.text)
    except Exception as e:
        print("❌ MESAJ GÖNDERME HATASI:", e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
