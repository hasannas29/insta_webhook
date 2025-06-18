from flask import Flask, request
import openai
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# Anahtarlar
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Flask uygulaması
app = Flask(__name__)

# Basit prompt
def get_prompt():
    return """
    Sen bir reklam danışmanısın. Kullanıcıdan sektörünü öğren, sorunlarını anla ve çözüm öner. 
    Cevabın kısa ve ikna edici olsun.
    """

# GPT çağrısı
def get_gpt_response(user_message):
    try:
        print("GPT INPUT:", user_message)  # test log
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": get_prompt()},
                {"role": "user", "content": user_message}
            ]
        )
        result = response['choices'][0]['message']['content']
        print("GPT CEVABI:", result)
        return result
    except Exception as e:
        print("GPT HATASI:", e)
        return "GPT HATASI OLDU"

# Webhook endpointi
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("GELEN VERİ:", data)

        message = (
            data.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("message", {})
            .get("text")
        )

        if message:
            response = get_gpt_response(message)
            return {"status": "ok", "gpt_response": response}, 200
        else:
            return {"status": "no message found"}, 200
    except Exception as e:
        print("WEBHOOK HATASI:", e)
        return {"status": "error"}, 200

# Sunucu başlat
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
