import websocket #pip install websockets
import json
import threading
import time

# ----------------  coinbase -------------------
#what to do to when websocket opened (subscribe to ticker for bitcoin)
def on_coinbase_open(ws):
    subscribe_message = {
        'type': 'subscribe',
        'channels': [
            {
                'name': 'ticker',
                'product_ids': ['BTC-USD']
            }
        ]
    }
    ws.send(json.dumps(subscribe_message))

#what to do when websocket sends message (print data)
def on_coinbase_message(ws, message):
    data = json.loads(message)

    #data example:
    # {'type': 'ticker', 'sequence': 113118509526, 'product_id': 'BTC-USD', 'price': '117368.86', 'open_24h': '120715.1',
    #  'volume_24h': '9000.72909775', 'low_24h': '117324.72', 'high_24h': '122600', 'volume_30d': '180772.60924498',
    #  'best_bid': '117368.85', 'best_bid_size': '0.05017849', 'best_ask': '117369.32', 'best_ask_size': '0.03786184',
    #  'side': 'buy', 'time': '2025-10-10T18:48:28.055251Z', 'trade_id': 883994653, 'last_size': '0.03381592'}

    if data.get('type') == 'ticker':
        print(data)

def run_coinbase_ws():
    url = "wss://ws-feed.exchange.coinbase.com"
    ws = websocket.WebSocketApp(url, on_open=on_coinbase_open, on_message=on_coinbase_message)
    ws.run_forever()


# ----------------  kraken -------------------
def on_kraken_open(ws):
    subscribe_message = {
        'event': 'subscribe',
        'pair': ['XBT/USD'],
        'subscription': {
            'name': 'ticker'
        }
    }
    ws.send(json.dumps(subscribe_message))

def on_kraken_message(ws, message):
    data = json.loads(message)

    #data example:
    # [119930888, {'a': ['117420.10000', 9, '9.64329237'], 'b': ['117420.00000', 0, '0.00017522'],
    #              'c': ['117420.10000', '0.00016781'], 'v': ['0.00000000', '2305.27847295'],
    #              'p': ['0.00000', '119631.00330'], 't': [0, 54546], 'l': ['0.00000', '117361.40000'],
    #              'h': ['0.00000', '122498.00000'], 'o': ['0.00000', '120693.60000']}, 'ticker', 'XBT/USD']

    if isinstance(data, list) and data[-2] == 'ticker':
        ticker_data = data[1]
        print(ticker_data)

def run_kraken_ws():
    url = "wss://ws.kraken.com"
    ws = websocket.WebSocketApp(url, on_open=on_kraken_open, on_message=on_kraken_message)
    ws.run_forever()



if __name__ == '__main__':
    threading.Thread(target=run_coinbase_ws).start()
    threading.Thread(target=run_kraken_ws).start()

