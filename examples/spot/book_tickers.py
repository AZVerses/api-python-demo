from azpython.spot import Spot

az = Spot(host="https://s-api.myaztests.com", access_key='', secret_key='')
print(az.get_tickers_book(symbol='btc_usdt'))
print(az.get_tickers_book(symbols=['btc_usdt', 'eth_usdt']))
