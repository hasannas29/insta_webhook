from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "nasifogullari_token"

@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge, 200
    return "Doğrulama hatası", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("GELEN VERİ:", data)
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
