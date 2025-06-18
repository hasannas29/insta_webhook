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
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
            print("WEBHOOK DOĞRULANDI ✅")
            return request.args.get("hub.challenge")
        print("❌ WEBHOOK DOĞRULAMA BAŞARISIZ")
        return "Verification token mismatch", 403

    elif request.method == 'POST':
        try:
            data = request.get_json()
            print("📩 Gelen VERİ:", data)

            if data.get("object") == "instagram":
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        print("🔁 Değişiklik:", change)

                        if change.get("field") == "messages":
                            sender_id = change.get("value", {}).get("sender", {}).get("id")
                            user_message = change.get("value", {}).get("message", {}).get("text")

                            if sender_id and user_message:
                                print("📨 Kullanıcı mesajı:", user_message)
                                reply = get_gpt_response(user_message)
                                send_message(sender_id, reply)
                            else:
                                print("⚠️ Gerekli veri eksik, mesaj işlenmedi.")
            return "ok", 200

        except Exception as e:
            print("❌ JSON HATASI:", e)
            return "bad request", 400


# GPT yanıtı üret (sadece reklam konularına odaklı asistan)
def get_gpt_response(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen Nasıfoğulları Reklam Ajansı'nın dijital müşteri asistanısın. "
                        "Sadece şu konularda bilgi ver:\n"
                        "- Sosyal medya etkileşimi\n"
                        "- Düşük satışlar\n"
                        "- Takipçi ilgisizliği\n"
                        "- Instagram/Facebook reklam performansı\n"
                        "- 15.000 TL'lik reklam setimizin satışı\n\n"
                        "Konu dışında bir şey sorulursa şöyle yanıt ver:\n"
                        '“Bu hesap yalnızca dijital reklam çözümleri için hizmet vermektedir.”\n\n'
                        "Satış odaklı konuş. Fiyat sorulursa 15.000 TL olduğunu belirt. "
                        "Etkileşim azlığı, boşa giden içerikler gibi acı noktalara değin. "
                        "Her mesaj bir satış fırsatıdır. Asla boş konuşma. Kısa, net, ikna edici ol."
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )
        result = response['choices'][0]['message']['content']
        result = result[:1900]
        print("✅ GPT CEVABI:", result)
        return result
    except Exception as e:
        print("❌ GPT HATASI:", e)
        return "Şu anda teknik bir problem yaşıyoruz, lütfen daha sonra tekrar dene."


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
        if response.status_code != 200:
            print(f"❌ Instagram mesaj hatası: {response.status_code} - {response.text}")
        else:
            print("📤 Mesaj başarıyla gönderildi:", response.json())
    except Exception as e:
        print("❌ MESAJ GÖNDERME HATASI:", e)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
