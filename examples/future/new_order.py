from azpython.perp import Perp

az = Perp(host="https://f-api.azverse.xyz", access_key='', secret_key='')
# amount is the real base-coin quantity (post 去张 / de-contract): 0.01 = 0.01 btc,
# it is the coin amount, NOT a number of contracts (张).
res = az.send_order(symbol='btc_usdt', price=10000, amount=0.01, order_side='BUY', order_type='LIMIT', position_side='LONG')
print(res)
