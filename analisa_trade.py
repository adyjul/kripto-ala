import pandas as pd
from data_loader import fetch_data
from datetime import datetime

FILENAME = 'validasi_scalping_15m.xlsx'
LOOKAHEAD = 3  # Cek max 3 candle (15 menit x 3 = 45 menit)

def check_hits():
    df_signals = pd.read_excel(FILENAME)

    # Ambil candle terbaru
    df_candle = fetch_data(limit=LOOKAHEAD + 1)  # +1 karena candle saat ini
    highs = df_candle['high'].iloc[-LOOKAHEAD:]
    lows = df_candle['low'].iloc[-LOOKAHEAD:]

    updated = False

    for i in range(len(df_signals)):
        row = df_signals.loc[i]
        if row['status'] != 'HOLD':
            continue  # skip yg sudah TP/SL

        tp, sl = row['tp_price'], row['sl_price']
        signal = row['signal']

        hit_tp = False
        hit_sl = False

        # Cek kondisi
        for h, l in zip(highs, lows):
            if signal == 'LONG':
                if h >= tp:
                    hit_tp = True
                    break
                elif l <= sl:
                    hit_sl = True
                    break
            elif signal == 'SHORT':
                if l <= tp:
                    hit_tp = True
                    break
                elif h >= sl:
                    hit_sl = True
                    break

        if hit_tp:
            df_signals.at[i, 'status'] = 'TP'
            updated = True
        elif hit_sl:
            df_signals.at[i, 'status'] = 'SL'
            updated = True
        else:
            df_signals.at[i, 'status'] = 'NO-HIT'
            updated = True

    if updated:
        df_signals.to_excel(FILENAME, index=False)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Status updated.")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ No updates.")

if __name__ == "__main__":
    check_hits()
