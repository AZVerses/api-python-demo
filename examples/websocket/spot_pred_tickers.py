# -*- coding:utf-8 -*-
# Prediction-market batch tickers (spot only). No @symbol suffix; ~3s snapshot.
import time
import threading
from azpython.websocket.spot import SpotWebsocketStreamClient


if __name__ == '__main__':
    def message_handler(_, message):
        print(message)


    my_client = SpotWebsocketStreamClient(on_message=message_handler)

    # Subscribe to the batch stream of all prediction-market symbols
    my_client.all_pred_ticker(action=SpotWebsocketStreamClient.ACTION_SUBSCRIBE)
    # keep heartbeat
    threading.Thread(target=my_client.heartbeat, daemon=False).start()
    time.sleep(5)
    # # Unsubscribe
    my_client.all_pred_ticker(action=SpotWebsocketStreamClient.ACTION_UNSUBSCRIBE)
    time.sleep(5)
    print("closing ws connection")
    my_client.stop()
