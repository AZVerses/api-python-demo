from azpython.spot import Spot

az = Spot(host="https://s-api.azverse.xyz", access_key='', secret_key='')
print(az.get_trade_recent(symbol='btc_usdt'))
print(az.get_trade_recent(symbol='btc_usdt', limit=10))
