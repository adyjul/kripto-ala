from data_loader import fetch_data
from features import generate_features
from labeling import generate_labels
from utils import save_model
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = fetch_data()
df = generate_features(df)
df = generate_labels(df)

X = df[['rsi', 'ema_fast', 'ema_slow', 'macd', 'macd_signal', 'atr', 'bb_b']]
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
model = RandomForestClassifier(n_estimators=200)
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test)))
save_model(model)

print("✅ Model selesai dilatih dan disimpan ke models/crypto_model.h5")