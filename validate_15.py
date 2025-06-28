# validate_status.py

import pandas as pd
from datetime import datetime
from data_loader import fetch_data

FILENAME = 'validasi_scalping_15m.xlsx'

def validate_signals():
    try:
        df = pd.read_excel(FILENAME)
    except FileNotFoundError:
        print("❌ File tidak ditemukan.")
        return

    if df.empty:
        print("📭 Tidak ada data untuk divalidasi.")
        return

    # Ambil harga candle terbaru
    candles = fetch_data(limit=2)
    if candles.empty or len(candles) < 2:
        print("❌ Gagal ambil data candle.")
        return

    latest_candle = candles.iloc[-1]
    high = latest_candle['high']
    low = latest_candle['low']

    updated = 0
    for idx, row in df.iterrows():
        if row['status'] != 'HOLD':
            continue  # skip yang sudah terisi

        if row['signal'] == 'LONG':
            if high >= row['tp_price']:
                df.at[idx, 'status'] = 'TP'
            elif low <= row['sl_price']:
                df.at[idx, 'status'] = 'SL'
            else:
                df.at[idx, 'status'] = 'NO-HIT'

        elif row['signal'] == 'SHORT':
            if low <= row['tp_price']:
                df.at[idx, 'status'] = 'TP'
            elif high >= row['sl_price']:
                df.at[idx, 'status'] = 'SL'
            else:
                df.at[idx, 'status'] = 'NO-HIT'

        updated += 1

    df.to_excel(FILENAME, index=False)
    print(f"✅ Validasi selesai. {updated} sinyal diperbarui.")

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚦 Memulai validasi status sinyal...")
    validate_signals()
