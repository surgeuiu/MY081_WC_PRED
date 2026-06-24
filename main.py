import requests
import time
from datetime import datetime, timedelta

BOT_TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
        requests.post(url, data=data)
        print("Message sent:", text)
    except Exception as e:
        print("Send error:", e)

def predict_match(team1, team2):
    return f"Prediction:\n{team1} 2 - 1 {team2}"

def check_matches():
    print("Checking matches...")

    # TEST MODE (always sends message)
    prediction = predict_match("Argentina", "Austria")
    send_message(prediction)

# 🔁 KEEP BOT ALIVE
print("Bot started...")

while True:
    try:
        check_matches()
        time.sleep(60)  # every 1 min
    except Exception as e:
        print("Error:", e)
        time.sleep(10)
