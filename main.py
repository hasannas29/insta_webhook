from flask import Flask, request
import requests
import openai
import os
import time
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Sabit ayarlar
VERIFY_TOKEN = "nasifogullari_token"
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Flask uygulaması
app = Flask(__name__)

# 🛡️ Kullanıcı mesaj zamanları (basit rate limit için)
user_last_message_time = {}
RATE_LIMIT_SECONDS = 30  # 30 saniyede birden fazla mesaj atanı engeller

# 📢 GPT'ye verilecek ikna odaklı prompt
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
    - Her cevabın kısa, ikna edici ve harekete geçirici olmalı.
    - Asla yapay zekâ olduğunu belirtme.

    Cevaplarını sıcak, samimi ama profesyonel tut.
    Sonunda mutlaka harekete geçirici bir çağrı ekle: "İstersen sana özel plan yapalım", "Uygun musun hemen başlayalım?" gibi.
    """

# GPT'den cevap al
def get_gpt_response(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": get_prompt()},
                {"role": "user", "content": user_message}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print("GPT Hatası:", e)
        return "Şu anda teknik bir problem yaşıyoruz, birazdan tekrar dene lütfen."

# Meta mesaj gönder
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
        print("Meta API Hatası:", e)

# Webhook doğrulama
@app.route('/', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge'), 200
    return 'Invalid verification token', 403

# Webhook mesaj işleme
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json

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
                                # Spam atıyorsa uyar, cevap verme
                                warning = "Lütfen mesajlarınızı peş peşe göndermeyin. Yanıtlamak için zaman tanıyın. 🙂"
                                send_message(sender_id, warning)
                            else:
                                # Zaman güncelle ve cevabı gönder
                                user_last_message_time[sender_id] = now
                                reply = get_gpt_response(user_message)
                                send_message(sender_id, reply)

        return "ok", 200
    except Exception as e:
        print("Webhook Hatası:", e)
        return "ok", 200  # Meta hata dönerse webhook devre dışı kalır, her zaman 200 dön!

# Render çalıştırması
if __name__ == '__main__':
    app.run(debug=True)
