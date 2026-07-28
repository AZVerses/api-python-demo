# -*- coding:utf-8 -*-
import time
import threading
from azpython.websocket.perp import PerpWebsocketStreamClient

if __name__ == '__main__':
    # 700 accounts-push rebuild: the private account WS carries the login token on the
    # handshake (no more listenKey / LOGIN). Fetch a valid login token and pass it below.
    token = ""


    def message_handler(_, message):
        print(message)


    my_client = PerpWebsocketStreamClient(on_message=message_handler,
                                          is_auth=True, token=token)

    # Subscribe to a single symbol stream
    my_client.user_balance(action=PerpWebsocketStreamClient.ACTION_SUBSCRIBE)
    # keep heartbeat
    threading.Thread(target=my_client.heartbeat, daemon=False).start()
    time.sleep(5)
    # # Unsubscribe
    my_client.user_balance(action=PerpWebsocketStreamClient.ACTION_UNSUBSCRIBE)
    time.sleep(5)
    print("closing ws connection")
    my_client.stop()
