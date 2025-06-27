# predict_scalping.py

import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from data_loader import get_historical_klines
from utils.config import load_config

# Load config
cfg = load_config()
symbol = cfg['symbol']
interval = cfg.get('interval', '5m')
window_size = cfg['window_size']
tp_pct = cfg.get('tp_pct', 0.004)  # 0.4%
sl_pct = cfg.get('sl_pct', 0.0015) # 0.15%
threshold = cfg.get('threshold', 0.0015)

# Load model
model = load_model("models/scalping_model.h5")

# Load data
df = get_historical_klines(symbol=symbol, interval=interval, lookback=str(window_size + 50))

# === Hitung indikator teknikal ===
def calculate_indicators(df):
    df['ema_7'] = df['close'].ewm(span=7, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df['rsi'] = 100 - (100 / (1 + rs))
    return df.dropna()

df = calculate_indicators(df)

# Pastikan data cukup
if df.empty or len(df) <= window_size:
    raise ValueError("❌ Data tidak cukup untuk prediksi")

# Ambil fitur dan skalakan
features = ['close', 'volume', 'rsi', 'ema_7', 'ema_21']
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[features])
X_input = np.array([scaled[-window_size:]])
X_input = X_input.reshape((1, window_size, len(features)))

# Prediksi harga close berikutnya
predicted_scaled = model.predict(X_input)[0][0]
predicted_price = scaler.inverse_transform([[predicted_scaled] + [0]*4])[0][0]

# Harga saat ini (close terakhir)
current_price = df['close'].iloc[-1]
delta = predicted_price - current_price
percent_change = delta / current_price

# Ambil keputusan
if percent_change > threshold:
    decision = "📈 LONG"
elif percent_change < -threshold:
    decision = "📉 SHORT"
else:
    decision = "⏸️ HOLD"

# Simulasi TP dan SL
tp_price = current_price * (1 + tp_pct)
sl_price = current_price * (1 - sl_pct)

# Output
print("\n======== SIMULASI PREDIKSI SCALPING ========")
print(f"Symbol         : {symbol}")
print(f"Interval       : {interval}")
print(f"Harga Sekarang : {current_price:.2f}")
print(f"Harga Prediksi : {predicted_price:.2f}")
print(f"Perubahan      : {percent_change:.4f} ({percent_change*100:.2f}%)")
print(f"Keputusan      : {decision}")
if decision != "⏸️ HOLD":
    print(f"Target Profit  : {tp_price:.2f}")
    print(f"Stop Loss      : {sl_price:.2f}")
print("=============================================\n")
