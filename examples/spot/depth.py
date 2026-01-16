from azpython.spot import Spot

az = Spot(host="https://s-api.myaztests.com", access_key='', secret_key='')
print(az.get_depth(symbol='btc_usdt'))
print(az.get_depth(symbol='btc_usdt', limit=10))
