from azpython.perp import Perp

az = Perp(host="https://f-api.azverse.xyz", access_key='', secret_key='')
print(az.get_k_line(symbol='btc_usdt', interval="1m"))
