#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/15
# Function:
import time
from ws_util import HuobiWS
from rs_util import HuobiREST
import config
import process
import db_util
import logging
import log_config
logger = logging.getLogger(__name__)
import threading

class Huobi:
    def __init__(self, debug=False):
        self._hws = None
        self._db = None
        self._debug = debug
        self._run = False
        
    def _init_ws(self):
        logger.info("-------start connect web socket server.")
        log_config.output2ui("-------start connect web socket server.")
        self._hws = HuobiWS(config.CURRENT_WS_URL)
        ret = self._hws.ws_connect()
        if not ret:
            logger.error("init_ws failed.")
            log_config.output2ui("init_ws failed.", 3)
            return False
        self._hws.start_recv()
        return True

    #抓取历史数据
    def _req_history_kline(self):
        logger.info("---req_history_kline.")
        log_config.output2ui("---req_history_kline.")
        for symbol in config.NEED_TOBE_SUB_SYMBOL:
            for kl in config.KL_HISTORY:
                channel = "market.{}.kline.{}".format(symbol, kl)
                logger.info("---req_history_kline: {}.".format(channel))
                log_config.output2ui("---req_history_kline: {}.".format(channel))
                #只能拿到最近的300条数据 ，可用
                if self._hws:
                    self._hws.ws_req(channel, process.kline_req_msg_process)
                time.sleep(1.5)
        return True

    #开始订阅
    def _sub_market(self):
        logger.info("---start sub.")
        log_config.output2ui("--start sub.")
        for symbol in config.NEED_TOBE_SUB_SYMBOL:
            for kl in config.KL_ALL:
                channel = "market.{}.kline.{}".format(symbol, kl)
                logger.info("-sub_market: {}.".format(channel))
                log_config.output2ui("-sub_market: {}.".format(channel))
                self._hws.ws_sub(channel, process.kline_sub_msg_process)

    def _init_db(self):
        du = db_util.DBUtil()
        du.init()
        db_util.DB_INSTANCE = du
        self._db = du
        return True

    def _show_result(self, suffix=""):
        for channel, df in process.KLINE_DATA.items():
            logger.info("\n{} data:\n{}".format(channel, df))
            process.plot_candle_chart(df, type=2, pic_name=channel+suffix)

    def init(self):
        ret1 = self._init_ws()
        ret2 = True
        if config.DB_SAVE:
            ret2 = self._init_db()
        return ret1 and ret2

    def init_history(self):
        return self._req_history_kline()

    def run(self, after=None):
        if not self._hws:
            self._init_ws()
            self._init_db()

        self._sub_market()
        if self._debug:
            self._show_result("1")
        self._run = True
        run_time = 0
        log_config.output2ui("Start work successfully!", 8)
        while self._run:
            time.sleep(1)
            if after and run_time > after:
                break
            run_time += 1
        return True

    def exit(self):
        self._run = False
        if self._hws:
            self._hws.ws_close()
            self._hws = None
        if self._db:
            self._db.close()
            self._db = None
        if self._debug:
            self._show_result("2")
        return True

    def history_trade_test(self, symbol, kline):
        channel = "market.{}.kline.{}".format(symbol, kline)
        logger.info("---req_history_kline: {}.".format(channel))
        # log_config.output2ui("---req_history_kline: {}.".format(channel))
        # 只能拿到最近的300条数据 ，可用
        if self._hws:
            self._hws.ws_req(channel, process.kline_req_msg_process)
        time.sleep(0.5)


# 循环获取历史交易量信息
def save_history_trade_vol(symbols):
    def save_history(symbols):
        before_time = 300        # 初始化时拿5个5分钟周期数据,因为最多只允许拿2000条
        for symbol in symbols:
            trade_vol_list = []
            num = 4
            while num > 0:
                beg = num * before_time
                result = get_trade_vol_by_time(symbol, beg, before_time=before_time, big_limit=10)
                if result:
                    trade_vol_list.append(result)
                    process.TRADE_VOL_HISTORY[symbol] = trade_vol_list
                num -= 1

        while 1:

            try:
                for symbol in symbols:
                    trade_vol_list = process.TRADE_VOL_HISTORY.get(symbol, [])
                    if len(trade_vol_list) > 0:
                        last_end_time = trade_vol_list[-1].get("end_time", 0)
                        current_time = int(time.time())*1000
                        before_time = round((current_time-last_end_time)/1000)+1
                    result = get_trade_vol_by_time(symbol, 0, before_time=before_time, big_limit=10)
                    logger.info("save_history_trade_vol, symbol={}, before time={}, \nresult={}".format(symbol, before_time, result))
                    if result:
                        log_config.output2ui(
                            "save_history_trade_vol, symbol={}, before time={}, \nresult={}".format(symbol, before_time,
                                                                                                    result))
                        trade_vol_list.append(result)
                        process.TRADE_VOL_HISTORY[symbol] = trade_vol_list
                    # logger.debug("TRADE_VOL_HISTORY={}".format(process.TRADE_VOL_HISTORY))
            except Exception as e:
                logger.exception("get_trade_vol_by_time, e={}".format(e))
            time.sleep(300)
    th = threading.Thread(target=save_history, args=(symbols,))
    th.setDaemon(True)
    th.start()
    return True


# before_time ---向前推多少秒
def get_trade_vol_by_time(symbol, beg=0, before_time=900, big_limit=10, retry=1):
    hrs = HuobiREST(config.CURRENT_REST_MARKET_URL, config.CURRENT_REST_TRADE_URL, config.ACCESS_KEY, config.SECRET_KEY, config.PRIVATE_KEY)
    should_get_size = int((before_time+beg)*1.5)
    logger.info("get_trade_vol_by_time should_get_size={}".format(should_get_size))
    if should_get_size > 2000:
        should_get_size = 1999

    current_time = int(time.time())
    start_time = (current_time-before_time - beg-3)*1000
    end_time = (current_time-beg)*1000
    is_ok = False
    response = None
    while retry > 0:
        response = hrs.get_history_trade(symbol, size=should_get_size)
        retry -= 1
        if response[0] != 200 or not response[1] or response[1].get("status", "") != config.STATUS_OK:
            time.sleep(5)
            continue

        is_ok = True
        break

    if not is_ok:
        logger.error("get_trade_vol_by_time return None, response={}".format(response))
        return None

    result = {"trade_vol": 0, "buy_vol": 0, "sell_vol": 0, "big_buy": 0, "big_sell": 0, "total_buy_cost": 0,
              "total_sell_cost": 0, "avg_buy_cost": 0, "avg_sell_cost": 0, "start_time": 0, "end_time": 0}
    try:
        list_time = []
        data = response[1].get("data", [])
        for d in data:
            ld = d.get("data", [])
            for sd in ld:
                # 小于起始时间或大于结束时间的不要
                ts = sd.get("ts", 0)
                if ts < start_time or ts > end_time:
                    continue

                list_time.append(ts)
                amount = sd.get("amount", 0)
                price = sd.get("price", 0)
                direction = sd.get("direction")
                result["{}_vol".format(direction)] += amount
                result["trade_vol"] += amount
                if amount >= big_limit:
                    result["big_"+direction] += 1

                if "buy" in direction:
                    result["total_buy_cost"] += amount * price
                elif "sell" in direction:
                    result["total_sell_cost"] += amount * price
                else:
                    logger.error("get_trade_vol error={}".format(sd))

        if result["buy_vol"]>0:
            result["avg_buy_cost"] = result["total_buy_cost"]/result["buy_vol"]
        if result["sell_vol"]>0:
            result["avg_sell_cost"] = result["total_sell_cost"]/result["sell_vol"]
        list_time.sort()
        if len(list_time) > 0:
            result["start_time"] = list_time[0]
            result["end_time"] = list_time[-1]
    except Exception as e:
        logger.exception("get_trade_vol_by_time e={}, result={}".format(e, result))
        log_config.output2ui("get_trade_vol_by_time e={}, result={}".format(e, result), 4)
        return None

    return result


def get_trade_vol(symbol, beg=0, size=900, big_limit=10):
    hrs = HuobiREST(config.CURRENT_REST_MARKET_URL, config.CURRENT_REST_TRADE_URL, config.ACCESS_KEY, config.SECRET_KEY, config.PRIVATE_KEY)
    should_get_size = beg+size
    if should_get_size > 2000:
        return None

    response = hrs.get_history_trade(symbol, size=should_get_size)
    if response[0] != 200:
        return None

    if response[1].get("status", "") != "ok":
        return None

    result = {"trade_vol": 0, "buy_vol": 0, "sell_vol": 0, "big_buy": 0, "big_sell": 0, "total_buy_cost": 0,
              "total_sell_cost": 0, "avg_buy_cost": 0, "avg_sell_cost": 0, "start_time": 0, "end_time": 0}
    try:
        list_time = []
        data = response[1].get("data", [])
        for d in data:
            ld = d.get("data", [])
            for sd in ld:
                beg -= 1        #前beg条不要
                if beg > 0:
                    continue

                list_time.append(sd.get("ts", 0))
                amount = sd.get("amount", 0)
                price = sd.get("price", 0)
                direction = sd.get("direction")
                result["{}_vol".format(direction)] += amount
                result["trade_vol"] += amount
                if amount >= big_limit:
                    result["big_"+direction] += 1

                if "buy" in direction:
                    result["total_buy_cost"] += amount * price
                elif "sell" in direction:
                    result["total_sell_cost"] += amount * price
                else:
                    logger.error("get_trade_vol error={}".format(sd))

        result["avg_buy_cost"] = result["total_buy_cost"]/result["buy_vol"]
        result["avg_sell_cost"] = result["total_sell_cost"]/result["sell_vol"]
        list_time.sort()
        result["start_time"] = list_time[0]
        result["end_time"] = list_time[-1]
    except Exception as e:
        logger.exception("get_trade_vol e={}".format(e))
        log_config.output2ui("get_trade_vol e={}".format(e), 4)

    return result


if __name__ == '__main__':
    hb = Huobi(debug=True)
    ret = hb.init()
    if not ret:
        print("---------init failed")
        exit(1)

    hb.init_history()
    hb.run(after=15)
    hb.exit()
