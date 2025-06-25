# predict_decision.py

import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from data_loader import get_historical_klines
from utils.config import load_config

# Load config
cfg = load_config()
symbol = cfg['symbol']
interval = cfg['interval']
window_size = cfg['window_size']
threshold = cfg.get('threshold', 0.6)

# Load trained model
model = load_model("models/crypto_model.h5")

# Get fresh data
data = get_historical_klines(symbol=symbol, interval=interval, lookback=str(window_size + 1))
if data.empty or len(data) <= window_size:
    raise ValueError("❌ Data tidak cukup untuk prediksi")

# Prepare data
scaler = MinMaxScaler()
scaled_close = scaler.fit_transform(data['close'].values.reshape(-1, 1))

X_test = np.array([scaled_close[-window_size:].flatten()])
X_test = X_test.reshape((1, window_size, 1))

# Predict
predicted_scaled = model.predict(X_test)[0][0]
predicted_price = scaler.inverse_transform([[predicted_scaled]])[0][0]

last_price = data['close'].iloc[-1]
delta = predicted_price - last_price
percentage_change = delta / last_price

# Decision
if percentage_change > threshold:
    decision = "📈 LONG"
elif percentage_change < -threshold:
    decision = "📉 SHORT"
else:
    decision = "⏸️ HOLD"

# Output
print("======== PREDIKSI PASAR ========")
print(f"Last Price     : {last_price:.2f}")
print(f"Predicted Price: {predicted_price:.2f}")
print(f"Change         : {percentage_change:.4f} ({percentage_change*100:.2f}%)")
print(f"Decision       : {decision}")
print("================================")
