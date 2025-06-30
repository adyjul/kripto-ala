import pandas as pd
from datetime import datetime
from data_loader import fetch_data
import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv

# Load .env
load_dotenv()

FILENAME = '/root/kripto-ala/validasi_scalping_15m.xlsx'

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

    candles = fetch_data(limit=5)  # Ambil 5 candle terbaru
    if candles.empty or len(candles) < 4:
        print("❌ Gagal ambil data candle.")
        return

    result_messages = []
    updated = 0

    # Ambil 3 candle setelah sinyal
    for idx, row in df.iterrows():
        if row['status'] != 'HOLD':
            continue

        entry_time = pd.to_datetime(row['timestamp'])
        valid_candles = candles[candles['timestamp'] > entry_time].head(3)

        for _, candle in valid_candles.iterrows():
            high = candle['high']
            low = candle['low']
            status = None

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

            if status:
                df.at[idx, 'status'] = status
                updated += 1
                result_messages.append(
                    f"📈 Sinyal ({row['signal']})\n"
                    f"🕒 Waktu: {row['timestamp']}\n"
                    f"💰 Entry: {row['current_price']:.2f}\n"
                    f"🎯 TP: {row['tp_price']:.2f}\n"
                    f"🛡️ SL: {row['sl_price']:.2f}\n"
                    f"📌 Status: {status}"
                )
                break
        else:
            # Jika tidak TP atau SL setelah 3 candle
            df.at[idx, 'status'] = 'NO-HIT'
            updated += 1
            result_messages.append(
                f"📈 Sinyal ({row['signal']})\n"
                f"🕒 Waktu: {row['timestamp']}\n"
                f"💰 Entry: {row['current_price']:.2f}\n"
                f"🎯 TP: {row['tp_price']:.2f}\n"
                f"🛡️ SL: {row['sl_price']:.2f}\n"
                f"📌 Status: NO-HIT"
            )

    df.to_excel(FILENAME, index=False)
    print(f"✅ Validasi selesai. {updated} sinyal diperbarui.")

    for msg in result_messages:
        asyncio.run(kirim_pesan(msg))


if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚦 Memulai validasi status sinyal...")
    validate_signals()
