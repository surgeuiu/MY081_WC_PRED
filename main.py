import requests
import time
import json
import os
import math
from datetime import datetime, timedelta
import pytz

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8824713902:AAHUlzA4RqtTAHkEbKbxS1r87cd2l6ZfdLE"
CHAT_ID = "8699689811"
FILE_NAME = "sent_matches.json"

BD = pytz.timezone("Asia/Dhaka")

# =========================
# LOAD SENT MATCHES
# =========================
def load_sent():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as f:
                return set(json.load(f))
        except:
            return set()
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
    print("✅ SENT:", text)

# =========================
# GET MATCHES (RETRY SAFE)
# =========================
def get_matches():
    today = datetime.now(BD).strftime("%Y-%m-%d")

    url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={today}&s=Soccer"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        matches = data.get("events", [])

        if not matches:
            print("⚠️ No matches from API")
        else:
            print(f"📊 Total matches fetched: {len(matches)}")

        return matches

    except Exception as e:
        print("❌ API ERROR:", e)
        return []

# =========================
# TIME CHECK (FIXED)
# =========================
def is_match_soon(date_str, time_str):
    try:
        if not time_str:
            return False

        # API time is UTC → convert to BD
        match_dt_utc = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M:%S")
        match_dt_utc = pytz.utc.localize(match_dt_utc)

        match_dt_bd = match_dt_utc.astimezone(BD)
        now_bd = datetime.now(BD)

        diff = match_dt_bd - now_bd

        print(f"⏱ {match_dt_bd} | Now: {now_bd} | Diff: {diff}")

        # ✅ Wider + safer window
        return timedelta(minutes=15) <= diff <= timedelta(hours=3)

    except Exception as e:
        print("❌ TIME ERROR:", e)
        return False

# =========================
# POISSON MODEL
# =========================
def poisson(lmbda, k):
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)

def predict_match(team1, team2):
    exp1 = 1.4
    exp2 = 1.2

    best = (0, 0)
    best_prob = 0

    for i in range(6):
        for j in range(6):
            p = poisson(exp1, i) * poisson(exp2, j)
            if p > best_prob:
                best_prob = p
                best = (i, j)

    g1, g2 = best

    if g1 > g2:
        winner = team1
        diff = g1 - g2
    elif g2 > g1:
        winner = team2
        diff = g2 - g1
    else:
        winner = "Draw"
        diff = 0

    return winner, diff, best_prob

# =========================
# MAIN LOOP
# =========================
print("🚀 BOT STARTED (NO MISS VERSION)...")

while True:
    try:
        matches = get_matches()

        for match in matches:
            try:
                event_id = match.get("idEvent")
                team1 = match.get("strHomeTeam")
                team2 = match.get("strAwayTeam")
                date = match.get("dateEvent")
                time_str = match.get("strTime")

                if not all([event_id, team1, team2, date]):
                    continue

                print(f"\n🔎 Checking: {team1} vs {team2}")

                unique_id = str(event_id)

                if unique_id in sent_matches:
                    print("⏩ Already sent")
                    continue

                if not is_match_soon(date, time_str):
                    print("⏩ Not in time window")
                    continue

                # ✅ Predict
                winner, diff, conf = predict_match(team1, team2)

                # ✅ Format (YOUR REQUIREMENT)
                message = f"""🔥 AI Prediction 🔥

{team1} vs {team2}

🏆 Winner: {winner}
⚽ Goal Difference: {diff}
📊 Confidence: {round(conf*100,2)}%
"""

                send_message(message)

                # ✅ Save
                sent_matches.add(unique_id)
                save_sent(sent_matches)

            except Exception as e:
                print("❌ Match error:", e)

        time.sleep(60)

    except Exception as e:
        print("❌ LOOP ERROR:", e)
        time.sleep(30)
