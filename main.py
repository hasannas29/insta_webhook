from flask import Flask, request
import requests
import openai
import os

app = Flask(__name__)

VERIFY_TOKEN = "nasifogullari_token"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Meta Webhook doğrulama (GET)
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
            print("WEBHOOK DOĞRULANDI ✅")
            return request.args.get("hub.challenge")
        print("❌ WEBHOOK DOĞRULAMA BAŞARISIZ")
        return "Verification token mismatch", 403

    # POST: mesaj işleme
    if request.method == 'POST':
        data = request.get_json()
        print("📩 Gelen VERİ:", data)

        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        sender_id = change["value"]["sender"]["id"]
                        user_message = change["value"]["message"]["text"]

                        # GPT yanıtı al
                        reply = get_gpt_response(user_message)

                        # Mesajı gönder
                        send_message(sender_id, reply)
        return "ok", 200


# GPT yanıtı üret
def get_gpt_response(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen Instagram müşteri asistanısın. Kısa, net ve kibarca cevap ver."},
                {"role": "user", "content": user_message}
            ]
        )
        result = response['choices'][0]['message']['content']
        print("✅ GPT CEVABI:", result)
        return result
    except Exception as e:
        print("❌ GPT HATASI:", e)
        return "Şu anda teknik bir problem yaşıyoruz, birazdan tekrar dene lütfen."


# Instagram'a cevap gönder
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📤 Mesaj gönderildi:", response.text)


# Sunucu başlat (Render uyumlu)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
