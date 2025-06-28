# runner.py
import time
import pandas as pd
from datetime import datetime
from model import load_model, predict_live
from data_loader import fetch_data

FILENAME = 'validasi_scalping_15m.xlsx'
TP_PCT = 0.002   # Target Profit: 0.2%
SL_PCT = 0.0015  # Stop Loss: 0.15%
THRESHOLD = 0.55

model = load_model()

def init_excel():
    try:
        pd.read_excel(FILENAME)
    except FileNotFoundError:
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
        tp = sl = current

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

def run():
    print("🚀 Scalping bot 15M aktif... validasi sinyal setiap 15 menit.")
    init_excel()
    while True:
        try:
            df = fetch_data(limit=100)
            prediction = predict_live(df, model, threshold=THRESHOLD)
            append_signal(prediction)
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(900)  # 15 menit

if __name__ == '__main__':
    run()
