from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from bot import run_bot
from alerts import handle_commands
import pytz

WAT = pytz.timezone("Africa/Lagos")

def job():
    print(f"\n⏰ Scheduled job triggered at {datetime.now(WAT).strftime('%Y-%m-%d %H:%M')} WAT")
    run_bot()

def command_listener():
    print(f"👂 Checking commands at {datetime.now(WAT).strftime('%H:%M')}")
    handle_commands()

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone=WAT)

    # Run scan every weekday at 3:45 PM WAT
    scheduler.add_job(
        job,
        trigger='cron',
        day_of_week='mon-fri',
        hour=15,
        minute=45,
        timezone=WAT
    )

    # Check for commands every 10 seconds
    scheduler.add_job(
        command_listener,
        trigger='interval',
        seconds=10
    )

    print("🤖 Stock Signal Bot Started")
    print("⏰ Scheduled to run Monday-Friday at 3:45 PM WAT")
    print("📱 Signals will be sent to your Telegram")
    print("👂 Listening for commands every 10 seconds")
    print("="*50)

    print("\n🔄 Running initial test scan now...")
    run_bot()

    scheduler.start()
