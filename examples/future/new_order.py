from azpython.perp import Perp

az = Perp(host="https://f-api.myaztests.com", access_key='', secret_key='')
res = az.send_order(symbol='btc_usdt', price=10000, amount=1, order_side='BUY', order_type='LIMIT', position_side='LONG')
print(res)
