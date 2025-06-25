from dotenv import load_dotenv
from binance.client import Client
from utils.config import load_config
cfg = load_config()
import os

load_dotenv()

client = Client(api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_SECRET"))

def execute_order(symbol, signal):
    try:
        leverage = cfg['leverage']
        margin_pct = cfg['margin_pct']
        sl_pct = cfg['sl_pct']
        tp_pct = cfg['tp_pct']

        # Set leverage
        client.futures_change_leverage(symbol=symbol, leverage=leverage)

        # Get price & balance
        price = float(client.futures_symbol_ticker(symbol=symbol)['price'])
        balance_info = client.futures_account_balance()
        usdt_balance = float([x for x in balance_info if x['asset'] == 'USDT'][0]['balance'])

        # Hitung margin (contoh: 3% dari balance)
        margin_amount = usdt_balance * margin_pct

        # Hitung quantity (margin * leverage / harga)
        quantity = round((margin_amount * leverage) / price, 3)

        print(f"USDT balance: {usdt_balance:.2f}, margin: {margin_amount:.2f}, qty: {quantity}, price: {price}")

        # Tentukan arah
        if signal == "LONG":
            side = 'BUY'
            opposite_side = 'SELL'
            sl_price = round(price * (1 - sl_pct), 2)
            tp_price = round(price * (1 + tp_pct), 2)
        else:
            side = 'SELL'
            opposite_side = 'BUY'
            sl_price = round(price * (1 + sl_pct), 2)
            tp_price = round(price * (1 - tp_pct), 2)

        # Entry order (market)
        entry = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        print(f"ENTRY: {signal} @ {price}")

        # Stop loss
        client.futures_create_order(
            symbol=symbol,
            side=opposite_side,
            type='STOP_MARKET',
            stopPrice=str(sl_price),
            closePosition=True,
            timeInForce='GTC'
        )
        print(f"SL set at {sl_price}")

        # Take profit
        client.futures_create_order(
            symbol=symbol,
            side=opposite_side,
            type='TAKE_PROFIT_MARKET',
            stopPrice=str(tp_price),
            closePosition=True,
            timeInForce='GTC'
        )
        print(f"TP set at {tp_price}")

        return entry

    except Exception as e:
        print(f"❌ Order failed: {e}")
        return None
