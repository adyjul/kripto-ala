import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import AverageTrueRange
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

FILENAME = 'data/scalping_15m.xlsx'
MODEL_FILE = 'model_scalping_15m.pkl'

def load_data():
    df = pd.read_excel(FILENAME)

    # Urutkan by time
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

    # Target label: 1 = LONG, 0 = SHORT
    df['target'] = np.where(df['close'].shift(-2) > df['close'], 1, 0)

    df.dropna(inplace=True)
    return df

def train_model(df):
    features = ['rsi', 'macd', 'macd_signal', 'macd_hist',
                'ema_fast', 'ema_slow', 'adx', 'atr',
                'open', 'high', 'low', 'close', 'volume']
    
    X = df[features]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # Evaluasi
    y_pred = model.predict(X_test)
    print("📊 Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("\n📈 Classification Report:\n", classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_FILE)
    print(f"✅ Model disimpan ke: {MODEL_FILE}")

if __name__ == "__main__":
    df = load_data()
    train_model(df)
