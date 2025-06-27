from model import predict_live

pred, prob = predict_live()

if pred == 1:
    print(f"📈 BUY signal detected! Prob: {prob:.2f}")
else:
    print(f"📉 SELL signal detected! Prob: {1 - prob:.2f}")
