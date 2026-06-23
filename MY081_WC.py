import requests
import time
from datetime import datetime, timedelta

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "8699689811"   # your chat id

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

def predict_match(team1, team2):
    # Simple logic (you can upgrade later)
    return f"Prediction:\n{team1} 2 - 1 {team2}"

def check_matches():
    # Example match (you will later connect API)
    match_time = datetime.now() + timedelta(hours=2)

    if datetime.now() >= match_time - timedelta(hours=1.5):
        prediction = predict_match("Argentina", "Austria")
        send_message(prediction)

while True:
    check_matches()
    time.sleep(300)  # check every 5 minutes
