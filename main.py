

import requests
import time
from datetime import datetime, timedelta

sent_matches = set()
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

# 🧠 Main Loop
sent_matches = set()

print("Bot started with API...")

while True:
    try:
        matches = get_matches()

        for match in matches:
            match_id = match["idEvent"]

# Skip if already sent
if match_id in sent_matches:
    continue
            team1 = match["strHomeTeam"]
            team2 = match["strAwayTeam"]
            match_time_str = match["dateEvent"] + " " + match["strTime"]

            match_time = datetime.strptime(match_time_str, "%Y-%m-%d %H:%M:%S")

            now = datetime.utcnow() + timedelta(hours=6)

            # ⏰ 1.5 hour before match
            if 0 < (match_time - now).total_seconds() <= 21800:

                key = f"{team1}-{team2}-{match_time}"

                if key not in sent_matches:
                    msg = predict_match(team1, team2)
                    send_message(msg)
                    sent_matches.add(key)

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
