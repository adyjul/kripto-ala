from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange, BollingerBands

def generate_features(df):
    df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
    df['ema_fast'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
    df['ema_slow'] = EMAIndicator(close=df['close'], window=21).ema_indicator()
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'])
    df['atr'] = atr.average_true_range()
    bb = BollingerBands(close=df['close'])
    df['bb_b'] = bb.bollinger_pband()
    return df.dropna()
