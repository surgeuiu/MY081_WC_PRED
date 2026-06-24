
import requests
import time
import json
import os
import math
from datetime import datetime, timedelta

BOT_TOKEN = "8824713902:AAHUlzA4RqtTAHkEbKbxS1r87cd2l6ZfdLE"
CHAT_ID = "8699689811"

FILE_NAME = "sent_matches.json"

# =========================
# LOAD SENT MATCHES
# =========================
def load_sent():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(FILE_NAME, "w") as f:
        json.dump(list(sent), f)

sent_matches = load_sent()

# =========================
# SEND TELEGRAM
# =========================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    print("✅ Sent:", text)

# =========================
# GET MATCHES (TODAY)
# =========================
def get_matches():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={today}&s=Soccer"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        return data.get("events", [])
    except:
        return []

# =========================
# CHECK TIME WINDOW
# =========================
def is_match_soon(date_str, time_str):
    try:
        match_dt = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.utcnow()

        diff = match_dt - now

        return timedelta(hours=1) <= diff <= timedelta(hours=2)
    except:
        return False

# =========================
# AI PREDICTION (POISSON)
# =========================
def poisson(lmbda, k):
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)

def predict_match(team1, team2):
    # simple fallback averages (fast + stable)
    exp1 = 1.4
    exp2 = 1.2

    best = (0, 0)
    best_prob = 0

    for i in range(5):
        for j in range(5):
            p = poisson(exp1, i) * poisson(exp2, j)
            if p > best_prob:
                best_prob = p
                best = (i, j)

    g1, g2 = best

    if g1 > g2:
        winner = team1
    elif g2 > g1:
        winner = team2
    else:
        winner = "Draw"

    return f"""🔥 AI Prediction 🔥
{team1} {g1} - {g2} {team2}
Winner: {winner}
Confidence: {round(best_prob*100,2)}%
"""

# =========================
# MAIN LOOP
# =========================
print("🚀 Bot started (Production Mode)...")

while True:
    try:
        matches = get_matches()

        for match in matches:
            event_id = match.get("idEvent")
            team1 = match.get("strHomeTeam")
            team2 = match.get("strAwayTeam")
            date = match.get("dateEvent")
            time_str = match.get("strTime")

            if not all([event_id, team1, team2, date, time_str]):
                continue

            # UNIQUE KEY (no duplicate forever)
            unique_id = f"{event_id}"

            if unique_id in sent_matches:
                continue

            if is_match_soon(date, time_str):
                prediction = predict_match(team1, team2)

                send_message(prediction)

                sent_matches.add(unique_id)
                save_sent(sent_matches)

        time.sleep(60)

    except Exception as e:
        print("❌ Error:", e)
        time.sleep(30)
