import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_message(text):
    """Send a Telegram message to your phone"""
    try:
        url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        r    = requests.post(url, data=data)
        if r.status_code == 200:
            print(f"📱 Telegram sent successfully")
        else:
            print(f"❌ Telegram error: {r.text}")
    except Exception as e:
        print(f"❌ Telegram failed: {e}")

def send_buy_signal(signal):
    msg = f"""
🎯 <b>BUY SIGNAL</b>

📈 Stock: <b>{signal['symbol']}</b>
💵 Price: <b>${signal['price']}</b>
📉 RSI: <b>{signal['rsi']} (Oversold)</b>
🌍 Market: <b>HEALTHY ✅</b>

🎯 Target: <b>${signal['target']} (+4%)</b>
🛑 Stop Loss: <b>${signal['stop_loss']} (-2%)</b>

👉 Open Bamboo and buy now!
    """
    send_message(msg)

def send_take_profit(symbol, entry, current):
    profit_pct = round(((current - entry) / entry) * 100, 2)
    msg = f"""
💰 <b>TAKE PROFIT</b>

📈 Stock: <b>{symbol}</b>
🔵 Entry: <b>${entry}</b>
🟢 Current: <b>${current}</b>
📊 Profit: <b>+{profit_pct}%</b>

👉 Open Bamboo and SELL now!
    """
    send_message(msg)

def send_stop_loss(symbol, entry, current):
    loss_pct = round(((current - entry) / entry) * 100, 2)
    msg = f"""
🛑 <b>STOP LOSS TRIGGERED</b>

📈 Stock: <b>{symbol}</b>
🔵 Entry: <b>${entry}</b>
🔴 Current: <b>${current}</b>
📊 Loss: <b>{loss_pct}%</b>

👉 Open Bamboo and SELL now!
    """
    send_message(msg)

def send_no_signal():
    msg = """
😴 <b>NO SIGNAL TODAY</b>

Bot scanned VOO, MSFT, AAPL.
No qualifying setup found.
Will check again tomorrow at 3:45 PM.
    """
    send_message(msg)

def send_market_unhealthy():
    msg = """
🚫 <b>MARKET FILTER ACTIVE</b>

SPY is below 200 EMA.
Market trend is weak.
Bot is protecting your capital.
No trades today.
    """
    send_message(msg)
