
import requests
import time
import json

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

# 🤖 Prediction
def predict_match(team1, team2):
    return f"🔥 Prediction 🔥\n{team1} 2 - 1 {team2}"

# 📂 Load file
def load_sent():
    try:
        with open(FILE_NAME, "r") as f:
            return set(json.load(f))
    except:
        return set()

# 💾 Save file
def save_sent(data):
    with open(FILE_NAME, "w") as f:
        json.dump(list(data), f)

print("Bot started...")

while True:
    try:
        sent_matches = load_sent()

        matches = get_matches()

        seen_in_this_loop = set()   # 🔥 NEW (fix same-loop duplicate)

        for match in matches:
            match_id = match.get("idEvent")
            home = match.get("strHomeTeam")
            away = match.get("strAwayTeam")

            if not match_id or not home or not away:
                continue

            # 🔥 STRONG UNIQUE KEY
            unique_key = f"{match_id}_{home}_{away}"

            # 🚫 Skip if duplicate in same loop
            if unique_key in seen_in_this_loop:
                continue

            # 🚫 Skip if already sent before
            if unique_key in sent_matches:
                continue

            seen_in_this_loop.add(unique_key)

            msg = predict_match(home, away)
            send_message(msg)

            # ✅ Save immediately
            sent_matches.add(unique_key)
            save_sent(sent_matches)

            time.sleep(3)  # small delay

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)

