import json
import yfinance as yf
from datetime import datetime
from signals import scan_watchlist, calculate_ema, get_data
from alerts  import send_buy_signal, send_take_profit, send_stop_loss, send_no_signal, send_market_unhealthy
from logger  import log_signal, log_trade

TRADE_FILE = "active_trade.json"

def load_trade():
    """Load active trade from JSON file"""
    try:
        with open(TRADE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_trade(data):
    """Save active trade to JSON file"""
    with open(TRADE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def clear_trade():
    """Clear trade after it closes"""
    save_trade({})

def get_current_price(symbol):
    """Get latest price for a symbol"""
    try:
        df = yf.download(symbol, period="2d", interval="1d", progress=False)
        return float(df['Close'].iloc[-1])
    except:
        return None

def check_open_trade():
    """
    If we have an open trade check if
    target or stop loss has been hit
    """
    trade = load_trade()

    if not trade or not trade.get("in_trade"):
        return False

    symbol      = trade['symbol']
    entry       = trade['entry_price']
    target      = trade['target']
    stop_loss   = trade['stop_loss']
    current     = get_current_price(symbol)

    if not current:
        print(f"❌ Could not get price for {symbol}")
        return True

    print(f"📊 Open trade: {symbol} | Entry: {entry} | Current: {current} | Target: {target} | SL: {stop_loss}")

    if current >= target:
        print(f"💰 Take profit hit for {symbol}")
        send_take_profit(symbol, entry, current)
        log_trade(symbol, entry, current, target, stop_loss, "TAKE PROFIT")
        clear_trade()

    elif current <= stop_loss:
        print(f"🛑 Stop loss hit for {symbol}")
        send_stop_loss(symbol, entry, current)
        log_trade(symbol, entry, current, target, stop_loss, "STOP LOSS")
        clear_trade()

    else:
        print(f"⏳ Trade still open. Waiting for target or stop loss.")

    return True

def run_bot():
    """Main bot function that runs every day at 3:45 PM WAT"""
    print(f"\n{'='*50}")
    print(f"🤖 Bot running at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}\n")

    # Step 1 - Check if we have an open trade first
    trade_open = check_open_trade()
    if trade_open:
        print("📋 Open trade being monitored. Skipping new scan.")
        return

    # Step 2 - Scan for new signal
    print("🔍 Scanning market for signals...")
    signal = scan_watchlist()

    if not signal:
        print("😴 No signal found today.")
        send_no_signal()
        return

    # Step 3 - Save signal as active trade
    trade = {
        "in_trade":    True,
        "symbol":      signal['symbol'],
        "entry_price": signal['price'],
        "target":      signal['target'],
        "stop_loss":   signal['stop_loss'],
        "entry_date":  datetime.now().strftime("%Y-%m-%d")
    }
    save_trade(trade)

    # Step 4 - Send Telegram alert
    send_buy_signal(signal)

    # Step 5 - Log the signal
    log_signal(
        signal['symbol'],
        signal['price'],
        signal['rsi'],
        signal['target'],
        signal['stop_loss']
    )

    print(f"\n✅ Bot cycle complete.")
