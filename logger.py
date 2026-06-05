import csv
import os
from datetime import datetime

LOG_FILE = "trade_log.csv"

def init_log():
    """Create the CSV file with headers if it doesn't exist"""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Date",
                "Symbol",
                "Entry Price",
                "Exit Price",
                "Target",
                "Stop Loss",
                "Result",
                "Profit/Loss %",
                "Outcome"
            ])
        print(f"📋 Trade log created")

def log_trade(symbol, entry, exit_price, target, stop_loss, outcome):
    """Write a completed trade to the CSV log"""
    init_log()
    pnl = round(((exit_price - entry) / entry) * 100, 2)
    result = f"+{pnl}%" if pnl > 0 else f"{pnl}%"

    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            symbol,
            entry,
            exit_price,
            target,
            stop_loss,
            result,
            pnl,
            outcome
        ])
    print(f"📋 Trade logged: {symbol} | {outcome} | {result}")

def log_signal(symbol, price, rsi, target, stop_loss):
    """Write a buy signal to the CSV log"""
    init_log()
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            symbol,
            price,
            "-",
            target,
            stop_loss,
            "-",
            "-",
            "SIGNAL SENT"
        ])
    print(f"📋 Signal logged: {symbol} | RSI: {rsi}")
