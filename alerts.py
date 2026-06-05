import requests
import json
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BASE_URL  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
last_update_id = None

def send_message(text, chat_id=TELEGRAM_CHAT_ID):
    try:
        url  = f"{BASE_URL}/sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
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

def get_updates(offset=None):
    try:
        url    = f"{BASE_URL}/getUpdates"
        params = {"timeout": 10, "offset": offset}
        r      = requests.get(url, params=params)
        return r.json().get("result", [])
    except:
        return []

def handle_commands(trade_file="active_trade.json", log_file="trade_log.csv"):
    global last_update_id

    updates = get_updates(offset=last_update_id)

    for update in updates:
        try:
            update_id       = update["update_id"]
            last_update_id  = update_id + 1

            message = update.get("message", {})
            text    = message.get("text", "").strip()
            chat_id = message.get("chat", {}).get("id")

            if not text or not chat_id:
                continue

            print(f"📩 Command received: {text}")

            if text == "/status":
                try:
                    with open(trade_file, 'r') as f:
                        trade = json.load(f)
                    if trade.get("in_trade"):
                        import yfinance as yf
                        symbol  = trade['symbol']
                        entry   = trade['entry_price']
                        target  = trade['target']
                        sl      = trade['stop_loss']
                        df      = yf.download(symbol, period="2d", interval="1d", progress=False)
                        current = float(df['Close'].squeeze().iloc[-1])
                        pnl     = round(((current - entry) / entry) * 100, 2)
                        msg = f"""
📊 <b>OPEN TRADE</b>

Stock: <b>{symbol}</b>
Entry: <b>${entry}</b>
Current: <b>${current}</b>
Target: <b>${target}</b>
Stop Loss: <b>${sl}</b>
Profit so far: <b>{pnl}%</b>
                        """
                    else:
                        msg = "😴 <b>No open trade right now.</b>\nBot will scan again at 3:45 PM WAT."
                except:
                    msg = "😴 <b>No open trade right now.</b>"
                send_message(msg, chat_id)

            elif text == "/scan":
                send_message("🔍 <b>Manual scan triggered...</b>", chat_id)
                from bot import run_bot
                run_bot()

            elif text == "/trade":
                try:
                    with open(trade_file, 'r') as f:
                        trade = json.load(f)
                    if trade.get("in_trade"):
                        msg = f"""
📋 <b>TRADE DETAILS</b>

Stock: <b>{trade['symbol']}</b>
Entry Price: <b>${trade['entry_price']}</b>
Target: <b>${trade['target']}</b>
Stop Loss: <b>${trade['stop_loss']}</b>
Entry Date: <b>{trade['entry_date']}</b>
                        """
                    else:
                        msg = "😴 <b>No active trade.</b>"
                except:
                    msg = "😴 <b>No active trade.</b>"
                send_message(msg, chat_id)

            elif text == "/log":
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                    if len(lines) <= 1:
                        msg = "📋 <b>No trades logged yet.</b>"
                    else:
                        last5 = lines[-5:]
                        msg   = "📋 <b>LAST 5 TRADES</b>\n\n"
                        for line in last5:
                            parts = line.strip().split(",")
                            if len(parts) >= 9:
                                msg += f"📅 {parts[0]} | {parts[1]} | {parts[8]}\n"
                except:
                    msg = "📋 <b>No trades logged yet.</b>"
                send_message(msg, chat_id)

            elif text == "/help":
                msg = """
🤖 <b>STOCK BOT COMMANDS</b>

/status — Check open trade + live P&L
/scan   — Trigger manual market scan
/trade  — View current trade details
/log    — View last 5 completed trades
/help   — Show this menu
                """
                send_message(msg, chat_id)

        except Exception as e:
            print(f"❌ Command error: {e}")
