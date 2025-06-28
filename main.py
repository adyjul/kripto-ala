import pandas as pd
import numpy as np
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import AverageTrueRange
import joblib
import time
import warnings
warnings.filterwarnings('ignore')

# === Konfigurasi ===
MODEL_PATH = 'model_scalping_15m.pkl'
DATA_FILE = 'data/scalping_15m.xlsx'
OUTPUT_FILE = 'validasi_scalping_15m.xlsx'
PROB_THRESHOLD = 0.55       # ✅ Lebih sensitif dari sebelumnya
TP_PCT = 0.002              # 0.2%
SL_PCT = 0.001              # 0.1%
INTERVAL_SECONDS = 15 * 60  # 15 menit

model = joblib.load(MODEL_PATH)

# === Hitung indikator teknikal ===
def hitung_indikator(df):
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()
    df['ema_fast'] = EMAIndicator(close=df['close'], window=12).ema_indicator()
    df['ema_slow'] = EMAIndicator(close=df['close'], window=26).ema_indicator()
    df['adx'] = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14).adx()
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
    return df

# === Prediksi sinyal ===
def predict_signal(df):
    fitur = ['rsi', 'macd', 'macd_signal', 'macd_hist',
             'ema_fast', 'ema_slow', 'adx', 'atr',
             'open', 'high', 'low', 'close', 'volume']
    X = df[fitur]
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0][pred]

    # 💡 Tambahkan threshold agar tidak terlalu ragu
    if prob < PROB_THRESHOLD:
        return 'HOLD', prob, df['close'].values[0]

    signal = 'LONG' if pred == 1 else 'SHORT'
    return signal, prob, df['close'].values[0]

# === Simpan ke Excel ===
def simpan_ke_excel(signal, prob, harga):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    current_price = harga  # kalau kamu mau bedakan bisa ambil dari df['close'].iloc[-1]

    if signal == 'LONG':
        tp = harga * (1 + TP_PCT)
        sl = harga * (1 - SL_PCT)
    elif signal == 'SHORT':
        tp = harga * (1 - TP_PCT)
        sl = harga * (1 + SL_PCT)
    else:
        tp, sl = np.nan, np.nan  # HOLD tidak butuh TP/SL

    new_row = {
        'timestamp': now,
        'signal': signal,
        'probability': round(prob, 4),
        'current_price': round(current_price, 2),
        'entry_price': round(harga, 2),
        'tp_price': round(tp, 2) if not np.isnan(tp) else '',
        'sl_price': round(sl, 2) if not np.isnan(sl) else '',
        'status': 'HOLD' if signal == 'HOLD' else 'OPEN'
    }

    try:
        df_old = pd.read_excel(OUTPUT_FILE)
        df_new = pd.concat([df_old, pd.DataFrame([new_row])], ignore_index=True)
    except:
        df_new = pd.DataFrame([new_row])

    df_new.to_excel(OUTPUT_FILE, index=False)
    print(f"[{now}] ✅ {signal} | Harga: {harga:.2f} | Prob: {prob:.2f} | TP: {tp:.2f if tp else 'N/A'} | SL: {sl:.2f if sl else 'N/A'}")

# === Loop utama ===
def loop_main():
    print("🚀 Scalping bot aktif (15m), threshold prob:", PROB_THRESHOLD)
    while True:
        try:
            df = pd.read_excel(DATA_FILE)
            df = df.sort_values('timestamp')
            df = hitung_indikator(df)
            df.dropna(inplace=True)
            latest = df.iloc[-1:]
            signal, prob, harga = predict_signal(latest)
            simpan_ke_excel(signal, prob, harga)
        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    loop_main()
