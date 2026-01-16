from azpython.spot import Spot

az = Spot(host="https://s-api.myaztests.com", access_key='', secret_key='')
res = az.cancel_order(order_id=12345678)
print(res)
