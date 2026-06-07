from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from bot import run_bot
from alerts import handle_commands
import pytz
import threading
from flask import Flask

app = Flask(__name__)
WAT = pytz.timezone("Africa/Lagos")

@app.route('/')
def home():
    return "Stock Bot Running ✅"

def job():
    print(f"\n⏰ Scheduled job triggered at {datetime.now(WAT).strftime('%Y-%m-%d %H:%M')} WAT")
    run_bot()

def command_listener():
    handle_commands()

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=WAT)

    scheduler.add_job(
        job,
        trigger='cron',
        day_of_week='mon-fri',
        hour=15,
        minute=45,
        timezone=WAT
    )

    scheduler.add_job(
        command_listener,
        trigger='interval',
        seconds=30,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()
    print("🤖 Stock Signal Bot Started")
    print("⏰ Scheduled Monday-Friday at 3:45 PM WAT")
    print("📱 Signals sent to Telegram")
    print("👂 Listening for commands every 30 seconds")
    print("="*50)
    run_bot()

if __name__ == "__main__":
    t = threading.Thread(target=start_scheduler)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=10000)
