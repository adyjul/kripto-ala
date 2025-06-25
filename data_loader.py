# data_loader.py

from binance.client import Client
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

client = Client(
    api_key=os.getenv("BINANCE_API_KEY"),
    api_secret=os.getenv("BINANCE_SECRET")
)

def get_historical_klines(symbol='BTCUSDT', interval='1h', lookback='1000'):
    try:
        raw = client.futures_klines(symbol=symbol, interval=interval, limit=int(lookback))
        df = pd.DataFrame(raw, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'num_trades',
            'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"❌ Gagal ambil data dari Binance: {e}")
        return pd.DataFrame()
