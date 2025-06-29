# runner_tp_sl_dinamis.py

import pandas as pd
from datetime import datetime
from model import predict_live, calculate_features
from data_loader import fetch_data
import joblib
import numpy as np

FILENAME = '/root/kripto-ala/validasi_scalping_15m_dinamis.xlsx'
MODEL_PATH = '/root/kripto-ala/models/model_scalping_15m.pkl'

ATR_FACTOR_TP = 1.5
ATR_FACTOR_SL = 1.0
THRESHOLD = 0.55

model = joblib.load(MODEL_PATH)

def init_excel():
    if not pd.io.common.file_exists(FILENAME):
        df = pd.DataFrame(columns=[
            'timestamp', 'signal', 'probability',
            'current_price', 'predicted_entry_price',
            'tp_price', 'sl_price', 'status', 'atr', 'volatility_ratio'
        ])
        df.to_excel(FILENAME, index=False)

def append_signal(prediction, atr, vr):
    signal = prediction['signal']
    prob = prediction['probability']
    current = prediction['current_price']
    predicted_entry = prediction['predicted_entry_price']
    timestamp = prediction['timestamp']

    if signal == 'LONG':
        tp = current + (atr * ATR_FACTOR_TP)
        sl = current - (atr * ATR_FACTOR_SL)
    elif signal == 'SHORT':
        tp = current - (atr * ATR_FACTOR_TP)
        sl = current + (atr * ATR_FACTOR_SL)
    else:
        tp = sl = current

    new_row = {
        'timestamp': timestamp,
        'signal': signal,
        'probability': prob,
        'current_price': current,
        'predicted_entry_price': predicted_entry,
        'tp_price': tp,
        'sl_price': sl,
        'status': 'HOLD',
        'atr': atr,
        'volatility_ratio': vr
    }

    df = pd.read_excel(FILENAME)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(FILENAME, index=False)

    print(f"[{timestamp}] ✅ Sinyal: {signal} | Prob: {prob:.2f} | Harga: {current:.2f} | ATR: {atr:.4f}")

def run_once():
    print("\n🚀 Scalping bot 15M dengan TP/SL dinamis berjalan...")
    init_excel()
    try:
        df = fetch_data(limit=100)
        df = calculate_features(df)
        latest = df.iloc[-1]
        prediction = predict_live(df, model, threshold=THRESHOLD)

        append_signal(
            prediction,
            atr=latest['atr'],
            vr=latest['volatility_ratio']
        )

    except Exception as e:
        print(f"❌ Gagal prediksi: {e}")

if __name__ == '__main__':
    run_once()
