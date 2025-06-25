# main.py
from decision import prediction, signal, probability
from excecute_trade import execute_order
from utils.config import load_config

cfg = load_config()
symbol = cfg['symbol']
threshold = cfg['threshold']

if probability > threshold:
    execute_order(symbol, signal)
else:
    print(f"Probabilitas terlalu rendah: {probability:.2%}, tidak entry")