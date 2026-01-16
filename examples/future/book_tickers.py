from azpython.perp import Perp

az = Perp(host="https://f-api.myaztests.com", access_key='', secret_key='')
print(az.get_book_ticker(symbol='btc_usdt'))
