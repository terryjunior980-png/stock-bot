import yfinance as yf
import pandas as pd
from config import WATCHLIST, MARKET_INDEX, RSI_PERIOD, RSI_OVERSOLD, EMA_FAST, EMA_MARKET

def get_data(symbol):
    df = yf.download(symbol, period="60d", interval="1d", progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

def calculate_rsi(series, period=14):
    delta    = series.diff()
    gain     = delta.where(delta > 0, 0.0)
    loss     = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs       = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def market_is_healthy():
    try:
        df = yf.download(MARKET_INDEX, period="300d", interval="1d", progress=False, auto_adjust=True)
        df.dropna(inplace=True)
        close         = df['Close'].squeeze()
        ema200        = calculate_ema(close, EMA_MARKET)
        current_price = float(close.iloc[-1])
        current_ema   = float(ema200.iloc[-1])
        healthy       = current_price > current_ema
        print(f"📊 SPY: {current_price:.2f} | 200 EMA: {current_ema:.2f} | Healthy: {healthy}")
        return healthy
    except Exception as e:
        print(f"❌ Market health check failed: {e}")
        return False

def scan_watchlist():
    if not market_is_healthy():
        print("🚫 Market unhealthy. No trades today.")
        return None

    candidates = []

    for symbol in WATCHLIST:
        try:
            df = get_data(symbol)
            if len(df) < 30:
                continue

            close           = df['Close'].squeeze()
            df['RSI']       = calculate_rsi(close, RSI_PERIOD)
            df['EMA_FAST']  = calculate_ema(close, EMA_FAST)

            current_close   = float(close.iloc[-1])
            current_rsi     = float(df['RSI'].iloc[-1])
            current_ema     = float(df['EMA_FAST'].iloc[-1])
            recent_rsi      = df['RSI'].iloc[-5:]
            rsi_was_low     = (recent_rsi < RSI_OVERSOLD).any()
            price_above_ema = current_close > current_ema

            if rsi_was_low and price_above_ema:
                target    = round(current_close * 1.04, 2)
                stop_loss = round(current_close * 0.98, 2)
                candidates.append({
                    'symbol':    symbol,
                    'price':     round(current_close, 2),
                    'rsi':       round(current_rsi, 2),
                    'ema':       round(current_ema, 2),
                    'target':    target,
                    'stop_loss': stop_loss
                })
                print(f"✅ Signal: {symbol} | Price: {current_close:.2f} | RSI: {current_rsi:.2f}")
            else:
                print(f"⏭️  No signal: {symbol} | RSI: {current_rsi:.2f}")

        except Exception as e:
            print(f"❌ Error scanning {symbol}: {e}")

    if not candidates:
        return None

    best = min(candidates, key=lambda x: x['rsi'])
    print(f"\n🎯 Best signal: {best['symbol']} | RSI: {best['rsi']}")
    return best
