import requests
import pandas as pd
from datetime import datetime
import time

# Konfigurasi
SYMBOL = 'BTCUSDT'
INTERVAL = '15m'
LIMIT = 1000  # Max = 1000
FILENAME = 'data/scalping_15m.xlsx'

def fetch_binance_klines(symbol, interval, limit=1000):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Format hasil
    ohlcv = []
    for d in data:
        ohlcv.append({
            'timestamp': datetime.fromtimestamp(d[0] / 1000),
            'open': float(d[1]),
            'high': float(d[2]),
            'low': float(d[3]),
            'close': float(d[4]),
            'volume': float(d[5])
        })

    return pd.DataFrame(ohlcv)

if __name__ == "__main__":
    print("📥 Mengambil data dari Binance...")
    df = fetch_binance_klines(SYMBOL, INTERVAL, LIMIT)
    
    df.to_excel(FILENAME, index=False)
    print(f"✅ Disimpan ke: {FILENAME}")
    print(df.tail())
