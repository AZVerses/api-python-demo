# -*- coding:utf-8 -*-
# 700 market-center rebuild: there is no separate agg_ticker channel any more.
# The ticker channel has absorbed the best bid/ask (bp/bq/ap/aq), so subscribe to
# `ticker@{symbol}` instead.
import time
import threading
from azpython.websocket.perp import PerpWebsocketStreamClient

if __name__ == '__main__':
    symbol = "btc_usdt"


    def message_handler(_, message):
        print(message)


    my_client = PerpWebsocketStreamClient(on_message=message_handler)

    # Subscribe to a single symbol stream (best bid/ask now included in ticker)
    my_client.ticker(symbol=symbol, action=PerpWebsocketStreamClient.ACTION_SUBSCRIBE)
    # keep heartbeat
    threading.Thread(target=my_client.heartbeat, daemon=False).start()
    time.sleep(5)
    # # Unsubscribe
    my_client.ticker(symbol=symbol, action=PerpWebsocketStreamClient.ACTION_UNSUBSCRIBE)
    time.sleep(5)
    print("closing ws connection")
    my_client.stop()
