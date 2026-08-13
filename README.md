# azpython
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Official Python3 API connector for AZX's HTTP APIs.

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contact](#contact)

## About
Put simply, `azpython` (Python + AZX) is the official lightweight one-stop-shop module for the AZ.COM HTTP APIs. 

## Installation
`azpython` requires Python 3.9.1 or higher. The module can be installed manually or via [PyPI](https://pypi.org/project/azpython/) with `pip`:
```
pip install azpython
```

## Usage
You can retrieve a specific spot market like so:
```python
from azpython.spot import Spot
```

Create an HTTP session and connect via WebSocket for Inverse on mainnet:
```python
az = Spot(host="https://s-api.azverse.xyz", access_key='', secret_key='')
```

Information can be sent to, or retrieved from, the AZX APIs:
```python
print(az.balance("usdt"))
```

You can retrieve a specific future market like so:
```python
from azpython.perp import Perp
```

Create an HTTP session and connect via WebSocket for Inverse on mainnet:
```python
az = Perp(host="https://f-api.azverse.xyz", access_key='', secret_key='')
```

Information can be sent to, or retrieved from, the AZX APIs:
```python
print(az.get_account_capital())
```

## Hosts & endpoints

REST hosts (the `/az` path prefix is kept — do NOT drop it):

| Domain | REST host | Signed path prefix |
| ------ | --------- | ------------------ |
| Spot   | `https://s-api.azverse.xyz` | `/az/spot/...` |
| Future | `https://f-api.azverse.xyz` | `/az/future/...` |

Requests are signed with the `validate-*` HMAC-SHA256 headers (unchanged).

WebSocket endpoints (700 rebuild, base `wss://s-ws.azverse.xyz` / `wss://f-ws.azverse.xyz`):

| Domain | Public market | Private account |
| ------ | ------------- | --------------- |
| Spot   | `/spot/public` | `/ws/account/spot` |
| Future | `/futures/public` | `/ws/account/futures` |

* Public market: subscribe with plain channels (`ticker@btc_usdt`, `depth@btc_usdt`,
  `depth5@btc_usdt` (levels 5/10/20/50/100), `kline_1m@btc_usdt`, `deal@btc_usdt`, `tickers`,
  `best_price@btc_usdt`, `fundrate@btc_usdt`, `index_price@`/`mark_price@` (futures),
  `pred_ticker@`/`pred_tickers` (spot), ...). The ack is `{"id":..,"code":200,"msg":"success"}`
  (`code` 400/429 with a token `msg` on failure). Heartbeat is text `ping` → `pong` or JSON
  `{"method":"ping"}` → `{"pong":<ts>}`. **Every push frame is the unified envelope**
  `{"ch":<family>,"event":<subscription string>,"data":<obj|array>}` with short `data` keys
  (`v`/`uv`/`bp`/`bq`/`ap`/`aq`/`ix`/`mx`; full depth `ch:"depth_update"` with `u`/`pu`;
  fixed-level `ch:"depth"` with string `data.id`).
* Private account: there is no more `listenKey` — carry the login token **on the handshake**
  (`?token=<token>`; fetch the spot token via `POST /az/spot/ws-token`). The account comes from
  the token, so channels are plain names (`balance`, `order`, `trade`, `position`, `notify`, ...);
  heartbeat is text `ping` -> `pong`.
* Symbols are lowercase underscore, e.g. `btc_usdt`.

```python
from azpython.websocket.spot import SpotWebsocketStreamClient
client = SpotWebsocketStreamClient(is_auth=True, token="<accessToken>")
client.user_balance(action=SpotWebsocketStreamClient.ACTION_SUBSCRIBE)
```

## Examples
You can find more examples in the project folder /examples/

## Contact
You can reach out for support on the [AZAPI Telegram](https://localhost) group chat.
