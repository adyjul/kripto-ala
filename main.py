import time
from datetime import datetime
import pandas as pd
from model import predict_live
from data_loader import fetch_data
from analisa_trade import check_hits

FILENAME = 'validasi_scalping_15m.csv'

TP_PCT = 0.002
SL_PCT = 0.0015

def append_signal(signal, prob, entry_price):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if signal == 'LONG':
        tp = entry_price * (1 + TP_PCT)
        sl = entry_price * (1 - SL_PCT)
    else:
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
        df = pd.read_csv(FILENAME)
        df = df.dropna(how='all')
    except FileNotFoundError:
        df = pd.DataFrame(columns=new_row.keys())

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FILENAME, index=False)

def main_loop():
    print("🚀 Bot scalping 15M running...")

    while True:
        try:
            pred, prob = predict_live()
            signal = 'LONG' if pred == 1 else 'SHORT'

            df_candle = fetch_data(limit=2)
            entry_price = df_candle['close'].iloc[-1]

            append_signal(signal, prob, entry_price)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Signal: {signal} | Prob: {prob:.2f} | Entry: {entry_price:.2f}")

            check_hits()
        except Exception as e:
            print(f"❌ Error in main loop: {e}")

        time.sleep(900)

if __name__ == "__main__":
    main_loop()
