from azpython.spot import Spot

az = Spot(host="https://s-api.azverse.xyz", access_key='', secret_key='')
print(az.get_kline(symbol='btc_usdt', interval="1m"))
print(az.get_kline(symbol='btc_usdt', interval="1h", limit=10))