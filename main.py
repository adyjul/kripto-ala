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

MODEL_PATH = 'model_scalping_15m.pkl'
DATA_FILE = 'data/scalping_15m.xlsx'
OUTPUT_FILE = 'validasi_scalping_15m.xlsx'

model = joblib.load(MODEL_PATH)

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

def predict_signal(df):
    fitur = ['rsi', 'macd', 'macd_signal', 'macd_hist',
             'ema_fast', 'ema_slow', 'adx', 'atr',
             'open', 'high', 'low', 'close', 'volume']
    X = df[fitur]
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0][pred]
    signal = 'LONG' if pred == 1 else 'SHORT'
    return signal, prob, df['close'].values[0]

def simpan_ke_excel(signal, prob, harga):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tp = harga * 1.002
    sl = harga * 0.998
    new_row = {
        'timestamp': now,
        'signal': signal,
        'probability': round(prob, 4),
        'entry_price': harga,
        'tp_price': tp,
        'sl_price': sl,
        'status': 'HOLD'
    }
    try:
        df_old = pd.read_excel(OUTPUT_FILE)
        df_new = pd.concat([df_old, pd.DataFrame([new_row])], ignore_index=True)
    except:
        df_new = pd.DataFrame([new_row])
    df_new.to_excel(OUTPUT_FILE, index=False)
    print(f"[{now}] ✅ Sinyal {signal} (Prob: {prob:.2f}) disimpan.")

def loop_main():
    print("🚀 Scalping bot aktif, prediksi tiap 15 menit...")
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
            print(f"❌ Error in main loop: {e}")
        
        # Tunggu 15 menit
        time.sleep(15 * 60)

if __name__ == "__main__":
    loop_main()
