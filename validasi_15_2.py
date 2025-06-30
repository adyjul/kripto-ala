# validate_status.py (dengan logika dinamis dan konfirmasi indikator tambahan)

import pandas as pd
from datetime import datetime, timedelta
from data_loader import fetch_data
import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import AverageTrueRange

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

def konfirmasi_indikator(df_candle):
    df_candle['rsi'] = RSIIndicator(close=df_candle['close'], window=14).rsi()
    macd = MACD(close=df_candle['close'])
    df_candle['macd_hist'] = macd.macd_diff()
    df_candle.dropna(inplace=True)
    return df_candle

def validate_signals():
    try:
        df = pd.read_excel(FILENAME)
    except FileNotFoundError:
        print("❌ File tidak ditemukan.")
        return

    if df.empty:
        print("📭 Tidak ada data untuk divalidasi.")
        return

    # Ambil 4 candle terakhir (3 validasi + 1 konfirmasi saat ini)
    candles = fetch_data(limit=4)
    if candles.empty or len(candles) < 4:
        print("❌ Gagal ambil data candle.")
        return

    candles = konfirmasi_indikator(candles)
    latest = candles.iloc[-1]
    window = candles.iloc[-4:-1]  # 3 candle validasi TP/SL

    messages = []
    updated = 0
    for idx, row in df.iterrows():
        if row['status'] != 'HOLD':
            continue

        ts = pd.to_datetime(row['timestamp'])
        if datetime.now() - ts > timedelta(minutes=45):
            df.at[idx, 'status'] = 'NO-HIT'
        else:
            # Konfirmasi tambahan: volume spike & indikator
            if latest['volume'] < window['volume'].mean() * 1.5:
                continue  # Tidak validasi jika tidak ada spike

            rsi_valid = 45 < latest['rsi'] < 70 if row['signal'] == 'LONG' else 30 < latest['rsi'] < 55
            macd_valid = latest['macd_hist'] > 0 if row['signal'] == 'LONG' else latest['macd_hist'] < 0

            if not (rsi_valid and macd_valid):
                continue  # Sinyal tidak valid jika tidak dikonfirmasi indikator

            if row['signal'] == 'LONG':
                if window['high'].max() >= row['tp_price']:
                    df.at[idx, 'status'] = 'TP'
                elif window['low'].min() <= row['sl_price']:
                    df.at[idx, 'status'] = 'SL'
            elif row['signal'] == 'SHORT':
                if window['low'].min() <= row['tp_price']:
                    df.at[idx, 'status'] = 'TP'
                elif window['high'].max() >= row['sl_price']:
                    df.at[idx, 'status'] = 'SL'

        if df.at[idx, 'status'] != 'HOLD':
            updated += 1
            pesan = (
                f"📈 Validasi Sinyal"
                f"🕒 Waktu       : {row['timestamp']}"
                f"📌 Sinyal      : {row['signal']}"
                f"🎯 Entry       : {row['current_price']:.2f}"
                f"📈 TP Price    : {row['tp_price']:.2f}"
                f"📉 SL Price    : {row['sl_price']:.2f}"
                f"✅ Status      : {df.at[idx, 'status']}"
            )
            messages.append(pesan)

    df.to_excel(FILENAME, index=False)
    print(f"✅ Validasi selesai. {updated} sinyal diperbarui.")

    for msg in messages:
        asyncio.run(kirim_pesan(msg))

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚦 Memulai validasi status dinamis...")
    validate_signals()
