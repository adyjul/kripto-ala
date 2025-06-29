# validate_status.py (revisi ketat & multiple signals)

import pandas as pd
from datetime import datetime
from data_loader import fetch_data
import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv

# Load env
load_dotenv()

FILENAME = '/root/kripto-ala/validasi_scalping_15m.xlsx'
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TELEGRAM_TOKEN)

# Config
MAX_CANDLE_LOOKBACK = 3  # Validasi maksimal dalam 3 candle terakhir (45 menit)

async def kirim_pesan_bulk(pesan_list):
    try:
        for pesan in pesan_list:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=pesan)
    except Exception as e:
        print(f"❌ Gagal kirim ke Telegram: {e}")

def validate_signals():
    try:
        df = pd.read_excel(FILENAME)
    except FileNotFoundError:
        print("❌ File tidak ditemukan.")
        return

    if df.empty:
        print("📭 Tidak ada data untuk divalidasi.")
        return

    candles = fetch_data(limit=MAX_CANDLE_LOOKBACK + 1)
    if candles.empty or len(candles) <= 1:
        print("❌ Gagal ambil data candle.")
        return

    updated = 0
    pesan_list = []

    for idx, row in df.iterrows():
        if row['status'] != 'HOLD':
            continue

        # Cek sinyal masih valid dalam rentang candle terakhir
        signal_time = pd.to_datetime(row['timestamp'])
        recent_candles = candles[candles['timestamp'] > signal_time]

        if len(recent_candles) == 0 or len(recent_candles) > MAX_CANDLE_LOOKBACK:
            continue  # Skip sinyal lama

        status = 'NO-HIT'
        for _, candle in recent_candles.iterrows():
            high = candle['high']
            low = candle['low']

            if row['signal'] == 'LONG':
                if high >= row['tp_price']:
                    status = 'TP'
                    break
                elif low <= row['sl_price']:
                    status = 'SL'
                    break

            elif row['signal'] == 'SHORT':
                if low <= row['tp_price']:
                    status = 'TP'
                    break
                elif high >= row['sl_price']:
                    status = 'SL'
                    break

        df.at[idx, 'status'] = status
        updated += 1

        if status in ['TP', 'SL']:
            pesan_list.append(
                f"📈 Validasi Sinyal\n"
                f"🕒 Waktu       : {row['timestamp']}\n"
                f"📌 Sinyal      : {row['signal']}\n"
                f"🎯 Entry       : {row['current_price']:.2f}\n"
                f"📈 TP Price    : {row['tp_price']:.2f}\n"
                f"📉 SL Price    : {row['sl_price']:.2f}\n"
                f"✅ Status      : {status}"
            )

    df.to_excel(FILENAME, index=False)
    print(f"✅ Validasi selesai. {updated} sinyal diperbarui.")

    if pesan_list:
        asyncio.run(kirim_pesan_bulk(pesan_list))
    else:
        print("📪 Tidak ada sinyal TP/SL untuk dikirim ke Telegram.")

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚦 Memulai validasi status sinyal...")
    validate_signals()
