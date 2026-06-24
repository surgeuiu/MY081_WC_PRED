
import requests
import time
import math
import sqlite3
from datetime import datetime, timedelta, timezone

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8824713902:AAHUlzA4RqtTAHkEbKbxS1r87cd2l6ZfdLE"
CHAT_ID = "8699689811"
BD = timezone(timedelta(hours=6))

# =========================
# DATABASE (NO DUPLICATES)
# =========================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS sent (
    match_id TEXT PRIMARY KEY
)
""")

def already_sent(match_id):
    cur.execute("SELECT 1 FROM sent WHERE match_id=?", (match_id,))
    return cur.fetchone() is not None

def mark_sent(match_id):
    cur.execute("INSERT INTO sent VALUES (?)", (match_id,))
    conn.commit()

# =========================
# TELEGRAM SEND
# =========================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    print("✅ Sent:", text)

# =========================
# GET MATCHES (BD DATE)
# =========================
def get_matches():
    today = datetime.now(BD).strftime("%Y-%m-%d")
    url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={today}&s=Soccer"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        return data.get("events", [])
    except:
        return []

# =========================
# TIME FILTER (BD TIME)
# =========================
def is_match_soon(date_str, time_str):
    try:
        match_dt = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M:%S")
        match_dt = match_dt.replace(tzinfo=timezone.utc).astimezone(BD)

        now = datetime.now(BD)
        diff = match_dt - now

        return timedelta(hours=1) <= diff <= timedelta(hours=2)
    except:
        return False

# =========================
# POISSON FUNCTION
# =========================
def poisson(lmbda, k):
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)

# =========================
# ELO (TEAM STRENGTH)
# =========================
def get_team_strength(team):
    base = 1500
    return base + (hash(team) % 100)

# =========================
# EXPECTED GOALS (AI CORE)
# =========================
def expected_goals(team1, team2):
    elo1 = get_team_strength(team1)
    elo2 = get_team_strength(team2)

    diff = elo1 - elo2

    exp1 = 1.4 + (diff / 400)
    exp2 = 1.2 - (diff / 400)

    return max(0.5, exp1), max(0.5, exp2)

# =========================
# PREDICTION ENGINE
# =========================
def predict_match(team1, team2):
    exp1, exp2 = expected_goals(team1, team2)

    home_win = 0
    draw = 0
    away_win = 0
    goal_diff_prob = {}

    for i in range(7):
        for j in range(7):
            p = poisson(exp1, i) * poisson(exp2, j)

            diff = abs(i - j)
            goal_diff_prob[diff] = goal_diff_prob.get(diff, 0) + p

            if i > j:
                home_win += p
            elif i < j:
                away_win += p
            else:
                draw += p

    # Winner decision
    if home_win > away_win and home_win > draw:
        winner = team1
        confidence = home_win
    elif away_win > home_win and away_win > draw:
        winner = team2
        confidence = away_win
    else:
        winner = "Draw"
        confidence = draw

    # Goal Difference
    if winner == "Draw":
        best_diff = 0
    else:
        goal_diff_prob.pop(0, None)
        best_diff = max(goal_diff_prob, key=goal_diff_prob.get)

    return winner, best_diff, confidence

# =========================
# FORMAT MESSAGE
# =========================
def format_message(team1, team2, winner, diff, confidence):
    return f"""🔥 AI Prediction 🔥

{team1} vs {team2}

🏆 Winner: {winner}
⚽ Goal Difference: {diff}
📊 Confidence: {round(confidence*100,2)}%
"""

# =========================
# MAIN LOOP
# =========================
print("🚀 Ultimate AI Bot Running (BD Time)...")

while True:
    try:
        matches = get_matches()

        for m in matches:
            event_id = m.get("idEvent")
            team1 = m.get("strHomeTeam")
            team2 = m.get("strAwayTeam")
            date = m.get("dateEvent")
            time_str = m.get("strTime")

            if not all([event_id, team1, team2, date, time_str]):
                continue

            unique_id = f"{event_id}_{date}_{time_str}"

            if already_sent(unique_id):
                continue

            if is_match_soon(date, time_str):
                winner, diff, conf = predict_match(team1, team2)

                msg = format_message(team1, team2, winner, diff, conf)

                send_message(msg)
                mark_sent(unique_id)

        time.sleep(45)

    except Exception as e:
        print("❌ Error:", e)
        time.sleep(30)
