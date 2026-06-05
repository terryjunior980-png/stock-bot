from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from bot import run_bot
import pytz

# Timezone
WAT = pytz.timezone("Africa/Lagos")

def job():
    print(f"\n⏰ Scheduled job triggered at {datetime.now(WAT).strftime('%Y-%m-%d %H:%M')} WAT")
    run_bot()

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone=WAT)

    # Run every weekday at 3:45 PM WAT
    scheduler.add_job(
        job,
        trigger='cron',
        day_of_week='mon-fri',
        hour=15,
        minute=45,
        timezone=WAT
    )

    print("🤖 Stock Signal Bot Started")
    print("⏰ Scheduled to run Monday-Friday at 3:45 PM WAT")
    print("📱 Signals will be sent to your Telegram")
    print("="*50)

    # Run once immediately on startup to test
    print("\n🔄 Running initial test scan now...")
    run_bot()

    scheduler.start()
