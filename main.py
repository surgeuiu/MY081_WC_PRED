
import requests
import time
from datetime import datetime, timedelta

BOT_TOKEN = "8824713902:AAHUlzA4RqtTAHkEbKbxS1r87cd2l6ZfdLE"
CHAT_ID = "8699689811"


# 📩 Send Telegram Message
def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
        requests.post(url, data=data)
        print("Message sent:", text)
    except Exception as e:
        print("Send error:", e)

# ⚽ Prediction Logic
def predict_match(team1, team2):
    return f"🔥 Prediction 🔥\n{team1} 2 - 1 {team2}"

# 🕒 Set Match Time (TEST: 2 minutes from now)
match_time = datetime.now() + timedelta(minutes=2)

print("Bot started...")

# 🔁 Main Loop (Never stops)
while True:
    try:
        now = datetime.now()
        time_left = (match_time - now).total_seconds()

        print(f"Checking... Time left: {time_left}")

        # ⏰ Trigger before match (within 2 min for test)
        if 0 < time_left <= 120:
            send_message(predict_match("Argentina", "Austria"))
            
            # 🛑 Prevent duplicate sending
            time.sleep(180)

        time.sleep(300)

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
