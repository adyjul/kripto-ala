import time
import pandas as pd
from datetime import datetime
from model import predict_live
from data import fetch_data

FILENAME = 'validasi_scalping_15m.xlsx'

TP_PCT = 0.002   # Target Profit: 0.2%
SL_PCT = 0.0015  # Stop Loss: 0.15%

def init_excel():
    try:
        df = pd.read_excel(FILENAME)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            'timestamp', 'signal', 'probability',
            'entry_price', 'tp_price', 'sl_price',
            'status'
        ])
        df.to_excel(FILENAME, index=False)
    return df

def append_signal(signal, prob, entry_price):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if signal == 'LONG':
        tp = entry_price * (1 + TP_PCT)
        sl = entry_price * (1 - SL_PCT)
    else:  # SHORT
        tp = entry_price * (1 - TP_PCT)
        sl = entry_price * (1 + SL_PCT)

    new_row = {
        'timestamp': timestamp,
        'signal': signal,
        'probability': prob,
        'entry_price': entry_price,
        'tp_price': tp,
        'sl_price': sl,
        'status': 'HOLD'
    }

    df = pd.read_excel(FILENAME)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(FILENAME, index=False)

def run():
    print("🔁 Validasi sinyal LONG/SHORT berjalan terus...")
    init_excel()
    while True:
        try:
            # Ambil sinyal
            pred, prob = predict_live()
            signal = 'LONG' if pred == 1 else 'SHORT'

            # Ambil harga terkini dari candle terakhir
            df_candle = fetch_data(limit=2)
            entry_price = df_candle['close'].iloc[-1]

            # Simpan hasil
            append_signal(signal, prob, entry_price)

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sinyal: {signal} | Prob: {prob:.2f} | Entry: {entry_price:.2f}")

        except Exception as e:
            print(f"❌ Error: {e}")

        # Tunggu 15 menit (900 detik)
        time.sleep(900)

if __name__ == "__main__":
    run()
