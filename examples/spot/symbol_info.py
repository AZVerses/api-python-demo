from azpython.spot import Spot

az = Spot(host="https://s-api.myaztests.com", access_key='', secret_key='')
print(az.get_symbol_config(symbol='btc_usdt'))
