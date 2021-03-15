"""
https://github.com/TiredFingers/poloniex-api
"""
import hmac
import hashlib
import urllib
import websockets
import json
import requests
from requests import Response
import datetime
from decimal import Decimal


class PoloniexConnector:

    __public_key = ""
    __private_key = ""
    __rest_api_url = ""
    __ws_api_url = ""
    __ws_connections = dict()
    __currencies = dict()

    def __init__(self, pub_key: str, priv_key: str, rest_api_url="https://poloniex.com/",
                 ws_api_url="wss://api2.poloniex.com") -> None:

        self.__public_key = pub_key
        self.__private_key = priv_key
        self.__rest_api_url = rest_api_url
        self.__ws_api_url = ws_api_url

    @staticmethod
    def get_nonce() -> int:
        return int(datetime.datetime.now().timestamp() * 1000)

    def return_ticker(self) -> Response:
        """
        :return: requests.Response obj

        :version 1.0.1
        :rev 11.01.2021
        """
        return self.__get_public_command({
            "command": "returnTicker"
        })

    def return_24_volume(self) -> Response:
        """
        :return: requests.Response obj

        :version 1.0.1
        :rev 11.01.2021
        """
        return self.__get_public_command({
            "command": "return24hVolume"
        })

    def return_order_book(self, pair_ticker: str, depth=10) -> Response:
        """
        :param pair_ticker: str
        :param depth: int
        :return: requests.Response obj

        :version 1.0.2
        :rev 11.01.2021
        """
        return self.__get_public_command({
                "command":"returnOrderBook",
                "currencyPair": str(pair_ticker),
                "depth": str(depth)
            })

    def return_public_trade_history(self, pair: str, start=0, end=0) -> Response:
        """
        :param str pair:
        :param int start:
        :param int end:
        :return: requests.Response obj

        :version 1.0.1
        :rev 11.01.2021
        """

        payload = {
            "command": "returnTradeHistory",
            "currencyPair": str(pair)
        }

        if start > 0:
            payload["start"] = start

        if end > 0:
            payload["end"] = end

        return self.__get_public_command(payload)

    def return_chart_data(self, pair: str, start: int, end: int, period: int) -> Response:
        """
        :param str pair:
        :param unix timestamp start:
        :param unix timestamp end:
        :param int period: (300, 900, 1800, 7200, 14400, 86400)
        :return: requests.Response obj

        :version 1.0.1
        :rev 11.01.2021
        """
        return self.__get_public_command({
            "command": "returnChartData",
            "currencyPair": str(pair),
            "start": start,
            "end": end,
            "period": period
        })

    def return_currencies(self) -> Response:
        """
        :return: requests.Response obj

        :version 1.0.1
        :revision 11.01.2021
        """
        return self.__get_public_command({
            "command": "returnCurrencies"
        })

    def init_currencies(self) -> None:
        """
        :return: None

        :version 1.0.1
        :revision 11.01.2021
        """
        currencies = self.return_currencies().json()

        for currency in currencies:
            self.__currencies[currencies[currency]["id"]] = currencies[currency]
            self.__currencies[currencies[currency]["id"]]["ticker"] = currency

    def get_currencies(self) -> dict:
        """
        :return: dict

        :version 1.0.1
        :revision 11.01.2021
        """
        return self.__currencies

    def return_loan_orders(self, currency: str) -> Response:
        """
        :param str currency:
        :return: requests.Response obj

        :version 1.0.1
        :rev 11.01.2021
        """
        return self.__get_public_command({
            "command": "returnLoanOrders",
            "currency": currency
        })

    def return_balances(self) -> Response:
        """
        :return: requests.Response object

        :version 1.0.1
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnBalances",
            "nonce": self.get_nonce()
        })

    def return_complete_balances(self) -> Response:
        """
        :return: requests.Response object

        :version 1.0.1
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnCompleteBalances",
            "nonce": self.get_nonce()
        })

    def return_deposit_addresses(self) -> Response:
        """
        :return: requests.Response object

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnDepositAddresses",
            "nonce": self.get_nonce()
        })

    def return_open_orders(self, pair_ticker: str) -> Response:
        """
        :return: requests.Response object

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnOpenOrders",
            "currencyPair": str(pair_ticker),
            "nonce": self.get_nonce()
        })

    def return_trade_history(self, pair_ticker: str) -> Response:
        """
        :return: requests.Response object

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnTradeHistory",
            "currencyPair": str(pair_ticker),
            "nonce": self.get_nonce()
        })

    def return_order_trades(self, order_number: str) -> Response:
        """
        :param order_number str
        :return: requests.Response object

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnOrderTrades",
            "orderNumber": str(order_number),
            "nonce": self.get_nonce()
        })

    def return_order_status(self, order_number) -> Response:
        """
        :param order_number str
        :return: requests.Response object

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnOrderStatus",
            "orderNumber": str(order_number),
            "nonce": self.get_nonce()
        })

    def buy(self, ticker: str, rate: Decimal, amount: Decimal, fill_or_kill=0, immidiate_or_cancel=0, post_only=0) -> Response:
        """
        :param str ticker:
        :param Decimal rate: how much you want to spend
        :param Decimal amount: how much you need to buy
        :param int fill_or_kill:
        :param int immidiate_or_cancel:
        :param int post_only:
        :return: requests.Response object

        :version 1.0.0
        :rev 11.01.2021
        """
        post_data = {
            "command": "buy",
            "currencyPair": str(ticker),
            "rate": rate,
            "amount": amount,
            "nonce": self.get_nonce()
        }

        if fill_or_kill == 1:
            post_data["fillOrKill"] = 1

        if immidiate_or_cancel == 1:
            post_data["immediateOrCancel"] = 1

        if post_only == 1:
            post_data["postOnly"] = 1

        return self.__post_private_command(post_data)

    def sell(self, ticker: str, rate: Decimal, amount: Decimal) -> Response:
        """
        :param str ticker:
        :param Decimal rate:
        :param Decimal amount:
        :return: requests.Response object

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "sell",
            "currencyPair": str(ticker),
            "rate": rate,
            "amount": amount,
            "nonce": self.get_nonce()
        })

    def cancel_order(self, order_number: str) -> Response:
        """
        :param order_number str
        :return: Response obj

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "cancelOrder",
            "orderNumber": str(order_number),
            "nonce": self.get_nonce()
        })

    def move_order(self, order_number: str, rate: Decimal) -> Response:
        """
        :param order_number str
        :param rate Decimal
        :return: Response obj

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "moveOrder",
            "orderNumber": order_number,
            "rate": rate,
            "nonce": self.get_nonce()
        })

    def return_fee_info(self) -> Response:
        """
        :return: requests.Response obj

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnFeeInfo",
            "nonce": self.get_nonce()
        })

    def return_available_account_balances(self) -> Response:
        """
        :return: requests.Response obj

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnAvailableAccountBalances",
            "nonce": self.get_nonce()
        })

    def return_tradable_balances(self) -> Response:
        """
        :return: requests.Response obj

        :version 1.0.0
        :rev 11.01.2021
        """
        return self.__post_private_command({
            "command": "returnTradableBalances",
            "nonce": self.get_nonce()
        })

    async def subscribe_to_public_channel(self, channel_id: int):
        """
        :return websocket connection

        :version 1.0.0
        :rev 11.01.2021
        """
        await self.__ws_connect(channel_id)
        await self.__ws_send({
            "command": "subscribe",
            "channel": channel_id
        }, channel_id)

        return self.__ws_connections[channel_id]

    async def subscribe_to_private_channel(self, channel_id: int):
        """
        :param int channel_id:
        :return: void

        await self.__ws_connect(channel_id)
        await self.__ws_send({
            "command": "subscribe",
            "channel": channel_id,
            "sign": hmac.new(self.__private_key.encode(), digestmod=hashlib.sha512).hexdigest(),
            "key": self.__public_key,
            "payload": "nonce=" + str(self.get_nonce())
        }, channel_id)

        while True:
            resp = await self.__ws_connections[channel_id].recv()
            print(resp)
        """
        pass

    def get_public_key(self) -> str:
        return self.__public_key

    def get_private_key(self) -> str:
        return self.__private_key

    def reset_connection(self) -> None:
        self.__public_key = ""
        self.__private_key = ""

    def get_first_sell_price(self, pair: str) -> Decimal:
        """
        :param pair: str
        :return: Decimal

        :version 1.0.0
        :revision 11.01.2021
        """
        json_res = self.return_order_book(pair, 1).json()

        if "asks" in json_res and len(json_res["asks"]) > 0 and len(json_res["asks"][0]) > 0:

            return Decimal(json_res["asks"][0][0])

        return Decimal(0)

    def get_common_commission(self) -> Decimal:
        """

        :return: Decimal
        :version 1.0.0
        :revision 11.01.2021
        """
        res = self.return_fee_info().json()
        return Decimal(res['makerFee']) + Decimal(res['takerFee'])

    async def __ws_connect(self, channel_id: int) -> None:
        """
        :param int channel_id:
        :return: None

        :version 1.0.1
        :rev 11.01.2021
        """
        self.__set_ws_connection(
            await websockets.connect(self.__ws_api_url),
            channel_id
        )

    async def __ws_send(self, payload, channel_id) -> None:
        """
        :param dict payload:
        :param int channel_id:
        :return: None

        :version 1.0.1
        :revision 11.01.2021
        """
        await self.__ws_connections[channel_id].send(json.dumps(payload))

    def __set_ws_connection(self, ws_connection, channel_id: int) -> None:
        """
        :param connection object ws_connection:
        :param int channel_id:
        :return: None

        :version 1.0.1
        :revision 11.01.2021
        """
        self.__ws_connections[channel_id] = ws_connection

    def __get_public_command(self, payload: dict) -> Response:
        """
        :param dict payload:
        :return: requests.Response

        ver 1.0.2
        rev 11.01.2021
        """
        return requests.get(self.__rest_api_url + "public", params=payload)

    def __post_private_command(self, payload: dict) -> Response:
        """
        :param payload: dict
        :return: requests.Response obj

        ver 1.0.1
        rev 11.01.2021
        """
        post_data = urllib.parse.urlencode(payload).encode()

        sign = hmac.new(self.__private_key.encode(), post_data, hashlib.sha512).hexdigest()

        headers = {
            'Sign': sign.encode(),
            'Key': self.__public_key.encode()
        }

        return requests.post(self.__rest_api_url + "tradingApi", data=payload, headers=headers)
