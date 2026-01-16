from azpython.spot import Spot

az = Spot(host="https://s-api.azverse.xyz", access_key='', secret_key='')
res = az.order(symbol='btc_usdt', price=10000, quantity=0.001, side='BUY', type='LIMIT')
print(res)
