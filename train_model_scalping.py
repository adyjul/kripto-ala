# train_model_scalping.py

import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import pandas as pd
import tensorflow as tf
import random
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

from data_loader import get_historical_klines
from utils.config import load_config

# Reproducibility
seed = 42
os.environ['PYTHONHASHSEED'] = str(seed)
tf.random.set_seed(seed)
np.random.seed(seed)
random.seed(seed)

# Load config
cfg = load_config()
symbol = cfg['symbol']
interval = cfg.get('interval', '5m')  # default scalping interval
window_size = cfg['window_size']

# Load raw data
df = get_historical_klines(symbol=symbol, interval=interval, lookback=str(window_size + 100))

if df.empty or len(df) < window_size + 20:
    raise ValueError("❌ Data tidak cukup atau kosong untuk training.")

# ==== Technical indicators ====
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

# Select features
features = ['close', 'volume', 'rsi', 'ema_7', 'ema_21']
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[features])

# Build dataset
X, y = [], []
for i in range(window_size, len(scaled)):
    X.append(scaled[i - window_size:i])
    y.append(scaled[i][0])  # predict close price

X, y = np.array(X), np.array(y)

# ==== Build Model ====
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
model.add(LSTM(64))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X, y, epochs=20, batch_size=32)

# Save model
os.makedirs("models", exist_ok=True)
model.save("models/scalping_model.h5")
print("✅ Model scalping selesai dilatih dan disimpan ke models/scalping_model.h5")
