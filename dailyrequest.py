import requests
import json




def get_point_change(symbol):
    endpoint = r'https://api.tdameritrade.com/v1/marketdata/quotes'
    payload = {
        'apikey': '9QAJTJSAZZIVFTUZYEEX1CRD4ECDM86B', 
        'symbol': symbol,
    }

    response = requests.get(url=endpoint, params=payload, timeout=20).json()
    open_price = response[symbol]['openPrice']
    current = response[symbol]['lastPrice']

    point_change = current-open_price

    return point_change