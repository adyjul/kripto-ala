import os
# ============== FORCE CPU ONLY ==============
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # suppress TensorFlow warnings

# ============== SET SEED FOR REPRODUCIBILITY ==============
import tensorflow as tf
import numpy as np
import random

SEED = 42
os.environ['PYTHONHASHSEED'] = str(SEED)
tf.random.set_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)

# ============== IMPORT LIBRARIES ==============
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from data_loader import get_historical_klines
from utils.config import load_config
import os

# ============== LOAD CONFIG ==============
cfg = load_config()
symbol = cfg['symbol']
interval = cfg['interval']
window_size = cfg['window_size']


# ============== GET DATA ==============
data = get_historical_klines(symbol=symbol, interval=interval)
print(f"Jumlah data: {len(data)}")
print(f"Contoh isi data[0]: {data[0] if data else 'EMPTY'}")

close_prices = np.array([float(c[4]) for c in data]).reshape(-1, 1)

# ============== PREPROCESS ==============
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(close_prices)

X = []
y = []

for i in range(window_size, len(scaled_data)):
    X.append(scaled_data[i-window_size:i, 0])
    y.append(scaled_data[i, 0])

X, y = np.array(X), np.array(y)
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

# ============== BUILD MODEL ==============
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
model.add(LSTM(units=50))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')

# ============== TRAIN ==============
model.fit(X, y, epochs=10, batch_size=32)

# ============== SAVE MODEL ==============
os.makedirs("models", exist_ok=True)
model.save("models/crypto_model.h5")
print("✅ Model trained and saved to models/crypto_model.h5")
