import asyncio #using asyncio instead of threading bc asyncio is more efficient for I/O tasks (which listening to websockets are)
import datetime
import json
import websockets #pip install websockets
from kafka import KafkaProducer #pip install kafka-python-ng

#set up kafka: https://kafka.apache.org/quickstart (download, then run JVM docker image)
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda m: json.dumps(m).encode(),
)

async def coinbase_ws():
    url = "wss://ws-feed.exchange.coinbase.com"
    async with websockets.connect(url) as ws:
        subscribe_message = {
            'type': 'subscribe',
            'channels': [
                {
                    'name': 'ticker',
                    'product_ids': ['BTC-USD']
                }
            ]
        }
        await ws.send(json.dumps(subscribe_message)) #when websocket opened, subscribe to ticker for bitcoin

        while True: #run infinitely
            try:
                #once you receive message from websocket, print filtered data
                message = await ws.recv()
                data = json.loads(message)

                # data example (dictionary):
                # {'type': 'ticker', 'sequence': 113118509526, 'product_id': 'BTC-USD', 'price': '117368.86', 'open_24h': '120715.1',
                #  'volume_24h': '9000.72909775', 'low_24h': '117324.72', 'high_24h': '122600', 'volume_30d': '180772.60924498',
                #  'best_bid': '117368.85', 'best_bid_size': '0.05017849', 'best_ask': '117369.32', 'best_ask_size': '0.03786184',
                #  'side': 'buy', 'time': '2025-10-10T18:48:28.055251Z', 'trade_id': 883994653, 'last_size': '0.03381592'}

                if data.get('type') == 'ticker':
                    filtered_data = {
                        'exchange': 'coinbase',
                        'symbol': data.get('product_id'), #BTC-USD
                        'price': data.get('price'),  # current market price
                        'bid': data.get('bid'),  # highest price someone willing to pay
                        'ask': data.get('ask'),  # lowest price someone willing to sell
                        'timestamp': datetime.datetime.now(datetime.UTC).isoformat()
                    }
                    print(filtered_data)

                    producer.send('coinbase-btc-usd', filtered_data)

            except Exception as e:
                print(e)

async def kraken_ws():
    url = "wss://ws.kraken.com/v2"
    async with websockets.connect(url) as ws:
        subscribe_message = {
            'method': 'subscribe',
            'params': {
                'channel': 'ticker',
                'symbol': [
                    'BTC/USD'
                ],
            }
        }
        await ws.send(json.dumps(subscribe_message)) #when websocket opened, subscribe to ticker for bitcoin

        while True: #run infinitely
            try:
                # once you receive message from websocket, print data
                message = await ws.recv()
                data = json.loads(message)

                # data example (dictionary):
                # {
                #     "channel": "ticker",
                #     "type": "snapshot",
                #     "data": [
                #         {
                #             "symbol": "ALGO/USD",
                #             "bid": 0.10025,
                #             "bid_qty": 740.0,
                #             "ask": 0.10036,
                #             "ask_qty": 1361.44813783,
                #             "last": 0.10035,
                #             "volume": 997038.98383185,
                #             "vwap": 0.10148,
                #             "low": 0.09979,
                #             "high": 0.10285,
                #             "change": -0.00017,
                #             "change_pct": -0.17
                #         }
                #     ]
                # }

                if data.get('channel') == 'ticker':
                    data = data.get('data')[0]
                    filtered_data = {
                        'exchange': 'kraken',
                        'symbol': data.get('symbol'),
                        'price': data.get('last'),
                        'bid': data.get('bid'),
                        'ask': data.get('ask'),
                        'timestamp': datetime.datetime.now(datetime.UTC).isoformat()
                    }
                    print(filtered_data)

                    producer.send('kraken-btc-usd', filtered_data)

            except Exception as e:
                print(e)

async def main():
    await asyncio.gather(
        coinbase_ws(),
        kraken_ws()
    )

if __name__ == '__main__':
    asyncio.run(main())