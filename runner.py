# runner.py (versi untuk cronjob + model terbaru)

import pandas as pd
from datetime import datetime
from model import load_data, predict_live
from data_loader import fetch_data
import joblib

FILENAME = '/root/kripto-ala/validasi_scalping_15m.xlsx'
MODEL_PATH = '/root/kripto-ala/models/model_scalping_15m.pkl'

TP_PCT = 0.002   # Target Profit: 0.2%
SL_PCT = 0.0015  # Stop Loss: 0.15%
THRESHOLD = 0.55  # Ambang probabilitas minimal agar tidak HOLD

def load_model(path):
    return joblib.load(path)

model = load_model(MODEL_PATH)

def init_excel():
    if not pd.io.common.file_exists(FILENAME):
        df = pd.DataFrame(columns=[
            'timestamp', 'signal', 'probability',
            'current_price', 'predicted_entry_price',
            'tp_price', 'sl_price', 'status'
        ])
        df.to_excel(FILENAME, index=False)

def append_signal(prediction):
    signal = prediction['signal']
    prob = prediction['probability']
    current = prediction['current_price']
    predicted_entry = prediction['predicted_entry_price']
    timestamp = prediction['timestamp']

    if signal == 'LONG':
        tp = current * (1 + TP_PCT)
        sl = current * (1 - SL_PCT)
    elif signal == 'SHORT':
        tp = current * (1 - TP_PCT)
        sl = current * (1 + SL_PCT)
    else:
        tp = sl = current  # Untuk HOLD, TP dan SL sama

    new_row = {
        'timestamp': timestamp,
        'signal': signal,
        'probability': prob,
        'current_price': current,
        'predicted_entry_price': predicted_entry,
        'tp_price': tp,
        'sl_price': sl,
        'status': 'HOLD'
    }

    df = pd.read_excel(FILENAME)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(FILENAME, index=False)

    print(f"[{timestamp}] ✅ Sinyal: {signal} | Prob: {prob:.2f} | Harga: {current:.2f}")

def run_once():
    print("🚀 Scalping bot 15M (versi terbaru) berjalan...")
    init_excel()

    try:
        df = fetch_data(limit=100)
        df['body'] = abs(df['close'] - df['open'])
        df['range'] = df['high'] - df['low']
        df['volatility_ratio'] = df['range'] / df['close']
        
        prediction = predict_live(df, model, threshold=THRESHOLD)
        append_signal(prediction)
    except Exception as e:
        print(f"❌ Gagal prediksi: {e}")

if __name__ == '__main__':
    run_once()
