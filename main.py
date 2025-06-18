import openai
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle (eğer .env kullanıyorsan)
load_dotenv()

# API key direkt burada da tanımlanabilir
# openai.api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sen bir reklam danışmanısın."},
            {"role": "user", "content": "Reklam hizmeti almak istiyorum"}
        ]
    )

    cevap = response['choices'][0]['message']['content']
    print("✅ GPT CEVABI:\n", cevap)

except Exception as e:
    print("❌ GPT HATASI:", e)
