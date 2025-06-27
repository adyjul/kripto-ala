def generate_labels(df, tp_pct=0.002, sl_pct=0.0015, window=3):
    labels = []
    for i in range(len(df) - window):
        entry_price = df['close'].iloc[i]
        tp = entry_price * (1 + tp_pct)
        sl = entry_price * (1 - sl_pct)
        high_future = df['high'].iloc[i+1:i+1+window].max()
        low_future = df['low'].iloc[i+1:i+1+window].min()
        if high_future >= tp:
            labels.append(1)
        elif low_future <= sl:
            labels.append(0)
        else:
            labels.append(None)
    df = df.iloc[:len(labels)].copy()
    df['label'] = labels
    return df.dropna()
