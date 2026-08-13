# -*- coding:utf-8 -*-
from typing import Optional
from urllib.parse import quote
from azpython.websocket.az_websocket import AZWebsocketClient


class PerpWebsocketStreamClient(AZWebsocketClient):
    """700 market-center / accounts-push rebuild.

    Endpoints (base ``wss://f-ws.azverse.xyz``):
      * public market   -> ``/futures/public``    (JSON ping heartbeat)
      * private account -> ``/ws/account/futures`` (text ping heartbeat)

    The private account WS carries the login token **on the handshake** (there is no
    more ``listenKey``): pass ``token=<token>``. The account is taken from the token,
    so subscription channel names are plain (no ``@listenKey`` suffix): ``order`` /
    ``trade`` / ``balance`` / ``position`` / ``notify`` / ``entrust`` / ``profit`` /
    ``track_entrust`` / ``user_profile`` / ``plan_reverse_entrust``.
    """

    def __init__(
            self,
            stream_url="wss://f-ws.azverse.xyz",
            on_message=None,
            on_open=None,
            on_close=None,
            on_error=None,
            on_ping=None,
            on_pong=None,
            is_auth=False,
            token=None,
            timeout=None,
            proxies: Optional[dict] = None,
    ):
        if not is_auth:
            stream_url = stream_url + "/futures/public"
        else:
            stream_url = stream_url + "/ws/account/futures"
            if token:
                stream_url = stream_url + "?token=" + quote(str(token))
        super().__init__(
            stream_url,
            on_message=on_message,
            on_open=on_open,
            on_close=on_close,
            on_error=on_error,
            on_ping=on_ping,
            on_pong=on_pong,
            timeout=timeout,
            proxies=proxies,
            ping_json=not is_auth,
        )

    # -------------------- public market channels --------------------

    def trade(self, symbol: str, id=None, action=None, **kwargs):
        """
        Trade record (public)
        Stream Name: deal@{symbol}
        Update Speed: Real-time
        """
        stream_name = "deal@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def kline(self, symbol: str, interval: str, id=None, action=None):
        """
        Kline/Candlestick Streams

        Stream Name: kline_{interval}@{symbol}

        interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 2d, 3d, 1w, 1M

        Update Speed: Real-time
        """
        stream_name = "kline_{}@{}".format(interval, symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def depth(self, symbol: str, level=20, id=None, action=None):
        """
        Limited depth (full top-N snapshot, whole-book replace)
        levels: 5, 10, 20, 50, 100
        Stream Names: depth{level}@{symbol}
        Frame: {"ch":"depth","event":"depth{level}@{symbol}",
                "data":{"id":<updateId str>,"s":..,"a":[..],"b":[..],"t":..}}
        Update Speed: Real-time
        """
        stream_name = "depth{}@{}".format(level, symbol.lower())
        self.send_message_to_server(stream_name, id=id, action=action)

    def depth_update(self, symbol: str, id=None, action=None):
        """
        Full depth: subscribe-time snapshot + delta
        Stream Names: depth@{symbol}
        Update Speed: ~100ms
        """
        stream_name = "depth@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, id=id, action=action)

    def ticker(self, symbol=None, id=None, action=None, **kwargs):
        """
        Stream Name: ticker@{symbol}
        (absorbs best bid/ask bp/bq/ap/aq and carries ix/mx index/mark price)
        Update Speed: Real-time
        """
        stream_name = "ticker@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def all_ticker(self, id=None, action=None):
        """
        Stream Name: tickers (full-market snapshot, no @symbol suffix)
        Update Speed: ~3s
        """
        stream_name = "tickers"
        self.send_message_to_server(stream_name, action=action, id=id)

    def ticker_book(self, symbol: str, id=None, action=None):
        """
        Stream Name: tickerbook@{symbol}
        Best bid/ask (top-of-book) changes only
        Update Speed: Real-time
        """
        stream_name = "tickerbook@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def index_price(self, symbol, id=None, action=None):
        """
        Stream Name: index_price@{symbol}
        Frame: {"ch":"index_price","event":"index_price@{symbol}","data":{"s":..,"p":<price>,"t":..}}
               (unified {ch,event,data} envelope, same as every other channel)
        Update Speed: 1000ms
        """
        stream_name = "index_price@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def mark_price(self, symbol, id=None, action=None):
        """
        Stream Name: mark_price@{symbol}
        Frame: {"ch":"mark_price","event":"mark_price@{symbol}","data":{"s":..,"p":<price>,"t":..}}
               (unified {ch,event,data} envelope, same as every other channel)
        Update Speed: 1000ms
        """
        stream_name = "mark_price@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def fund_rate(self, symbol, id=None, action=None):
        """
        Stream Name: fundrate@{symbol}
        Frame: {"ch":"fundrate","event":"fundrate@{symbol}","data":{"s":..,"r":<rate>,"t":..,"nt":<next>}}
        Update Speed: 60s
        """
        stream_name = "fundrate@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def best_price(self, symbol, id=None, action=None):
        """
        Best bid/ask streamed directly from the matching engine.
        Stream Name: best_price@{symbol}
        Frame: {"ch":"best_price","event":"best_price@{symbol}",
                "data":{"s":..,"a":<ask price>,"aa":<ask qty>,"b":<bid price>,"ba":<bid qty>,"t":..}}
        Update Speed: Real-time
        """
        stream_name = "best_price@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    # -------------------- private account channels --------------------
    # Plain channel names; the account comes from the handshake token.

    def user_balance(self, id=None, action=None):
        """
        :return: balance
        """
        self.send_message_to_server("balance", action=action, id=id)

    def user_position(self, id=None, action=None):
        """
        :return: position
        """
        self.send_message_to_server("position", action=action, id=id)

    def user_trade(self, id=None, action=None):
        """
        :return: trade
        """
        self.send_message_to_server("trade", action=action, id=id)

    def user_order(self, id=None, action=None):
        """
        :return: order
        """
        self.send_message_to_server("order", action=action, id=id)

    def user_notify(self, id=None, action=None):
        """
        :return: notify
        """
        self.send_message_to_server("notify", action=action, id=id)
