import pandas as pd
from binance.client import Client
import os
from utils.config import load_config

cfg = load_config()
interval = cfg['interval']

client = Client(api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_SECRET"))

def get_historical_klines(symbol='BTCUSDT',interval=interval, lookback='1000'):
    klines = client.get_historical_klines(symbol, interval, f"{lookback} hours ago UTC")
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['return'] = df['close'].pct_change()
    df.dropna(inplace=True)
    return df