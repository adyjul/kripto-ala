import os
import pandas as pd
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()  # Baca API_KEY dan SECRET dari .env

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
client = Client(api_key=API_KEY, api_secret=API_SECRET)

SYMBOL = 'BTCUSDT'
INTERVAL = Client.KLINE_INTERVAL_15MINUTE
LIMIT = 1000  # Max 1500 tergantung akun kamu
OUTPUT_FILE = 'data/scalping_15m.xlsx'

def fetch_and_save_data(symbol=SYMBOL, interval=INTERVAL, limit=1000):
    try:
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'qav', 'trades', 'taker_base', 'taker_quote', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        os.makedirs("data", exist_ok=True)
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"✅ Data disimpan ke: {OUTPUT_FILE} (Total: {len(df)} bar)")
    except Exception as e:
        print(f"❌ Gagal mengambil data: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
