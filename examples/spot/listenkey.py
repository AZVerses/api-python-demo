# -*- coding:utf-8 -*-
from azpython.spot import Spot

az = Spot(host="https://s-api.myaztests.com", access_key='', secret_key='')
print(az.listen_key())
