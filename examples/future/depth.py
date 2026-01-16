from azpython.perp import Perp

az = Perp(host="https://f-api.azverse.xyz", access_key='', secret_key='')
print(az.get_depth(symbol='btc_usdt', depth=10))
