

import requests
import time
import json
from datetime import datetime

BOT_TOKEN = "8824713902:AAHUlzA4RqtTAHkEbKbxS1r87cd2l6ZfdLE"
CHAT_ID = "8699689811"


FILE_NAME = "sent_matches.json"

# 📩 Send Telegram Message
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)
    print("Sent:", text)

# ⚽ Get matches
def get_matches():
    url = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d=2026-06-24&s=Soccer"
    response = requests.get(url)
    data = response.json()
    return data.get("events", [])

# 🤖 Prediction logic
def predict_match(team1, team2):
    return f"🔥 Prediction 🔥\n{team1} 2 - 1 {team2}"

# 📂 Load sent matches
def load_sent():
    try:
        with open(FILE_NAME, "r") as f:
            return set(json.load(f))
    except:
        return set()

# 💾 Save instantly (IMPORTANT)
def save_sent(sent):
    with open(FILE_NAME, "w") as f:
        json.dump(list(sent), f)

print("Bot started...")

while True:
    try:
        sent_matches = load_sent()   # 🔴 RELOAD EVERY LOOP (KEY FIX)

        matches = get_matches()

        for match in matches:
            match_id = match.get("idEvent")

            # extra safety (sometimes API sends duplicates)
            unique_key = f"{match_id}"

            if unique_key in sent_matches:
                continue

            home = match.get("strHomeTeam")
            away = match.get("strAwayTeam")

            if not home or not away:
                continue

            msg = predict_match(home, away)

            send_message(msg)

            # ✅ SAVE IMMEDIATELY AFTER SEND
            sent_matches.add(unique_key)
            save_sent(sent_matches)

            time.sleep(2)  # avoid fast duplicate trigger

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
