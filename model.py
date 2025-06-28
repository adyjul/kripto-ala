import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.volatility import AverageTrueRange

THRESHOLD = 0.5  # Turunkan threshold agar lebih agresif

def load_model(path='/root/kripto-ala/model_scalping_15m.pkl'):
    return joblib.load(path)

def calculate_indicators(df):
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
    df['ema_fast'] = EMAIndicator(close=df['close'], window=12).ema_indicator()
    df['ema_slow'] = EMAIndicator(close=df['close'], window=26).ema_indicator()
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()
    df['adx'] = ADXIndicator(high=df['high'], low=df['low'], close=df['close']).adx()
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close']).average_true_range()
    return df.dropna()

def predict_live(df, model, threshold=THRESHOLD):
    df = calculate_indicators(df)
    latest = df.iloc[-1:]
    fitur = ['rsi', 'macd', 'macd_signal', 'macd_hist',
             'ema_fast', 'ema_slow', 'adx', 'atr',
             'open', 'high', 'low', 'close', 'volume']

    X = latest[fitur]
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0][pred]
    signal = 'LONG' if pred == 1 else 'SHORT'

    if prob < threshold:
        signal = 'HOLD'

    close_price = float(latest['close'].values[0])
    atr_value = float(latest['atr'].values[0])

    # Gunakan ATR sebagai dasar prediksi harga target
    predicted_entry_price = close_price

    return {
        'signal': signal,
        'probability': float(prob),
        'current_price': close_price,
        'predicted_entry_price': predicted_entry_price,
        'atr': atr_value,
        'high': float(latest['high'].values[0]),
        'low': float(latest['low'].values[0]),
        'indicators': latest[fitur].to_dict(orient='records')[0],
        'timestamp': latest.index[-1].strftime('%Y-%m-%d %H:%M:%S') if latest.index.name == 'timestamp' else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
