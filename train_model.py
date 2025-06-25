# train_model.py
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from data_loader import get_historical_klines

df = get_historical_klines()
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[['close']])

X, y = [], []
window_size = 60

for i in range(window_size, len(scaled) - 1):
    X.append(scaled[i-window_size:i])
    y.append(1 if scaled[i+1][0] > scaled[i][0] else 0)  # 1 = Long, 0 = Short

X, y = np.array(X), np.array(y)

model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)))
model.add(LSTM(64))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(X, y, epochs=5, batch_size=32)

model.save('crypto_model.h5')