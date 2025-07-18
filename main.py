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
            print("⚙️ GELEN RAW DATA:", request.data)
            print("⚙️ PARSED JSON:", data)

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
