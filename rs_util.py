#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/15
# Function: huobi websocket api访问方法

from base64 import b64encode
from datetime import datetime
# import hashlib
from hashlib import sha256
import hmac
import json
# import urllib
import urllib.parse
# import urllib.request
# import requests
from requests import get, post
import logging
import log_config
import config
from util import deco_retry

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

logger = logging.getLogger(__name__)

"""Huobi rest api接口工具类"""


class HuobiREST:
    def __init__(self, timeout=config.NET_TIMEOUT):
        self._market_url = config.PLATFORMS["huobi"]["rest_market_url"]["default"]
        self._trade_url = config.PLATFORMS["huobi"]["rest_trade_url"]["default"]
        self._access_key = config.ACCESS_KEY
        self._secret_key = config.SECRET_KEY
        self._private_key = config.PLATFORMS["huobi"]["private_key"]
        self._account_id = None
        self._account_state = None
        self._timeout = timeout

    @property
    def account_id(self):
        return self._account_id

    @property
    def account_state(self):
        return self._account_state

    def _http_get(self, url, params, add_to_headers=None):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
            'Accept-Language': 'zh-cn'
        }
        if add_to_headers:
            headers.update(add_to_headers)

        post_data = urllib.parse.urlencode(params)
        try:
            logging.info("RESTAPI, GET: {}".format(url))
            # log_config.output2ui("RESTAPI, GET: {}".format(url))
            response = get(url, post_data, headers=headers, timeout=self._timeout)
            # logger.debug("RESTAPI _http_get url:{}\n post_data:{}\n response: {}".format(url, post_data, response.json()))
            # log_config.output2ui("RESTAPI _http_get url:{}\n post_data:{}\n response: {}".format(url, post_data, response.json()))
            return response.status_code, response.json()
        except Exception as e:
            logger.exception("RESTAPI _http_getException, url:{}\n post_data:{}\n e: {}".format(url, post_data, e))
            log_config.output2ui("RESTAPI _http_get Exception, url:{}\n post_data:{}\n e: {}".format(url, post_data, e), 4)
            return -1, None

    def _http_post(self, url, params, add_to_headers=None):
        headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-cn'
        }
        if add_to_headers:
            headers.update(add_to_headers)

        try:
            post_data = json.dumps(params)
            logger.info("RESTAPI, POST: {}".format(url))
            response = post(url, post_data, headers=headers, timeout=self._timeout)
            # logger.debug("RESTAPI _http_post, url:{}\n post_data:{}\n response: {}".format(url, post_data, response.json()))
            # log_config.output2ui(
            #     "RESTAPI _http_post, url:{}\n post_data:{}\n response: {}".format(url, post_data, response.json()))
            return response.status_code, response.json()
        except Exception as e:
            logger.exception("RESTAPI _http_post Exception, url:{}\n post_data:{}\n e: {}".format(url, post_data, e))
            log_config.output2ui("RESTAPI _http_post Exception, url:{}\n post_data:{}\n e: {}".format(url, post_data, e), 4)
            return -1, None

    def _http_get_with_key(self, params, request_path):
        method = 'GET'
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params.update({'AccessKeyId': self._access_key,
                       'SignatureMethod': 'HmacSHA256',
                       'SignatureVersion': '2',
                       'Timestamp': timestamp})

        trade_url = self._trade_url
        url_get = trade_url + request_path
        host_name = urllib.parse.urlparse(url_get).hostname
        host_name = host_name.lower()
        request_path = urllib.parse.urlparse(url_get).path
        request_path = request_path.lower()
        params['Signature'] = self._create_sign(params, method, host_name, request_path, self._secret_key)
        params['PrivateSignature'] = self._createPrivateSignature(params['Signature'])
        logger.info("{}".format(params))
        return self._http_get(url_get, params)

    def _http_post_with_key(self, params, request_path):
        method = 'POST'
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params_to_sign = {'AccessKeyId': self._access_key,
                          'SignatureMethod': 'HmacSHA256',
                          'SignatureVersion': '2',
                          'Timestamp': timestamp}

        trade_url = self._trade_url
        url_post = trade_url + request_path
        host_name = urllib.parse.urlparse(url_post).hostname
        host_name = host_name.lower()
        request_path = urllib.parse.urlparse(url_post).path
        request_path = request_path.lower()
        params_to_sign['Signature'] = self._create_sign(params_to_sign, method, host_name, request_path, self._secret_key)
        params_to_sign['PrivateSignature'] = self._createPrivateSignature(params_to_sign['Signature'])
        url = url_post + '?' + urllib.parse.urlencode(params_to_sign)
        return self._http_post(url, params)

    def _create_sign(self, params, method, host_name, request_path, secret_key):
        sorted_params = sorted(params.items(), key=lambda d: d[0], reverse=False)
        encode_params = urllib.parse.urlencode(sorted_params)
        payload = [method, host_name, request_path, encode_params]
        payload = '\n'.join(payload)
        payload = payload.encode(encoding='UTF8')
        secret_key = secret_key.encode(encoding='UTF8')

        digest = hmac.new(secret_key, payload, digestmod=sha256).digest()
        signature = b64encode(digest)
        signature = signature.decode()
        return signature

    def _createPrivateSignature(self, context):
        data = bytes(context, encoding='utf8')
        # Read the pri_key_file
        digest = hashes.Hash(hashes.SHA256(), default_backend())

        digest.update(data)
        dgst = digest.finalize()
        skey = load_pem_private_key(self._private_key, password=None, backend=default_backend())

        sig_data = skey.sign(data, ec.ECDSA(hashes.SHA256()))
        sig_r, sig_s = decode_dss_signature(sig_data)

        sig_bytes = b''
        key_size_in_bytes = self._bit_to_bytes(skey.public_key().key_size)
        sig_r_bytes = sig_r.to_bytes(key_size_in_bytes, "big")
        sig_bytes += sig_r_bytes
        # print("ECDSA signature R: {:s}".format(sig_r_bytes.hex()))
        sig_s_bytes = sig_s.to_bytes(key_size_in_bytes, "big")
        sig_bytes += sig_s_bytes
        #  print("ECDSA signature S: {:s}".format(sig_s_bytes.hex()))
        # print("ECDSA signautre: {:s}".format(sig_bytes.hex()))
        # print("ECDSA signautre: " + str(base64.b64encode(sig_bytes)))
        return b64encode(sig_bytes)

    def _bit_to_bytes(self, a):
        return (a + 7) // 8

    # 获取KLine
    def get_kline(self, symbol, period="60min", size=150):
        """
        :param symbol
        :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        :param size: 可选值： [1,2000]
        :return:
        """
        params = {'symbol': symbol,
                  'period': period,
                  'size': size}

        url = self._market_url + '/history/kline'
        return self._http_get(url, params)

    # 获取marketdepth
    def get_depth(self, symbol, depth_type):
        """
        :param symbol
        :param depth_type: 可选值：{ percent10, step0, step1, step2, step3, step4, step5 }
        :return:
        """
        params = {'symbol': symbol,
                  'type': depth_type}

        url = self._market_url + '/depth'
        return self._http_get(url, params)

    # 获取tradedetail

    def get_trade(self, symbol):
        """
        :param symbol
        :return:
        """
        params = {'symbol': symbol}
        url = self._market_url + '/trade'
        return self._http_get(url, params)

    #size=[1, 2000]
    # {
    #     "status": "ok",
    #     "ch": "market.ethusdt.trade.detail",
    #     "ts": 1502448925216,
    #     "data": [
    #         {
    #             "id": 31459998,
    #             "ts": 1502448920106,
    #             "data": [
    #                 {
    #                     "id": 17592256642623,
    #                     "amount": 0.04,
    #                     "price": 1997,
    #                     "direction": "buy",
    #                     "ts": 1502448920106
    #                 }
    #             ]
    #         }
    #     ]
    # }
    @deco_retry()
    def get_history_trade(self, symbol, size=100):
        """
        :param symbol
        :return:
        """
        params = {'symbol': symbol,
                  'size': size,
                  'AccessKeyId': self._access_key}
        url = self._market_url + '/history/trade'
        return self._http_get(url, params)

    # 获取merge ticker
    def get_ticker(self, symbol):
        """
        :param symbol:
        :return:
        """
        params = {'symbol': symbol}

        url = self._market_url + '/detail/merged'
        return self._http_get(url, params)

    # 获取 Market Detail 24小时成交量数据
    def get_detail(self, symbol):
        """
        :param symbol
        :return:
        """
        params = {'symbol': symbol,
                  'AccessKeyId': self._access_key}

        url = self._market_url + '/detail'
        return self._http_get(url, params)

    # 获取  支持的交易对

    def get_symbols(self, long_polling=None):
        """
        """
        params = {}
        if long_polling:
            params['long-polling'] = long_polling
        path = '/common/symbols'
        return self._http_get_with_key(params, path)

    '''
    Trade/Account API
    '''
    @deco_retry(retry_times=4)
    def get_accounts(self):
        """
        :return:
        """
        path = "/account/accounts"
        params = {}
        code, response = self._http_get_with_key(params, path)
        logger.info("get_accounts code = {c}, response={r}".format(c=code, r=response))
        # logger.info("get_accounts code = %d" % code)
        # logger.info("get_accounts code = %d", code)
        if code == 200 and response["data"]:
            try:
                self._account_id = response['data'][0]['id']
                self._account_state = response['data'][0]['state']
                config.ACCOUNT_ID = self._account_id
                config.ACCOUNT_STATE = self._account_state
                return code, response
            except Exception as e:
                logger.exception("get_accounts failed ,e =%s" % e)
                log_config.output2ui("get_accounts failed ,e =%s" % e, 4)
        self._account_id = None
        self._account_state = None
        config.ACCOUNT_ID = None
        config.ACCOUNT_STATE = None
        return code, None

    # 获取当前账户资产
    @deco_retry()
    def get_balance(self, acct_id=None, currency=None):
        '''
        :param acct_id:
        :param currency:
        :return:
        '''
        if not acct_id:
            acct_id = self.get_account_id()

        url = "/account/accounts/{0}/balance".format(acct_id)
        params = {"account-id": acct_id}
        ret = self._http_get_with_key(params, url)
        if not currency:
            return ret
        else:
            if ret[0] != 200:
                return ret
            response = ret[1]
            if response.get("status", None) != config.STATUS_OK:
                return ret[0], None

            data = response.get("data", None)
            state = data.get("state")
            if state != "working":
                logger.warning("balance is not working!!")
                log_config.output2ui("balance is not working!!", 2)
            bal_list = data.get("list", [])
            balance = {"trade": 0, "frozen": 0}
            for bal in bal_list:
                if bal.get("currency", "") == currency:
                    str_balance = bal.get("balance", "0")
                    num_balance = float(str_balance)
                    balance[bal.get("type", "unknown")] = num_balance
            return 200, balance

    def get_account_id(self):
        if self._account_id:
            return self._account_id
        elif config.ACCOUNT_ID:
            return config.ACCOUNT_ID

        self.get_accounts()
        return self._account_id

    # 下单
    # 创建并执行订单
    @deco_retry()
    def send_order(self, amount, source, symbol, _type, price=0):
        """
        :param amount: 限价单表示下单数量，市价买单时表示买多少钱，市价卖单时表示卖多少币
        :param source: 如果使用借贷资产交易，请在下单接口,请求参数source中填写'margin-api'
        :param symbol: 交易对btcusdt, bchbtc, rcneth ...
        :param _type: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param price:
        :return:
        """
        acct_id = self.get_account_id()

        params = {"account-id": acct_id,
                  "amount": amount,
                  "symbol": symbol,
                  "type": _type,
                  "source": source}
        if price:
            params["price"] = price

        url = '/order/orders/place'
        ret = self._http_post_with_key(params, url)
        if ret[0] != 200:
            return ret[0], None
        else:
            response = ret[1]
            if not response or response.get("status", "error") != "ok":
                return ret[0], None #response.get("err-msg", "status error")
            return ret[0], response.get("data", "")



    # 撤销订单
    @deco_retry()
    def cancel_order(self, order_id):
        """
        :param order_id:
        :return:
        """
        params = {}
        url = "/order/orders/{0}/submitcancel".format(order_id)
        return self._http_post_with_key(params, url)

    # 查询某个订单

    def order_info(self, order_id):
        """
        :param order_id:
        :return:
        """
        params = {}
        url = "/order/orders/{0}".format(order_id)
        return self._http_get_with_key(params, url)

    # 查询某个订单的成交明细

    def order_matchresults(self, order_id):
        """
        :param order_id:
        :return:
        """
        params = {}
        url = "/order/orders/{0}/matchresults".format(order_id)
        return self._http_get_with_key(params, url)

    # 查询当前委托、历史委托

    def orders_list(self, symbol, states, types=None, start_date=None, end_date=None, _from=None, direct=None, size=None):
        """

        :param symbol:
        :param states: 可选值 {pre-submitted 准备提交, submitted 已提交, partial-filled 部分成交, partial-canceled 部分成交撤销, filled 完全成交, canceled 已撤销}
        :param types: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date:
        :param end_date:
        :param _from:
        :param direct: 可选值{prev 向前，next 向后}
        :param size:
        :return:
        """
        params = {'symbol': symbol,
                  'states': states}

        if types:
            params[types] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        url = '/order/orders'
        return self._http_get_with_key(params, url)

    # 查询当前成交、历史成交

    def orders_matchresults(self, symbol, types=None, start_date=None, end_date=None, _from=None, direct=None, size=None):
        """
        :param symbol:
        :param types: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date:
        :param end_date:
        :param _from:
        :param direct: 可选值{prev 向前，next 向后}
        :param size:
        :return:
        """
        params = {'symbol': symbol}

        if types:
            params[types] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        url = '/order/matchresults'
        return self._http_get_with_key(params, url)

    # 申请提现虚拟币

    def withdraw(self, address, amount, currency, fee=0, addr_tag=""):
        """
        :param address_id:
        :param amount:
        :param currency:btc, ltc, bcc, eth, etc ...(火币Pro支持的币种)
        :param fee:
        :param addr-tag:
        :return: {
                  "status": "ok",
                  "data": 700
                }
        """
        params = {'address': address,
                  'amount': amount,
                  "currency": currency,
                  "fee": fee,
                  "addr-tag": addr_tag}
        url = '/dw/withdraw/api/create'
        return self._http_post_with_key(params, url)


    def query_deposit_withdraw_history(self, currency, _type="deposit", _from=None, size=None):
        params = {'crrency': currency,
                  'type': _type}
        url = '/query/deposit-withdraw'
        return self._http_post_with_key(params, url)
    # 申请取消提现虚拟币

    def cancel_withdraw(self, address_id):
        """
        :param address_id:
        :return: {
                  "status": "ok",
                  "data": 700
                }
        """
        params = {}
        url = '/dw/withdraw-virtual/{0}/cancel'.format(address_id)
        return self._http_post_with_key(params, url)

    '''
    借贷API
    '''
    # 创建并执行借贷订单

    def send_margin_order(self, amount, symbol, _type, price=0):
        """
        :param amount:
        :param source: 'margin-api'
        :param symbol:
        :param _type: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param price:
        :return:
        """

        acct_id = self.get_account_id()
        params = {"account-id": acct_id,
                  "amount": amount,
                  "symbol": symbol,
                  "type": _type,
                  "source": 'margin-api'}
        if price:
            params["price"] = price

        url = '/order/orders/place'
        return self._http_post_with_key(params, url)

    # 现货账户划入至借贷账户

    def exchange_to_margin(self, symbol, currency, amount):
        """
        :param amount:
        :param currency:
        :param symbol:
        :return:
        """
        params = {"symbol": symbol,
                  "currency": currency,
                  "amount": amount}

        url = "/dw/transfer-in/margin"
        return self._http_post_with_key(params, url)

    # 借贷账户划出至现货账户

    def margin_to_exchange(self, symbol, currency, amount):
        """
        :param amount:
        :param currency:
        :param symbol:
        :return:
        """
        params = {"symbol": symbol,
                  "currency": currency,
                  "amount": amount}

        url = "/dw/transfer-out/margin"
        return self._http_post_with_key(params, url)

    # 申请借贷

    def get_margin(self, symbol, currency, amount):
        """
        :param amount:
        :param currency:
        :param symbol:
        :return:
        """
        params = {"symbol": symbol,
                  "currency": currency,
                  "amount": amount}
        url = "/margin/orders"
        return self._http_post_with_key(params, url)

    # 归还借贷

    def repay_margin(self, order_id, amount):
        """
        :param order_id:
        :param amount:
        :return:
        """
        params = {"order-id": order_id,
                  "amount": amount}
        url = "/margin/orders/{0}/repay".format(order_id)
        return self._http_post_with_key(params, url)

    # 借贷订单

    def loan_orders(self, symbol, currency, start_date="", end_date="", start="", direct="", size=""):
        """
        :param symbol:
        :param currency:
        :param direct: prev 向前，next 向后
        :return:
        """
        params = {"symbol": symbol,
                  "currency": currency}
        if start_date:
            params["start-date"] = start_date
        if end_date:
            params["end-date"] = end_date
        if start:
            params["from"] = start
        if direct and direct in ["prev", "next"]:
            params["direct"] = direct
        if size:
            params["size"] = size
        url = "/margin/loan-orders"
        return self._http_get_with_key(params, url)

    # 借贷账户详情,支持查询单个币种

    def margin_balance(self, symbol):
        """
        :param symbol:
        :return:
        """
        params = {}
        url = "/margin/accounts/balance"
        if symbol:
            params['symbol'] = symbol

        return self._http_get_with_key(params, url)

    #计算买卖单量，
    def count_sell_buy(self, response, big_limit=10):
        result = {"buy": 0, "sell": 0, "big_buy": 0, "big_sell": 0}
        if response.get("status", "") != "ok":
            return None

        try:
            data = response.get("data", [])
            for d in data:
                ld = d.get("data", [])
                for sd in ld:
                    amount = sd.get("amount")
                    direction = sd.get("direction")
                    if amount >= big_limit:
                        result["big_"+direction] += 1
                    result[direction] += amount
        except Exception as e:
            logger.exception("count_sell_buy e={}".format(e))
            log_config.output2ui("count_sell_buy e={}".format(e), 4)
        return result

    def count_depth(self, response):
        if response.get("status", "") != "ok":
            return None
        result = {"bids": {"total": 0, "sum_amount": 0, "avg_price": 0},
                  "asks": {"total": 0, "sum_amount": 0, "avg_price": 0}}
        try:
            tick = response.get("tick", [])
            bids = tick.get("bids", [])
            sum_bid_amount = 0
            sum_bids = 0
            for bid in bids:
                price = bid[0]
                amount = bid[1]
                sum_bid_amount += amount
                sum_bids += (price*amount)
            result["bids"]["sum_amount"] = sum_bid_amount
            result["bids"]["total"] = sum_bids
            result["bids"]["avg_price"] = sum_bids/sum_bid_amount

            sum_ask_amount = 0
            sum_asks = 0
            asks = tick.get("asks", [])
            for ask in asks:
                price = ask[0]
                amount = ask[1]
                sum_ask_amount += amount
                sum_asks += (price*amount)
            result["asks"]["sum_amount"] = sum_ask_amount
            result["asks"]["total"] = sum_asks
            result["asks"]["avg_price"] = sum_asks/sum_ask_amount
        except Exception as e:
            logger.exception("count_depth e={}".format(e))
            log_config.output2ui("count_depth e={}".format(e), 4)
        return result


def test_MA(hrs, symbol="btcusdt", kl_type="5min", timeperiod=[5, 10, 30, 60]):
    import talib
    import matplotlib.pyplot as plt
    import numpy as np
    result = hrs.get_kline(symbol, kl_type)
    if result[0] == 200 and result[1]["status"] == "ok":
        close = []
        for data in result[1]["data"]:
            close.insert(0, data["close"])
        for t in timeperiod:
            ma = talib.MA(np.array(close), timeperiod=t)
            plt.plot(ma)
        plt.show()


def test_MACD(hrs, symbol="btcusdt", kl_type="5min", size=24, arg=[12, 26, 9]):
    import talib
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    result = hrs.get_kline(symbol, kl_type, size=size)
    # dw = pd.DataFrame([], [ "DIF", "DEA", "MACD"])

    if not (result[0] == 200 and result[1]["status"] == "ok"):
        print("test_MACD failed.result={}".format(result))

    close = []
    for data in result[1]["data"]:
        close.insert(0, data["close"])
    # macd = 12 天 EMA - 26 天 EMA,  ==== DIF
    # signal = 9 天 MACD的EMA   ===== DEA
    # hist = MACD - MACD signal  =====  hist
    # dw["close"] = np.array(close)
    dw = pd.DataFrame({"close": close})
    print(len(close))
    print(close)
    dif, dea, hist = talib.MACD(np.array(close), fastperiod=arg[0], slowperiod=arg[1], signalperiod=arg[2])
    dw["DIF"], dw["DEA"], dw["MACD"] = talib.MACD(np.array(close), fastperiod=arg[0], slowperiod=arg[1], signalperiod=arg[2])
    print(dw["DIF"])
    print(dw["DEA"])
    print(dw["MACD"])
   # dw["DIF"].append(dif, ignore_index=True)
    # plt.plot(dif)
    # plt.plot(dea)
    # plt.plot(hist)
    dw[['DIF', 'DEA']].plot()
    plt.show()


if __name__ == '__main__':
    from config import CURRENT_REST_MARKET_URL, CURRENT_REST_TRADE_URL, ACCESS_KEY, SECRET_KEY, PRIVATE_KEY
    hrs = HuobiREST(CURRENT_REST_MARKET_URL, CURRENT_REST_TRADE_URL, ACCESS_KEY, SECRET_KEY, PRIVATE_KEY)
    # print("get_symbols = {}".format(hrs.get_symbols()))
    # print("get_accounts = {}".format(hrs.get_accounts()))
    # print(hrs._account_id)
    print("get_balance = {}".format(hrs.get_balance(currency="eth")))
    print("get_balance = {}".format(hrs.get_balance(currency="usdt")))
    # exit(1)
    # print("get_trade = {}".format(hrs.get_trade("btcusdt")))

    # res = hrs.get_history_trade("ethusdt", 300)
    # print("get_history_trade = {}".format(res))
    # print(hrs.count_sell_buy(res[1]))
    # exit(1)

    # buy------------
    # ret = hrs.send_order(690, source="api", symbol="ethusdt", _type="buy-market")
    # print("send_order = {}".format(ret))
    # print("order_info = {}".format(hrs.order_info(ret[1])))

    # sell ---------
    ret = hrs.send_order(0.01, source="api", symbol="ethusdt", _type="sell-market")
    print("send_order = {}".format(ret))
    print("order_info = {}".format(hrs.order_info(ret[1])))

    # print("get_order = {}".format(hrs.get_order("ethusdt")))
    # ret = hrs.get_depth("ethusdt", "step0")
    # print("get_depth = {}".format(ret))
    # print("get_depth = {}".format(hrs.count_depth(ret[1])))
    # # print("get_kline = {}".format(hrs.get_kline("ethusdt", "5min")))
    # print("get_detail = {}".format(hrs.get_detail("ethusdt")))
    # print("send_order = {}".format(hrs.send_order(0.8, source="api", symbol="ethusdt", _type="buy-market")))


    # print("order_info = {}".format(hrs.order_info("6361787095")))
    print("order_list = {}".format(hrs.orders_list("ethusdt", "filled")))  # "submitted"
    print("query_deposit_withdraw_history = {}".format(hrs.query_deposit_withdraw_history("eth", "withdraw")))  # "submitted"
    # test_MA(hrs)
    # test_MACD(hrs,symbol="btcusdt", kl_type="5min", size=150)
    # ret = hrs.send_order(1, source="api", symbol="ethusdt", _type="buy-market")
    # if ret[0]:
    #     order_id = ret[1]
    #     order_response = hrs.order_info(order_id)
    #     if order_response[0] == 200:
    #         if order_response[1].get("status", "") == "ok":
    #             order_dtail = order_response[1].get("data", {})
    #             print("order success: {}".format(order_dtail))
    #             # TRADE_RECORD.append(order_dtail)