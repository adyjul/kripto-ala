import pandas as pd
from datetime import datetime
from data_loader import fetch_data
import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv

# Load .env
load_dotenv()

FILENAME = '/root/kripto-ala/validasi_scalping_15m_dinamis.xlsx'

# Telegram Bot setup
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TELEGRAM_TOKEN)

async def kirim_pesan(message):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
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

    candles = fetch_data(limit=3)
    if candles.empty or len(candles) < 3:
        print("❌ Gagal ambil data candle.")
        return

    high = candles['high'].max()
    low = candles['low'].min()

    updated_rows = []
    pesan_list = []

    for idx, row in df.iterrows():
        if row['status'] != 'HOLD':
            continue

        waktu_sinyal = pd.to_datetime(row['timestamp'])
        if (datetime.now() - waktu_sinyal).total_seconds() > 2700:
            continue  # Lewat 45 menit

        status = 'NO-HIT'
        if row['signal'] == 'LONG':
            if high >= row['tp_price']:
                status = 'TP'
            elif low <= row['sl_price']:
                status = 'SL'
        elif row['signal'] == 'SHORT':
            if low <= row['tp_price']:
                status = 'TP'
            elif high >= row['sl_price']:
                status = 'SL'

        df.at[idx, 'status'] = status
        updated_rows.append(idx)

        pesan_list.append(
            f"📈 Sinyal {row['signal']} ({status})\n"
            f"🕒 {row['timestamp']}\n"
            f"🎯 Entry: {row['current_price']:.2f}\n"
            f"🎯 TP: {row['tp_price']:.2f} | SL: {row['sl_price']:.2f}"
        )

    if updated_rows:
        df.to_excel(FILENAME, index=False)
        print(f"✅ Validasi selesai. {len(updated_rows)} sinyal diperbarui.")

    # Kirim semua pesan (maks 10 per batch biar tidak spam telegram)
    for i in range(0, len(pesan_list), 10):
        batch = pesan_list[i:i+10]
        asyncio.run(kirim_pesan("\n\n".join(batch)))

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚦 Memulai validasi status sinyal...")
    validate_signals()
