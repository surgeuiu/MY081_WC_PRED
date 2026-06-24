import requests
import time

BOT_TOKEN = "8824713902:AAHUlzA4RqtTAHkEbKbxS1r87cd2l6ZfdLE"
CHAT_ID = "8699689811"

def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
        requests.post(url, data=data)
        print("Message sent")
    except Exception as e:
        print("Error:", e)

print("Bot started...")

while True:
    try:
        send_message("Bot running ✅")
        time.sleep(180)
    except Exception as e:
        print("Loop error:", e)
        time.sleep(10)
