
import requests
import time
import json
from datetime import datetime

BOT_TOKEN = "8824713902:AAHUlzA4RqtTAHkEbKbxS1r87cd2l6ZfdLE"
CHAT_ID = "8699689811"

# 📩 Send Telegram Message
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)
    print("Sent:", text)

# ⚽ Get matches from API
def get_matches():
    url = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d=2026-06-24&s=Soccer"
    response = requests.get(url)
    data = response.json()
    return data.get("events", [])

# 🤖 Prediction logic
def predict_match(team1, team2):
    return f"🔥 Prediction 🔥\n{team1} 2 - 1 {team2}"

# 🧠 LOAD SENT MATCHES (permanent storage)
try:
    with open("sent_matches.json", "r") as f:
        sent_matches = set(json.load(f))
except:
    sent_matches = set()

print("Bot started with API...")

# 🔁 Main Loop
while True:
    try:
        matches = get_matches()

        for match in matches:
            match_id = match["idEvent"]

            # 🚫 Skip if already sent
            if match_id in sent_matches:
                continue

            home = match["strHomeTeam"]
            away = match["strAwayTeam"]

            message = predict_match(home, away)

            send_message(message)

            # ✅ Mark as sent
            sent_matches.add(match_id)

            # 💾 Save permanently
            with open("sent_matches.json", "w") as f:
                json.dump(list(sent_matches), f)

        time.sleep(60)  # run every 1 minute

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
