# train_model_cpu.py

import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
import numpy as np
import random
import pandas as pd

# Set seed untuk hasil konsisten
seed = 42
os.environ['PYTHONHASHSEED'] = str(seed)
tf.random.set_seed(seed)
np.random.seed(seed)
random.seed(seed)

from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

from data_loader import get_historical_klines
from utils.config import load_config

# Load config
cfg = load_config()
symbol = cfg['symbol']
interval = cfg['interval']
window_size = cfg['window_size']

# Load data
data = get_historical_klines(symbol=symbol, interval=interval)

# Validasi
if data.empty:
    raise ValueError("❌ Data dari Binance kosong. Pastikan API dan koneksi OK.")

# Preprocessing
scaler = MinMaxScaler()
scaled_close = scaler.fit_transform(data['close'].values.reshape(-1, 1))

X, y = [], []

for i in range(window_size, len(scaled_close)):
    X.append(scaled_close[i - window_size:i, 0])
    y.append(scaled_close[i, 0])

X, y = np.array(X), np.array(y)
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

# Build model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)))
model.add(LSTM(50))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X, y, epochs=10, batch_size=32)

# Save model
os.makedirs("models", exist_ok=True)
model.save("models/crypto_model.h5")
print("✅ Model selesai dilatih dan disimpan ke models/crypto_model.h5")
