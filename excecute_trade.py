from binance.client import Client
import os

client = Client(api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_SECRET"))

def execute_order(symbol, signal, quantity=0.001):
    try:
        if signal == "LONG":
            order = client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity
            )
        else:
            order = client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity
            )
        print(f"Order executed: {signal}")
        return order
    except Exception as e:
        print(f"Order failed: {e}")
        return None