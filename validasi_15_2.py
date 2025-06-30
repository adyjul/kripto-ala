import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_loader import fetch_data
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv

# === Konfigurasi ===
load_dotenv()
FILENAME = '/root/kripto-ala/validasi_scalping_15m.xlsx'
MAX_LOOKAHEAD = 3  # maksimal 3 candle ke depan (3x15m = 45 menit)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TELEGRAM_TOKEN)


async def kirim_pesan(message):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"❌ Gagal kirim ke Telegram: {e}")


def calculate_indicators(df):
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
    df['ema_fast'] = EMAIndicator(close=df['close'], window=12).ema_indicator()
    df['ema_slow'] = EMAIndicator(close=df['close'], window=26).ema_indicator()
    df['adx'] = ADXIndicator(high=df['high'], low=df['low'], close=df['close']).adx()
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close']).average_true_range()
    df['vol_spike'] = df['volume'] > df['volume'].rolling(window=10).mean() * 1.5
    df.dropna(inplace=True)
    return df


def validate_signals():
    try:
        df_signal = pd.read_excel(FILENAME)
    except FileNotFoundError:
        print("❌ File sinyal tidak ditemukan.")
        return

    if df_signal.empty:
        print("📭 Tidak ada data sinyal.")
        return

    # Ambil candle terakhir (cukup 100 saja)
    df_candles = fetch_data(limit=100)
    df_candles = calculate_indicators(df_candles)

    updated_signals = []

    for idx, row in df_signal.iterrows():
        if row['status'] != 'HOLD':
            continue

        # Cari candle saat sinyal muncul
        ts = pd.to_datetime(row['timestamp'])
        matching_idx = df_candles.index[df_candles['timestamp'] == ts]

        if matching_idx.empty:
            continue  # candle tidak ditemukan

        pos = matching_idx[0]

        # Hanya validasi jika sudah lewat 3 candle
        if pos + MAX_LOOKAHEAD >= len(df_candles):
            continue  # belum cukup waktu

        lookahead = df_candles.iloc[pos+1:pos+1+MAX_LOOKAHEAD]

        hit_tp = False
        hit_sl = False
        konfirmasi = False

        for _, candle in lookahead.iterrows():
            # Konfirmasi indikator
            if row['signal'] == 'LONG':
                if (
                    candle['ema_fast'] > candle['ema_slow']
                    and candle['rsi'] > 50
                    and candle['adx'] > 20
                    and candle['vol_spike']
                ):
                    konfirmasi = True
                    if candle['high'] >= row['tp_price']:
                        hit_tp = True
                        break
                    elif candle['low'] <= row['sl_price']:
                        hit_sl = True
                        break

            elif row['signal'] == 'SHORT':
                if (
                    candle['ema_fast'] < candle['ema_slow']
                    and candle['rsi'] < 50
                    and candle['adx'] > 20
                    and candle['vol_spike']
                ):
                    konfirmasi = True
                    if candle['low'] <= row['tp_price']:
                        hit_tp = True
                        break
                    elif candle['high'] >= row['sl_price']:
                        hit_sl = True
                        break

        # Update status
        if not konfirmasi:
            status = 'NO-CONFIRM'
        elif hit_tp:
            status = 'TP'
        elif hit_sl:
            status = 'SL'
        else:
            status = 'NO-HIT'

        df_signal.at[idx, 'status'] = status
        updated_signals.append({
            'timestamp': row['timestamp'],
            'signal': row['signal'],
            'price': row['current_price'],
            'tp': row['tp_price'],
            'sl': row['sl_price'],
            'status': status
        })

    df_signal.to_excel(FILENAME, index=False)
    print(f"✅ {len(updated_signals)} sinyal berhasil divalidasi.")

    # Kirim semua update via Telegram
    if updated_signals:
        pesan = "📊 *Hasil Validasi Sinyal 15M:*\n"
        for s in updated_signals:
            pesan += (
                f"🕒 {s['timestamp']}\n"
                f"🔹 Sinyal: {s['signal']} | Harga: {s['price']:.2f}\n"
                f"🎯 TP: {s['tp']:.2f} | SL: {s['sl']:.2f}\n"
                f"📌 Status: *{s['status']}*\n\n"
            )
        asyncio.run(kirim_pesan(pesan))


if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚦 Validasi sinyal dinamis mulai...")
    validate_signals()
