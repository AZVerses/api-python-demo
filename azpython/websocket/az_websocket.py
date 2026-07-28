# -*- coding:utf-8 -*-

import time
import json
import threading

import logging
from typing import Optional
from urllib.parse import urlparse
from websocket import (
    ABNF,
    create_connection,
    WebSocketException,
    WebSocketConnectionClosedException,
    WebSocketTimeoutException,
)

logger = logging.getLogger(__name__)


def get_timestamp():
    return int(time.time() * 1000)


def parse_proxies(proxies: dict):
    """Parse proxy url from dict, only support http and https proxy, not support socks5 proxy"""
    proxy_url = proxies.get("http") or proxies.get("https")
    if not proxy_url:
        return {}

    parsed = urlparse(proxy_url)
    return {
        "http_proxy_host": parsed.hostname,
        "http_proxy_port": parsed.port,
        "http_proxy_auth": (parsed.username, parsed.password)
        if parsed.username and parsed.password
        else None,
    }


class AZSocketManager(threading.Thread):
    def __init__(
            self,
            stream_url,
            on_message=None,
            on_open=None,
            on_close=None,
            on_error=None,
            on_ping=None,
            on_pong=None,
            timeout=None,
            proxies: Optional[dict] = None,
    ):
        threading.Thread.__init__(self)
        self.stream_url = stream_url
        self.on_message = on_message
        self.on_open = on_open
        self.on_close = on_close
        self.on_ping = on_ping
        self.on_pong = on_pong
        self.on_error = on_error
        self.timeout = timeout

        self._proxy_params = parse_proxies(proxies) if proxies else {}

        self.create_ws_connection()

    def create_ws_connection(self):
        logger.debug(
            f"Creating connection with WebSocket Server: {self.stream_url}, proxies: {self._proxy_params}",
        )

        self.ws = create_connection(
            self.stream_url, timeout=self.timeout, **self._proxy_params
        )
        logger.debug(
            f"WebSocket connection has been established: {self.stream_url}, proxies: {self._proxy_params}",
        )
        self._callback(self.on_open)

    def run(self):
        self.read_data()

    def send_message(self, message):
        logger.debug(f"Sending message to AZ WebSocket Server: {message}")
        self.ws.send(message)

    def ping(self):
        self.ws.ping()

    def read_data(self):
        data = ""
        while True:
            try:
                op_code, frame = self.ws.recv_data_frame(True)
            except WebSocketException as e:
                if isinstance(e, WebSocketConnectionClosedException):
                    logger.error("Lost websocket connection")
                elif isinstance(e, WebSocketTimeoutException):
                    logger.error("Websocket connection timeout")
                else:
                    logger.error("Websocket exception: {}".format(e))
                raise e
            except Exception as e:
                logger.error("Exception in read_data: {}".format(e))
                raise e

            self._handle_data(op_code, frame, data)
            self._handle_heartbeat(op_code, frame)

            if op_code == ABNF.OPCODE_CLOSE:
                logger.warn(
                    "CLOSE frame received, closing websocket connection"
                )
                self._callback(self.on_close)
                break

    def _handle_heartbeat(self, op_code, frame):
        if op_code == ABNF.OPCODE_PING:
            self._callback(self.on_ping, frame.data)
            self.ws.pong("")
            logger.debug("Received Ping; PONG frame sent back")
        elif op_code == ABNF.OPCODE_PONG:
            logger.debug("Received PONG frame")
            self._callback(self.on_pong)

    def _handle_data(self, op_code, frame, data):
        # 700 market-center / accounts-push rebuild:
        # Push frames are flat JSON text carrying a ``ch`` field (``<type>@<symbol>``)
        # and short keys, e.g.
        #   ticker : {"ch":"ticker@btc_usdt","s":..,"o":..,"c":..,"v":<qty>,"uv":<quote>,
        #             "r":<change rate>,"bp":..,"bq":..,"ap":..,"aq":..,"ix":..,"mx":..,"ts":..}
        #             (``ix``/``mx`` = index/mark price, futures only)
        #   depth  : {"ch":"depth@btc_usdt","type":"snapshot"|"delta","u":<seq>,"pu":<prev u>,
        #             "b":[[price,qty],..],"a":[[price,qty],..],"ts":..}  (qty=="0" removes level)
        # The subscribe/unsubscribe ack and the heartbeat reply also arrive here as text.
        if op_code == ABNF.OPCODE_TEXT:
            data = frame.data.decode("utf-8")
            # Heartbeat replies: public market WS answers JSON {"pong":<ts>};
            # private account WS answers the plain text "pong".
            if data == "pong":
                self._callback(self.on_pong, None)
                return
            try:
                obj = json.loads(data)
            except (ValueError, TypeError):
                obj = None
            if isinstance(obj, dict) and "pong" in obj:
                self._callback(self.on_pong, obj.get("pong"))
                return
            self._callback(self.on_message, data)

    def close(self):
        if not self.ws.connected:
            logger.warn("Websocket already closed")
        else:
            self.ws.send_close()
        return

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                logger.error("Error from callback {}: {}".format(callback, e))
                if self.on_error:
                    self.on_error(self, e)


class AZWebsocketClient:
    ACTION_SUBSCRIBE = "subscribe"
    ACTION_UNSUBSCRIBE = "unsubscribe"

    def __init__(
            self,
            stream_url,
            on_message=None,
            on_open=None,
            on_close=None,
            on_error=None,
            on_ping=None,
            on_pong=None,
            timeout=None,
            proxies: Optional[dict] = None,
            ping_json=True,
    ):
        # Heartbeat differs by domain (700 rebuild):
        #   public market WS  -> JSON  {"method":"ping"} -> {"pong":<ts>}   (ping_json=True)
        #   private account WS -> text "ping" -> "pong"                     (ping_json=False)
        self._ping_json = ping_json
        self.socket_manager = self._initialize_socket(
            stream_url,
            on_message,
            on_open,
            on_close,
            on_error,
            on_ping,
            on_pong,
            timeout,
            proxies,
        )

        # start the thread
        self.socket_manager.start()
        logger.debug("AZ WebSocket Client started.")

    def _initialize_socket(
            self,
            stream_url,
            on_message,
            on_open,
            on_close,
            on_error,
            on_ping,
            on_pong,
            timeout,
            proxies,
    ):
        return AZSocketManager(
            stream_url,
            on_message=on_message,
            on_open=on_open,
            on_close=on_close,
            on_error=on_error,
            on_ping=on_ping,
            on_pong=on_pong,
            timeout=timeout,
            proxies=proxies,
        )

    def _single_stream(self, stream):
        if isinstance(stream, str):
            return True
        elif isinstance(stream, list):
            return False
        else:
            raise ValueError("Invalid stream name, expect string or array")

    def send(self, message: dict):
        self.socket_manager.send_message(json.dumps(message))

    def send_message_to_server(self, message, action=None, id=None):
        if not id:
            id = get_timestamp()

        if action != self.ACTION_UNSUBSCRIBE:
            return self.subscribe(message, id=id)
        return self.unsubscribe(message, id=id)

    def subscribe(self, stream, id=None):
        # 700 rebuild: params are plain channel names (e.g. "ticker@btc_usdt", or
        # "balance"/"order" for the private account WS). The account is taken from the
        # handshake token, so there is no more @accountId / @listenKey suffix.
        if not id:
            id = get_timestamp()
        if self._single_stream(stream):
            stream = [stream]
        mes = {
            "method": "subscribe",
            "params": stream,
            "id": str(id)
        }
        json_msg = json.dumps(mes)
        self.socket_manager.send_message(json_msg)

    def unsubscribe(self, stream, id=None):
        if not id:
            id = get_timestamp()
        if self._single_stream(stream):
            stream = [stream]

        mes = {
            "method": "unsubscribe",
            "params": stream,
            "id": str(id)
        }
        json_msg = json.dumps(mes)
        self.socket_manager.send_message(json_msg)

    def ping(self):
        logger.debug("Sending ping to AZ WebSocket Server")
        if self._ping_json:
            # public market WS heartbeat
            self.socket_manager.send_message(json.dumps({"method": "ping"}))
        else:
            # private account WS heartbeat
            self.socket_manager.send_message(message="ping")

    def heartbeat(self):
        while True:
            if self.socket_manager.is_alive():
                self.ping()
                time.sleep(15)
            else:
                break

    def stop(self, id=None):
        self.socket_manager.close()
        self.socket_manager.join()
