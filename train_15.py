import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import AverageTrueRange
import joblib
import warnings

warnings.filterwarnings('ignore')

# Konfigurasi
DATA_FILE = 'data/scalping_15m.xlsx'
MODEL_FILE = 'models/model_scalping_15m.pkl'

def load_and_prepare_data(filepath):
    df = pd.read_excel(filepath)
    df = df.sort_values('timestamp')
    df = df.dropna()

    # Indikator teknikal
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()
    df['ema_fast'] = EMAIndicator(close=df['close'], window=12).ema_indicator()
    df['ema_slow'] = EMAIndicator(close=df['close'], window=26).ema_indicator()
    df['adx'] = ADXIndicator(high=df['high'], low=df['low'], close=df['close']).adx()
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close']).average_true_range()

    df.dropna(inplace=True)

    # Target label: 1 = LONG jika close selanjutnya > sekarang
    df['target'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)

    return df

def train_and_evaluate(df):
    features = [
        'rsi', 'macd', 'macd_signal', 'macd_hist',
        'ema_fast', 'ema_slow', 'adx', 'atr',
        'open', 'high', 'low', 'close', 'volume'
    ]
    X = df[features]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = RandomForestClassifier(n_estimators=300, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n📊 Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("\n📈 Classification Report:\n", classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_FILE)
    print(f"\n✅ Model berhasil disimpan ke: {MODEL_FILE}")

if __name__ == '__main__':
    df = load_and_prepare_data(DATA_FILE)
    train_and_evaluate(df)
