# data_loader.py

from binance.client import Client
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

# client = Client(
#     api_key=os.getenv("BINANCE_API_KEY"),
#     api_secret=os.getenv("BINANCE_SECRET")
# )

def fetch_data(symbol='BTCUSDT', interval='15m', limit=500):
    client = Client(api_key=os.getenv("API_KEY"), api_secret=os.getenv("API_SECRET"))
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)

    df = pd.DataFrame(klines, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'trades', 'taker_base', 'taker_quote', 'ignore'
    ])

    df['timestamp'] = pd.to_datetime(df['time'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    df = df.sort_values('timestamp').reset_index(drop=True)

    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

# def get_historical_klines(symbol='BTCUSDT', interval='5m', lookback='1000'):
#     try:
#         raw = client.futures_klines(symbol=symbol, interval=interval, limit=int(lookback))
#         df = pd.DataFrame(raw, columns=[
#             'timestamp', 'open', 'high', 'low', 'close', 'volume',
#             'close_time', 'quote_asset_volume', 'num_trades',
#             'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
#         ])
        
#         df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
#         df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

#         return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
#     except Exception as e:
#         print(f"❌ Gagal ambil data Binance: {e}")
#         return pd.DataFrame()
