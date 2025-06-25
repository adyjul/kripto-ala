# main.py
from decision import prediction, signal, probability
from execute_trade import execute_order

symbol = 'BTCUSDT'
if probability > 0.6:  # threshold keyakinan
    execute_order(symbol, signal)
else:
    print(f"Probabilitas terlalu rendah: {probability:.2%}, tidak entry")