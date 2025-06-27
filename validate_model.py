# validate_model_loop.py

import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from data_loader import get_historical_klines
from utils.config import load_config

os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

cfg = load_config()
symbol = cfg['symbol']
interval = cfg.get('interval', '5m')
window_size = cfg['window_size']
tp_pct = cfg.get('tp_pct', 0.004)
sl_pct = cfg.get('sl_pct', 0.0015)
threshold = cfg.get('threshold', 0.0015)

model = load_model("models/scalping_model.h5")

os.makedirs("logs", exist_ok=True)
log_path = os.path.join("logs", "validation_log.csv")
if os.path.exists(log_path):
    log_df = pd.read_csv(log_path)
else:
    log_df = pd.DataFrame(columns=[
        'time', 'current_price', 'predicted_price',
        'actual_price', 'decision', 'result', 'tp_hit', 'sl_hit'
    ])

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

def run_validation():
    df = get_historical_klines(symbol, interval, str(window_size + 50))
    df = calculate_indicators(df)
    if len(df) <= window_size:
        print("❌ Data tidak cukup")
        return

    features = ['close', 'volume', 'rsi', 'ema_7', 'ema_21']
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[features])
    X = np.array([scaled[-window_size:]])
    predicted_scaled = model.predict(X)[0][0]
    predicted_price = scaler.inverse_transform([[predicted_scaled] + [0]*4])[0][0]
    current_price = df['close'].iloc[-1]

    delta = predicted_price - current_price
    pct_change = delta / current_price
    if pct_change > threshold:
        decision = "LONG"
    elif pct_change < -threshold:
        decision = "SHORT"
    else:
        decision = "HOLD"

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Prediksi: {decision}, tunggu validasi 5 menit...")
    time.sleep(300)

    df2 = get_historical_klines(symbol, interval, "2")
    candle = df2.iloc[-1]
    high = candle['high']
    low = candle['low']
    actual_price = candle['close']

    result = "-"
    tp_hit = False
    sl_hit = False
    if decision == "LONG":
        tp = current_price * (1 + tp_pct)
        sl = current_price * (1 - sl_pct)
        if high >= tp:
            result, tp_hit = "TP", True
        elif low <= sl:
            result, sl_hit = "SL", True
        else:
            result = "NO-HIT"
    elif decision == "SHORT":
        tp = current_price * (1 - tp_pct)
        sl = current_price * (1 + sl_pct)
        if low <= tp:
            result, tp_hit = "TP", True
        elif high >= sl:
            result, sl_hit = "SL", True
        else:
            result = "NO-HIT"
    else:
        result = "HOLD"

    log_df.loc[len(log_df)] = {
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'current_price': current_price,
        'predicted_price': predicted_price,
        'actual_price': actual_price,
        'decision': decision,
        'result': result,
        'tp_hit': tp_hit,
        'sl_hit': sl_hit
    }
    log_df.to_csv(log_path, index=False)

    print(f"[VALIDASI] {decision} | Prediksi: {predicted_price:.2f} | Actual: {actual_price:.2f} | Result: {result}")

if __name__ == "__main__":
    try:
        while True:
            run_validation()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n⛔ Dihentikan manual oleh user.")
