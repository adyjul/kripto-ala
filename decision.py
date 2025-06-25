# decision.py
import numpy as np
from keras.models import load_model
from data_loader import get_historical_klines
from sklearn.preprocessing import MinMaxScaler

model = load_model('crypto_model.h5')
df = get_historical_klines()
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[['close']])

window_size = 60
last_window = scaled[-window_size:]
X = np.expand_dims(last_window, axis=0)

prediction = model.predict(X)
probability = prediction[0][0]
signal = 'LONG' if probability > 0.5 else 'SHORT'

print(f"Prediction: {signal}, Probability: {probability:.2%}")