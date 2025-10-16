import requests #pip install requests
import datetime

def fetch_coinbase_data():
    url = f"https://api.exchange.coinbase.com/products/BTC-USD/ticker" #bitcoin, priced in USD

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    #data example:
    # {'ask': '117555.78', 'bid': '117555.77', 'volume': '8984.14083016', 'trade_id': 883993695, 'price': '117555.78',
    #  'size': '0.00826436', 'time': '2025-10-10T18:47:11.507320251Z', 'rfq_volume': '90.091840'}

    return{
        'exchange': 'coinbase',
        'price': data['price'], #current market price
        'bid': data['bid'], #highest price someone willing to pay
        'ask': data['ask'], #lowest price someone willing to sell
        'timestamp': datetime.datetime.now(datetime.UTC).isoformat()
    }

def fetch_kraken_data():
    url=f"https://api.kraken.com/0/public/Ticker?pair=XBTUSD"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    #data example:
    # {'error': [], 'result': {'XXBTZUSD': {'a': ['117550.00000', '10', '10.000'], 'b': ['117549.90000', '1', '1.000'],
    #                                       'c': ['117550.00000', '0.00013880'], 'v': ['2105.83141119', '2296.17688418'],
    #                                       'p': ['119494.96161', '119642.14678'], 't': [45915, 54164],
    #                                       'l': ['117500.00000', '117500.00000'], 'h': ['122498.00000', '122498.00000'],
    #                                       'o': '121699.00000'}}}

    result_key = list(data['result'].keys())[0]
    result = data['result'][result_key] #get the first result

    return {
        'exchange': 'kraken',
        'price': result['c'][0],
        'bid': result['b'][0],
        'ask': result['a'][0],
        'timestamp': datetime.datetime.now(datetime.UTC).isoformat()
    }

if __name__ == "__main__":
    try:
        coinbase_data = fetch_coinbase_data()
        print(coinbase_data)

        kraken_data = fetch_kraken_data()
        print(kraken_data)

    except Exception as e:
        print(e)