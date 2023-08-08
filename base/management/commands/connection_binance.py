import requests
import time
import hashlib
import hmac
import pprint from pprint 

def get_server_time():
    url = "https://api.binance.com/api/v3/time"
    response = requests.get(url)
    return response.json()['serverTime']

def create_signature(query_string, secret_key):
    return hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def fetch_all_orders(api_key, secret_key, symbol):
    timestamp = get_server_time()
    query_string = 'symbol={}&timestamp={}'.format(symbol, timestamp)
    signature = create_signature(query_string, secret_key)

    headers = {
        'X-MBX-APIKEY': api_key
    }

    url = "https://api.binance.com/api/v3/allOrders?" + query_string + "&signature=" + signature
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return response.content

# Replace with your Binance API key and Secret Key, and the symbol you're interested in
api_key = "gYvkU2nUgrJMyGyAB9qvHeVJwgO63aPwCF7UXueiCmwKvy0TJGKmTGGSDu9ZwttO"
secret_key = "jEfXdcJ6E2lIdhqterlvWZeYsJS03iAXqqMgtygRFZl1uJ8FDDUaUOth5IirpVS2"
symbol = "ETHUSDT"  # Example symbol

pprint(fetch_all_orders(api_key, secret_key, symbol))
