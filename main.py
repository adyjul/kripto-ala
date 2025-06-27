import time
from datetime import datetime
import pandas as pd
from model import predict_live
from data_loader import fetch_data
from analisa_trade import check_hits

FILENAME = 'validasi_scalping_15m.xlsx'

TP_PCT = 0.002   # 0.2% TP
SL_PCT = 0.0015  # 0.15% SL

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

    try:
        df = pd.read_excel(FILENAME)
        df = df.dropna(how='all')  # 🛠 Fix: drop empty rows
    except FileNotFoundError:
        df = pd.DataFrame(columns=new_row.keys())

    # 🛠 Fix: Avoid concat warning
    new_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_df], ignore_index=True)

    df.to_excel(FILENAME, index=False)

def main_loop():
    print("🚀 Bot scalping 15M running...")

    while True:
        try:
            # ✅ Step 1: Prediksi sinyal
            pred, prob = predict_live()
            signal = 'LONG' if pred == 1 else 'SHORT'

            # ✅ Step 2: Ambil harga entry dari candle terbaru
            df_candle = fetch_data(limit=2)
            entry_price = df_candle['close'].iloc[-1]

            # ✅ Step 3: Simpan ke file validasi
            append_signal(signal, prob, entry_price)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Signal: {signal} | Prob: {prob:.2f} | Entry: {entry_price:.2f}")

            # ✅ Step 4: Evaluasi sinyal sebelumnya
            check_hits()

        except Exception as e:
            print(f"❌ Error in main loop: {e}")

        # ⏳ Tunggu 15 menit sebelum iterasi berikutnya
        time.sleep(900)

if __name__ == "__main__":
    main_loop()
