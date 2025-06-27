from data_loader import fetch_data
from features import generate_features
from utils import load_model

def predict_live():
    df = fetch_data()
    df = generate_features(df)
    model = load_model()
    X = df[['rsi', 'ema_fast', 'ema_slow', 'macd', 'macd_signal', 'atr', 'bb_b']]
    X_latest = X.iloc[-1:]
    pred = model.predict(X_latest)[0]
    prob = model.predict_proba(X_latest)[0][1]
    return pred, prob
