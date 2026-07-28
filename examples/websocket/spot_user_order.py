# -*- coding:utf-8 -*-
import time
import threading
from azpython.websocket.spot import SpotWebsocketStreamClient

if __name__ == '__main__':
    # 700 accounts-push rebuild: the private account WS carries the login token on the
    # handshake (no more listenKey / LOGIN). For spot fetch it via POST /az/spot/ws-token
    # (azpython.spot.Spot.listen_key -> result.accessToken) and pass it below.
    token = ""


    def message_handler(_, message):
        print(message)


    my_client = SpotWebsocketStreamClient(on_message=message_handler,
                                          is_auth=True, token=token)

    # Subscribe to a single symbol stream
    my_client.user_order(action=SpotWebsocketStreamClient.ACTION_SUBSCRIBE)
    # keep heartbeat
    threading.Thread(target=my_client.heartbeat, daemon=False).start()
    time.sleep(5)
    # # Unsubscribe
    my_client.user_order(action=SpotWebsocketStreamClient.ACTION_UNSUBSCRIBE)
    time.sleep(5)
    print("closing ws connection")
    my_client.stop()
