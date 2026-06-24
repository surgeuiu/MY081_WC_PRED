
import requests
import time
from datetime import datetime, timedelta

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

# 🧠 Check if match is upcoming (KEY FIX)
def is_match_upcoming(date_str, time_str):
    try:
        match_time = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.utcnow()

        # send only if match is within next 2 hours
        diff = (match_time - now).total_seconds()
        return 0 <= diff <= 7200
    except:
        return False

print("🚀 Bot started (Railway Safe Mode)...")

while True:
    try:
        matches = get_matches()

        seen_in_this_loop = set()  # prevent same-loop duplicate

        for match in matches:
            home = match.get("strHomeTeam")
            away = match.get("strAwayTeam")
            date = match.get("dateEvent")
            time_str = match.get("strTime")

            if not home or not away or not date or not time_str:
                continue

            # 🔥 FILTER: only upcoming matches
            if not is_match_upcoming(date, time_str):
                continue

            # 🔥 UNIQUE KEY
            unique_key = f"{home}_{away}_{date}_{time_str}"

            if unique_key in seen_in_this_loop:
                continue

            seen_in_this_loop.add(unique_key)

            # 📤 Send prediction
            message = predict_match(home, away)
            send_message(message)

            time.sleep(2)  # prevent rapid duplicate

        time.sleep(60)  # check every 1 min

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
