# train_model.py (versi revisi untuk meningkatkan akurasi scalping 15M)

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import AverageTrueRange
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib

FILENAME = '/root/kripto-ala/data/scalping_15m.xlsx'
MODEL_FILE = '/root/kripto-ala/models/model_scalping_15m.pkl'


def load_data():
    df = pd.read_excel(FILENAME)
    df = df.sort_values('timestamp')

    # Tambah indikator teknikal
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()
    df['ema_fast'] = EMAIndicator(close=df['close'], window=12).ema_indicator()
    df['ema_slow'] = EMAIndicator(close=df['close'], window=26).ema_indicator()
    df['adx'] = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14).adx()
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()

    # Tambahan fitur scalping
    df['body'] = abs(df['close'] - df['open'])
    df['range'] = df['high'] - df['low']
    df['volatility_ratio'] = df['range'] / df['close']

    # Target: 1 jika harga naik candle berikutnya, 0 jika turun
    df['target'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)
    df.dropna(inplace=True)
    return df

def calculate_indicators(df):
    df = df.copy()
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
    
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()
    
    df['ema_fast'] = EMAIndicator(close=df['close'], window=12).ema_indicator()
    df['ema_slow'] = EMAIndicator(close=df['close'], window=26).ema_indicator()
    
    df['adx'] = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14).adx()
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
    
    df.dropna(inplace=True)
    return df


def predict_live(df, model, threshold=0.55):
    df = calculate_indicators(df)
    latest = df.iloc[-1:]

    fitur = ['rsi', 'macd', 'macd_signal', 'macd_hist',
             'ema_fast', 'ema_slow', 'adx', 'atr',
             'open', 'high', 'low', 'close', 'volume']

    X = latest[fitur]
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0][pred]
    signal = 'LONG' if pred == 1 else 'SHORT'

    if prob < threshold:
        signal = 'HOLD'

    close_price = float(latest['close'].values[0])
    return {
        'signal': signal,
        'probability': float(prob),
        'current_price': close_price,
        'predicted_entry_price': close_price,  # default
        'timestamp': latest.index[-1].strftime('%Y-%m-%d %H:%M:%S') if latest.index.name == 'timestamp' else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def train_model(df):
    fitur = ['rsi', 'macd', 'macd_signal', 'macd_hist',
             'ema_fast', 'ema_slow', 'adx', 'atr',
             'open', 'high', 'low', 'close', 'volume',
             'body', 'range', 'volatility_ratio']

    X = df[fitur]
    y = df['target']

    model = RandomForestClassifier(n_estimators=300, max_depth=6, random_state=42)

    tscv = TimeSeriesSplit(n_splits=5)
    scores = cross_val_score(model, X, y, cv=tscv, scoring='accuracy')
    print(f"📊 Cross-validation Accuracy: {scores.mean():.4f} ± {scores.std():.4f}")

    # Fit final model
    model.fit(X, y)
    joblib.dump(model, MODEL_FILE)
    print(f"✅ Model disimpan ke: {MODEL_FILE}")


if __name__ == "__main__":
    df = load_data()
    train_model(df)
