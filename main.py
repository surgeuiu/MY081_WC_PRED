
import math
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

# ⚽ Get last matches of a team
def get_last_matches(team):
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team}"
    res = requests.get(url).json()

    if not res["teams"]:
        return []

    team_id = res["teams"][0]["idTeam"]

    url2 = f"https://www.thesportsdb.com/api/v1/json/3/eventslast.php?id={team_id}"
    res2 = requests.get(url2).json()

    return res2.get("results", [])[:5]


# 📊 Calculate team stats
def get_team_stats(team):
    matches = get_last_matches(team)

    goals_for = 0
    goals_against = 0
    count = 0

    for m in matches:
        if not m["intHomeScore"] or not m["intAwayScore"]:
            continue

        if m["strHomeTeam"] == team:
            goals_for += int(m["intHomeScore"])
            goals_against += int(m["intAwayScore"])
        else:
            goals_for += int(m["intAwayScore"])
            goals_against += int(m["intHomeScore"])

        count += 1

    if count == 0:
        return 1.2, 1.2  # default

    return goals_for / count, goals_against / count


# 🧠 Poisson probability
def poisson(lmbda, k):
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)


# 🤖 FINAL AI PREDICTION
def predict_match(team1, team2):
    gf1, ga1 = get_team_stats(team1)
    gf2, ga2 = get_team_stats(team2)

    # expected goals
    exp1 = (gf1 + ga2) / 2
    exp2 = (gf2 + ga1) / 2

    max_goals = 5
    best_score = (0, 0)
    best_prob = 0

    # find most probable score
    for i in range(max_goals):
        for j in range(max_goals):
            prob = poisson(exp1, i) * poisson(exp2, j)
            if prob > best_prob:
                best_prob = prob
                best_score = (i, j)

    g1, g2 = best_score

    # winner
    if g1 > g2:
        winner = team1
    elif g2 > g1:
        winner = team2
    else:
        winner = "Draw"

    return f"""🔥 AI Prediction (Poisson Model) 🔥
{team1} {g1} - {g2} {team2}
Winner: {winner}
Confidence: {round(best_prob*100,2)}%
"""
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
