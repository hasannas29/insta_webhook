from flask import Flask, request
import requests
import openai
import os
import time
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# Anahtarlar
VERIFY_TOKEN = "nasifogullari_token"
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Flask app
app = Flask(__name__)

# Rate limit için kullanıcı-zaman takibi
user_last_message_time = {}
RATE_LIMIT_SECONDS = 30  # saniye

# GPT prompt
def get_prompt():
    return """
    Sen Nasıfoğulları Reklam Ajansı'nın dijital reklam danışmanısın.

    Müşteri sana mesaj atıyor ve sen:
    - Sektörünü öğrenmeye çalışıyorsun,
    - Satış sorunları, sosyal medya problemleri, rakip baskısı gibi sıkıntılarını tespit ediyorsun,
    - Sonra Nasıfoğulları'nın sunduğu çözümleri anlatıyorsun:
        • Meta reklam yönetimi
        • Profesyonel tasarım
        • Dönüşüm artıran strateji
        • Sektöre özel hedefleme ve kampanya

    Cevapların kısa, ikna edici ve harekete geçirici olmalı.
    Samimi ama profesyonel konuş, asla yapay zekâ olduğunu söyleme.
    """

# GPT'den yanıt al
def get_gpt_response(user_message):
    try:
        print("📤 GPT'ye giden mesaj:", user_message)
       response = openai.ChatCompletion.create(
    model="gpt-4",
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

# Meta mesaj gönderme
def send_message(recipient_id, message_text):
    try:
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print("❌ Meta API HATASI:", e)

# Doğrulama (GET)
@app.route('/', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge'), 200
    return 'Invalid verification token', 403

# Mesaj işleme (POST)
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("📥 Gelen veri:", data)

        if data.get('object') == 'instagram':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    if value.get('field') == 'messages':
                        sender_id = value.get('sender', {}).get('id')
                        user_message = value.get('message', {}).get('text')

                        if sender_id and user_message:
                            now = time.time()
                            last_time = user_last_message_time.get(sender_id, 0)

                            if now - last_time < RATE_LIMIT_SECONDS:
                                warning = "Lütfen mesajlarınızı peş peşe göndermeyin. Yanıtlamak için zaman tanıyın. 🙂"
                                print("⚠️ Spam engellendi:", sender_id)
                                send_message(sender_id, warning)
                            else:
                                user_last_message_time[sender_id] = now
                                reply = get_gpt_response(user_message)
                                send_message(sender_id, reply)

        return "ok", 200
    except Exception as e:
        print("❌ Webhook HATASI:", e)
        return "ok", 200

# Uygulama başlat
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
