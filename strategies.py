#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/19
# Function:
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import talib
from strategy_pool import Strategy
import process
import config
from rs_util import HuobiREST
import log_config
import logging
import huobi
from popup_trade import PopupTrade

# result = {"trade_vol": 0, "buy_vol": 0, "sell_vol": 0, "big_buy": 0, "big_sell": 0, "total_buy_cost": 0,
#           "total_sell_cost": 0, "avg_buy_cost": 0, "avg_sell_cost": 0, "start_time": 0, "end_time": 0}
logger = logging.getLogger(__name__)

trade_detail = {"type": "buy-market",
                "order_id": "123",
                "amount": 1,
                "symbol": "ethusdt",
                "price": None,
                "time": 1234567890}
BUY_RECORD = []
SELL_RECORD = []
TRADE_RECORD = []

move_stop_profit_params = {"check": 1, "msf_min": 0.02, "msf_back": 0.25}
stop_loss_params = {"check": 1, "percent": 0.02}
kdj_buy_params = {"check": 1, "k": 20, "d": 22, "buy_percent": 0.4, "up_percent": 0.004, "peroid": "15min"}
kdj_sell_params = {"check": 1, "k": 82, "d": 78, "sell_percent": 0.4, "down_percent": 0.004, "peroid": "15min"}
vol_price_fly_params = {"check": 1, "vol_percent": 1.2, "high_than_last": 3, "price_up_limit": 0.03, "buy_percent": 0.5,
                        "peroid": "5min"}
boll_strategy_params = {"check": 1, "peroid": "15min", "open_diff1_percent": 0.012, "open_diff2_percent": 0.012,
                        "close_diff1_percent": 0.0025, "close_diff2_percent": 0.0025, "open_down_percent": -0.03,
                        "open_up_percent": 0.01, "open_buy_percent": 0.5, "trade_percent": 1.5, "close_up_percent": 0.03,
                        "close_buy_percent": 0.5}


def macd_strategy_5min():
    logger.info("macd_strategy_5min be called")
    dw = process.KLINE_DATA.get("market.btcusdt.kline.5min", None)
    if dw is None:
        print("macd_strategy_5min can't be run.")
        return False
    # macd = 12 天 EMA - 26 天 EMA,  ==== DIF
    # signal = 9 天 MACD的EMA   ===== DEA
    # hist = MACD - MACD signal  =====  hist
    # dw["close"] = np.array(close)

    # dif, dea, hist = talib.MACD(np.array(close), fastperiod=arg[0], slowperiod=arg[1], signalperiod=arg[2])
    dw["DIF"], dw["DEA"], dw["MACD"] = talib.MACD(dw.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
    print(dw["DIF"])
    print(dw["DEA"])
    print(dw["MACD"])

    dw.tail(10)

    dw[['DIF', 'DEA']].plot()
    # dw.loc[len(dw)-1]["DIF", "DEA", "MACD"]

    plt.show()
    plt.savefig("picture//macd_strategy_5min.png")


def macd_strategy_1min():
    print("macd_strategy be called")
    dw = process.KLINE_DATA.get("market.btcusdt.kline.1min", None)
    if dw is None:
        print("macd_strategy_1min can't be run.")
        return False
    # macd = 12 天 EMA - 26 天 EMA,  ==== DIF
    # signal = 9 天 MACD的EMA   ===== DEA
    # hist = MACD - MACD signal  =====  hist
    # dw["close"] = np.array(close)

    # dif, dea, hist = talib.MACD(np.array(close), fastperiod=arg[0], slowperiod=arg[1], signalperiod=arg[2])
    dw["DIF"], dw["DEA"], dw["MACD"] = talib.MACD(dw.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
    print(dw["DIF"])
    print(dw["DEA"])
    print(dw["MACD"])

    dw[['DIF', 'DEA']].plot()

    plt.show()
    plt.savefig("picture//macd_strategy_1min.png")


def macd_strategy_1day():
    print("macd_strategy be called")
    dw = process.KLINE_DATA.get("market.btcusdt.kline.1day", None)
    if dw is None:
        print("macd_strategy_1min can't be run.")
        return False
    # macd = 12 天 EMA - 26 天 EMA,  ==== DIF
    # signal = 9 天 MACD的EMA   ===== DEA
    # hist = MACD - MACD signal  =====  hist
    # dw["close"] = np.array(close)

    # dif, dea, hist = talib.MACD(np.array(close), fastperiod=arg[0], slowperiod=arg[1], signalperiod=arg[2])
    dw["DIF"], dw["DEA"], dw["MACD"] = talib.MACD(dw.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
    print(dw["DIF"])
    print(dw["DEA"])
    print(dw["MACD"])

    dw[['DIF', 'DEA']].plot()

    plt.show()
    plt.savefig("picture//macd_strategy_1day.png")


def is_kdj_5min_buy(market, times=3):
    df = process.KLINE_DATA.get(market, None)
    if df is None:
        logger.warning("is_kdj_5min_buy can't be run.dw is empty.")
        log_config.output2ui("is_kdj_5min_buy can't be run.dw is empty", 2)
        return False

    temp_df = df.head(len(df))
    df_len = len(temp_df)
    # k_df = temp_df.drop_duplicates('tick_id').reset_index(drop=True)
    k_df = temp_df
    k_df["slowk"], k_df["slowd"] = talib.STOCH(k_df.high.values, k_df.low.values, k_df.close.values,
                                               fastk_period=9,
                                               slowk_period=3,
                                               slowk_matype=0,
                                               slowd_period=3,
                                               slowd_matype=3)

    for i in range(1, times + 1):
        cur_d = k_df.loc[len(k_df) - i, "slowd"]
        cur_k = k_df.loc[len(k_df) - i, "slowk"]
        if cur_d > 20 or cur_k > 20:
            logger.info("is_kdj_5min_buy return False.")
            log_config.output2ui("is_kdj_5min_buy return False.")
            return False

    return True


def is_buy_big_than_sell(symbol, peroids=2):
    result = get_trade_vol_from_local(symbol, 0, peroids)
    if result:
        if result.get("buy_vol", 0) > result.get("sell_vol", 0):
            return True

    return False

# 判断历史几个周期内是否是开口或缩口
def is_history_open_close(market, history, open_percent, close_percent):
    while history>=0:
        upper, middle, lower = get_boll(market, history, False)
        diff1 = upper - middle
        diff2 = middle - lower
        pdiff1 = diff1/middle
        pdiff2 = diff2/middle

        if pdiff1 >= open_percent and pdiff2 >= open_percent:
            return "open"

        if pdiff1 <= close_percent and pdiff2 <= close_percent:
            return "close"
        history -= 1

    return "normal"


G_BOLL_BUY = 0
def boll_strategy():
    if boll_strategy_params.get("check", 1) != 1:
        log_config.output2ui("boll_strategy is not check", 2)
        return False

    peroid = boll_strategy_params.get("peroid", "15min")
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], peroid)
    symbol = config.NEED_TOBE_SUB_SYMBOL[0]
    upper, middle, lower = get_boll(market, 0)
    price = get_current_price(symbol)
    diff1 = upper - middle
    diff2 = middle - lower
    state = 0
    # 先初步判断是否开或缩，参数松
    open_diff1_percent = boll_strategy_params.get("open_diff1_percent", 0.012)
    open_diff2_percent = boll_strategy_params.get("open_diff2_percent", 0.012)
    pdiff1 = diff1/price
    pdiff2 = diff2/price
    if pdiff1 > open_diff1_percent * 0.8 and pdiff2 > open_diff2_percent*0.8:
        state = 1  # 张口
    close_diff1_percent = boll_strategy_params.get("close_diff1_percent", 0.0025)
    close_diff2_percent = boll_strategy_params.get("close_diff2_percent", 0.0025)
    if pdiff1 < close_diff1_percent*1.25 and pdiff2 < close_diff2_percent*1.25:
        state = -1  # 缩口

    buy_percent = 0
    # 判断是否开口超跌
    up_down = get_up_down(market)
    now = int(time.time()) * 1000
    history_open_close = None
    if state==1 or state==-1:
        # 历史开口幅度大于opp
        history_open_close = is_history_open_close(market, 3, open_diff1_percent, close_diff1_percent)

    if state == 1:
        if price < lower:
            # 跌幅超过open_down_percent（0.03）
            down_percent = boll_strategy_params.get("open_down_percent", -0.03)
            if up_down <= down_percent and up_down > -0.05:
                # 超跌在右侧
                open_up_percent = boll_strategy_params.get("open_up_percent", 0.01)
                # 最近一段时间上涨幅度超过open_up_percent（0.01）
                if price > get_min_price(symbol, now - 45 * 60 * 1000) * (1+open_up_percent):
                    # 历史开口幅度大于open_diff1_percent
                    if history_open_close == "open":
                        logger.info("开口超跌")
                        log_config.output2ui("开口超跌")
                        buy_percent = boll_strategy_params.get("open_buy_percent", 0.2)

    # 缩口状态
    elif state == -1:
        # 是否向上通道中
        if upper > price and price > middle:
            # 上下轨缩口幅度在一定范围
            if pdiff1 > close_diff1_percent and pdiff1 < 0.004:
                if pdiff2 > close_diff1_percent and pdiff2 < 0.004:
                    try:
                        t1_vol = get_trade_vol_from_local(symbol, 0, 3).get("trade_vol", 0)
                        t2_vol = get_trade_vol_from_local(symbol, 3, 6).get("trade_vol", 0)
                    except:
                        return False
                    trade_percent = boll_strategy_params.get("trade_percent", 1.5)
                    # 交易量0-3 大于 1.5 倍的 3-6
                    if t1_vol > trade_percent * t2_vol:
                        close_up_percent = boll_strategy_params.get("close_up_percent", 0.03)
                        # 当天上涨幅度不能超过3%
                        if up_down < close_up_percent:
                            # 历史开口幅度大于open_diff1_percent
                            if history_open_close == "close":
                                logger.info("缩口向上")
                                log_config.output2ui("缩口向上")
                                buy_percent = boll_strategy_params.get("close_buy_percent", 0.2)

    sell_percent = 0
    if price > upper:
        # sell_percent = 0.2
        logger.info("boll strategy price > upper, upper={}, price={}".format(upper, price))
        log_config.output2ui("boll strategy price > upper, upper={}, price={}".format(upper, price))

        if (upper - middle) / middle > open_diff1_percent:
            sell_percent += 0.5
            logger.info("超过上轨，且(upper-middle)/middle >open_diff1_percent")
            log_config.output2ui("超过上轨，且(upper-middle)/middle >open_diff1_percent")
        # if up_down > 0.05:
        #     logger.info("超过上轨，up_down > 0.05")
        #     log_config.output2ui("超过上轨，up_down > 0.05")
        #     sell_percent += 0.2
    # max_price = get_max_price(symbol, now - 10 * 60 * 1000)

    # if max_price > price and max_price > middle:
    #     if price <= middle:
    #         logger.info("下跌到中轨， max_price={}， middle={}, price={}".format(max_price, middle, price))
    #         log_config.output2ui("下跌到中轨， max_price={}， middle={}, price={}".format(max_price, middle, price))
    #         sell_percent = 0.2

    logger.info(
        "boll_strategy call buy percent: {},sell_percent={}, current price={}, upper={}, middle={}, lower={}, pdiff1={}, pdiff2={}".format(
            buy_percent, sell_percent, price, upper, middle, lower, pdiff1, pdiff2))
    log_config.output2ui(
        "boll_strategy call buy percent: {},sell_percent={}, current price={}, upper={}, middle={}, lower={}, pdiff1={}, pdiff2={}".format(
            buy_percent, sell_percent, price, upper, middle, lower, pdiff1, pdiff2))
    global G_BOLL_BUY
    if buy_percent > 0:
        # msg = "[BUY]boll_strategy buy {} percent: {}, current price={}, upper={}, middle={}, lower={}, pdiff1={}, pdiff2={}".format(symbol, buy_percent, price, upper, middle, lower, pdiff1, pdiff2)
        msg = "[买入{}]boll 买入比例={}%, 当前价格={}, 上轨={}, 中轨={}, 下轨={}, 上－中／价={}, 中－下／价={}".format(symbol, round(
            buy_percent * 100, 2), round(price, 3), round(upper, 2), round(middle, 2),
                                                                                                     round(lower, 2),
                                                                                                     round(pdiff1, 2),
                                                                                                     round(pdiff2, 2))
        if not trade_alarm(msg):
            return False

        ret = buy_market(symbol, percent=buy_percent, current_price=price)
        if ret[0]:
            msg = "[买入{}]boll 买入比例={}%, 买入金额={}$, 当前价格={}$, 上轨={}, 中轨={}, 下轨={}, 上－中／价={}, 中－下／价={}".format(symbol, round(
                buy_percent * 100, 2), round(ret[1], 3), round(price, 3), round(upper, 2), round(middle, 2), round(lower, 2),
                                                                                                 round(pdiff1, 2),
                                                                                                 round(pdiff2, 2))

            logger.info(msg)
            log_config.output2ui(msg, 7)
            log_config.send_mail(msg)

            # log_config.send_mail(
            #     "[BUY SUCCESS]buy {} percent: {}, current price: {}".format(symbol, buy_percent, price))

            G_BOLL_BUY += 1
            return True

    # if sell_percent > 0 and G_BOLL_BUY > 0:
    if sell_percent > 0:
        msg = "[卖出{}]boll 卖出比例={}%, 当前价格={}, 上轨={}, 中轨={}, 下轨={}, 上－中／价={}, 中－下／价={}".format(symbol, round(sell_percent*100, 2), round(price,3), round(upper,2), round(middle,2), round(lower,2), round(pdiff1,2), round(pdiff2,2))
        if not trade_alarm(msg):
            return False

        ret = sell_market(symbol, percent=sell_percent, current_price=price)
        if ret[0]:
            msg = "[卖出{}]boll 卖出比例={}%, 卖出量={}个, 当前价格={}$, 上轨={}, 中轨={}, 下轨={}, 上－中／价={}, 中－下／价={}".format(symbol, round(
                sell_percent * 100, 2), round(ret[1], 3), round(price, 3), round(upper, 2), round(middle, 2), round(lower, 2),
                                                                                                 round(pdiff1, 2),
                                                                                                 round(pdiff2, 2))

            logger.info(msg)
            log_config.output2ui(msg, 7)
            log_config.send_mail(msg)
            # log_config.send_mail("[SELL SUCCESS]sell {} percent: {}, current price: {}".format(symbol, sell_percent, price))
            G_BOLL_BUY -= 1
            return True

    return False


def kdj_strategy_buy(currency=[], max_trade=1):
    if kdj_buy_params.get("check", 1) != 1:
        log_config.output2ui("kdj_buy is not check", 2)
        return False

    peroid = kdj_buy_params.get("peroid", "15min")
    logger.info("kdj_buy_{} be called".format(peroid))
    log_config.output2ui("kdj_buy_{} be called".format(peroid))
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], peroid)
    symbol = market.split(".")[1]
    cur_k, cur_d, cur_j = get_kdj(market)
    current_price = get_current_price(symbol)
    logger.info("current k={}, d={}, current_price={}".format(cur_k, cur_d, current_price))
    log_config.output2ui("current k={}, d={}, current_price={}".format(cur_k, cur_d, current_price))

    # kd不能大于40
    if cur_k >25 or cur_d>25:
        logger.info("cur_k or cur_d > 25")
        return False

    #回暖幅度超过0.008
    now = int(time.time()) * 1000
    min_price = get_min_price(symbol, last_time=now - (15 * 60 * 1000))
    if not min_price or min_price <= 0:
        return False

    up_percent = kdj_buy_params.get("up_percent", 0.008)
    actual_up_percent = round((current_price - min_price) / min_price, 4)
    logger.info("kdj buy min_price={}, current_price={},  need up_percent={} actual up_percent = {}".format(min_price,
                                                                                                            current_price,
                                                                                                            up_percent,
                                                                                                            actual_up_percent))
    if actual_up_percent < up_percent:
        logger.info("kdj buy actual_up_percent{} less than need up_percent{}.".format(actual_up_percent, up_percent))
        return False

    logger.info("kdj buy actual_up_percent{} big than need up_percent{}.".format(actual_up_percent, up_percent))
    # 最近三个周期内出现过kd小于20
    last_k, last_d, last_j = get_kdj(market, 1)
    last_k_2, last_d_2, last_j_2 = get_kdj(market, 2)
    need_k = kdj_buy_params.get("k", 20)
    need_d = kdj_buy_params.get("d", 22)
    if (cur_k <= need_k and cur_d <= need_d) \
            or (last_k <= need_k and last_d <= need_d) \
            or (last_k_2 <= need_k and last_d_2 <= need_d):

    # if cur_k < kdj_buy_params.get("k", 20) and cur_d < kdj_buy_params.get("d", 22):
        # 连续3个五分钟要满足kd小于20
        # ret = is_kdj_5min_buy(market="market.{}.kline.5min".format(config.NEED_TOBE_SUB_SYMBOL[0]), times=2)
        # if not ret:
        #     logger.info("is_kdj_5min_buy return False")
        #     log_config.output2ui("is_kdj_5min_buy return False")
        #     return False

        # logger.info("is_kdj_5min_buy return True")
        # log_config.output2ui("is_kdj_5min_buy return True")
        percent = kdj_buy_params.get("buy_percent", 0.4)
        #
        # now = int(time.time()) * 1000
        # min_price = get_min_price(symbol, now - 15 * 60 * 1000)
        # up_percent = kdj_buy_params.get("up_percent", 0.008)
        # actual_up_percent = round((current_price-min_price)/min_price, 4)
        # logger.info("kdj buy min_price={}, current_price={},  need up_percent={} actual up_percent = {}".format(min_price, current_price, up_percent, actual_up_percent))
        # if actual_up_percent < up_percent:
        #     return False
        #
        # logger.info("kdj buy actual_up_percent big than need up_percent")

        ret = is_buy_big_than_sell(symbol, 2)
        if ret:
            logger.info("is_buy_big_than_sell return True")
            log_config.output2ui("is_buy_big_than_sell return True")
            percent += 0.1

        msg_show = "[买入{}]kdj_{} 买入比例={}%, 当前价格={}, 阶段最低价格={}, 指标K={}, D={}, 回暖幅度={}%".format(
            symbol, peroid, round(percent * 100, 2), round(current_price, 3), round(min_price, 3),
            round(cur_k, 2), round(cur_d, 2), round(actual_up_percent * 100, 2))

        if not trade_alarm(msg_show):
            return False

        ret = buy_market(symbol, percent=percent, current_price=current_price)
        if ret[0]:
            msg_show = "[买入{}]kdj_{} 买入比例={}%, 买入金额数={}$, 当前价格={}, 阶段最低价格={}, 指标K={}, D={}, 回暖幅度={}%".format(
                symbol, peroid, round(percent * 100, 2), round(ret[1], 3), round(current_price, 3), round(min_price, 3),
                round(cur_k, 2), round(cur_d, 2), round(actual_up_percent * 100, 2))
            logger.info(msg_show)
            log_config.output2ui(msg_show, 6)
            log_config.send_mail(msg_show)
            # log_config.send_mail("[BUY SUCCESS]buy {} percent: {}, current price: {}".format(symbol, percent, current_price))
        logger.info("-----BUY_RECORD = {}".format(BUY_RECORD))
        return True
    return False


def kdj_strategy_sell(currency=[], max_trade=1):
    if kdj_sell_params.get("check", 1) != 1:
        log_config.output2ui("kdj_sell is not check", 2)
        return False

    peroid = kdj_sell_params.get("peroid", "15min")
    logger.info("kdj_sell_{} be called".format(peroid))
    log_config.output2ui("kdj_sell_{} be called".format(peroid))
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], peroid)
    symbol = market.split(".")[1]
    cur_k, cur_d, cur_j = get_kdj(market)
    current_price = get_current_price(symbol)
    logger.info("current k={}, d={}, current_price={}".format(cur_k, cur_d, current_price))
    log_config.output2ui("current k={}, d={}, current_price={}".format(cur_k, cur_d, current_price))

    #kd要大于50
    if cur_k<70 or cur_d<70:
        logger.info("cur_k or cur_d < 80")
        return False

    #回撤超过0.008
    now = int(time.time()) * 1000
    max_price = get_max_price(symbol, last_time=now - (15 * 60 * 1000))
    if not max_price or max_price<= 0:
        return False

    down_percent = kdj_sell_params.get("down_percent", 0.008)
    actual_down_percent = round((max_price - current_price) / max_price, 4)
    logger.info(
        "kdj sell max_price={}, current_price={}, need down_percent={}, actual_down_percent={}".format(max_price,
                                                                                                       current_price,
                                                                                                       down_percent,
                                                                                                       actual_down_percent))
    if actual_down_percent < down_percent:
        return False

    # 最近三个周期内出现过kd大于80
    last_k, last_d, last_j = get_kdj(market, 1)
    last_k_2, last_d_2, last_j_2 = get_kdj(market, 2)
    need_k = kdj_sell_params.get("k", 85)
    need_d = kdj_sell_params.get("d", 80)
    if (cur_k >= need_d and cur_d >= need_d) \
            or (last_k >= need_k and last_d >= need_d) \
            or (last_k_2 >= need_k and last_d_2 >= need_d):
        percent = kdj_sell_params.get("sell_percent", 0.4)

        msg_show = "[卖出{}]kdj_{} 卖出比例={}%, 当前价格={}, 阶段最高价格={}, 回撤幅度={}%, 指标K={}, D={}．".format(
            symbol, peroid, round(percent * 100, 2), round(current_price, 3), round(max_price, 3),
            round(actual_down_percent * 100, 2), round(cur_k, 2), round(cur_d, 2), )
        if not trade_alarm(msg_show):
            return False

        logger.info("kdj sell actual_down_percent={} is big than need down percent".format(actual_down_percent))
        ret = sell_market(symbol, percent=percent, current_price=current_price)
        if ret[0]:
            msg_show = "[卖出{}]kdj_{} 卖出比例={}%, 卖出数量={}个, 当前价格={}, 阶段最高价格={}, 回撤幅度={}%, 指标K={}, D={}．".format(
                symbol, peroid, round(percent * 100, 2), round(ret[1], 3), round(current_price, 3), round(max_price, 3),
                round(actual_down_percent * 100, 2), round(cur_k, 2), round(cur_d, 2), )

            logger.info(msg_show)
            log_config.output2ui(msg_show, 7)
            log_config.send_mail(msg_show)
            # log_config.send_mail("[SELL SUCCESS]sell {} percent: {}, current price: {}".format(symbol, percent, current_price))
        return True

    return False


def get_last_trade_info(market, type=0):
    last_buy_amount = 0
    last_price = 0
    last_time = 0
    for pos in range(len(TRADE_RECORD) - 1, -1, -1):
        # if trade.get("is_stop_loss", False):
        trade = TRADE_RECORD[pos]
        if type == 0:
            if "buy-limit" in trade["type"]:
                last_buy_amount = trade.get("amount", 0)
                last_price = float(trade.get("price", "0.0"))
                # trade["is_stop_loss"] = True
                last_time = trade.get('created-at', 0)
                break

            if "buy-market" == trade["type"]:
                last_buy_amount = float(trade.get("amount", "0.0"))
                if last_buy_amount > 0:
                    last_price = float(trade.get('field-cash-amount', "0.0")) / last_buy_amount
                # trade["is_stop_loss"] = True
                last_time = trade.get('created-at', 0)
                break
        else:
            if "sell-limit" in trade["type"]:
                last_buy_amount = trade.get("amount", 0)
                last_price = float(trade.get("price", "0.0"))
                # trade["is_stop_loss"] = True
                last_time = trade.get('created-at', 0)
                break

            if "sell-market" == trade["type"]:
                last_buy_amount = float(trade.get("amount", "0.0"))
                if last_buy_amount > 0:
                    last_price = float(trade.get('field-cash-amount', "0.0")) / last_buy_amount
                # trade["is_stop_loss"] = True
                last_time = trade.get('created-at', 0)
                break
    logger.info(
        "last buy info: last_buy_amount={}, last price={}, last_time={}".format(last_buy_amount, last_price, last_time))
    log_config.output2ui(
        "last buy info: last_buy_amount={}, last price={}, last_time={}".format(last_buy_amount, last_price, last_time))
    return last_buy_amount, last_price, last_time


def stop_loss(percent=0.03):
    logger.info("stop loss checking ------stop_loss_params={}".format(stop_loss_params))
    log_config.output2ui("stop loss checking ------stop_loss_params={}".format(stop_loss_params))

    if stop_loss_params.get("check", 1) != 1:
        log_config.output2ui("stop loss is not check", 2)
        return False

    precision = 0.0000001
    trigger = False
    for trade in BUY_RECORD:
        last_buy_amount = float(trade.get("field-amount", "0.0"))
        last_price = float(trade.get("price", "0.0"))
        if last_price < precision and last_buy_amount > 0:
            last_price = float(trade.get('field-cash-amount', "0.0")) / last_buy_amount
        last_time = trade.get('created-at', 0)

        if last_buy_amount <= precision or last_price <= precision:
            continue

        symbol = trade.get("symbol")
        current_price = get_current_price(symbol)

        loss_percent = (last_price - current_price) / last_price
        if loss_percent >= stop_loss_params["percent"]:
            msg = "[SELL] stop loss execute, sell {}, loss percent={}, config loss percent={}, last_buy_price={}, last_buy_amount={}, current_price={}".format(
                    symbol, loss_percent, stop_loss_params["percent"], last_price, last_buy_amount, current_price)
            if not trade_alarm(msg):
                return False

            logger.info(
                "stop loss execute, loss percent={}, config loss percent={}, last_buy_price={}, last_buy_amount={}, current_price={}".format(
                    loss_percent, stop_loss_params["percent"], last_price, last_buy_amount, current_price))
            log_config.output2ui(
                "stop loss execute, loss percent={}, config loss percent={}, last_buy_price={}, last_buy_amount={}, current_price={}".format(
                    loss_percent, stop_loss_params["percent"], last_price, last_buy_amount, current_price))

            ret = sell_market(symbol, last_buy_amount, current_price=current_price)
            if ret[0]:
                BUY_RECORD.remove(trade)
                trigger = True
                logger.info(
                    "stop_loss sell {} amount={}, last buy price={}, current price={}, loss_percent={}".format(
                        symbol, last_buy_amount, last_price,
                        current_price, loss_percent))

                msg_show = "[卖出{}] 移动止损 卖出量={}个, 买入价={}, 当前价={}, 损失比例={}%".format(
                        symbol, round(last_buy_amount, 3), round(last_price, 3),
                        round(current_price,3), round(loss_percent*100, 2))

                log_config.output2ui(msg_show, 7)
                log_config.send_mail(msg_show)
                # log_config.send_mail("[SELL SUCCESS]sell {} current price: {}".format(symbol, current_price))
    return trigger


def move_stop_profit():
    # market = "market.ethusdt.kline.15min"
    precision = 0.0000001
    logger.info("move_stop_profit checking params={}".format(move_stop_profit_params))
    log_config.output2ui("move_stop_profit checking params={}".format(move_stop_profit_params))
    if move_stop_profit_params.get("check", 1) != 1:
        log_config.output2ui("move_stop_profit is not check", 2)
        return False

    trigger = False
    for trade in BUY_RECORD:
        logger.info("move_stop_profit last buy trade = {}".format(trade))
        log_config.output2ui("move_stop_profit last buy trade = {}".format(trade))
        last_buy_amount = float(trade.get("field-amount", "0.0"))
        last_price = float(trade.get("price", "0.0"))
        if last_price < precision and last_buy_amount > 0:
            last_price = float(trade.get('field-cash-amount', "0.0")) / last_buy_amount
        last_time = trade.get('created-at', 0)

        if last_buy_amount <= precision or last_price <= precision:
            continue

        symbol = trade.get("symbol", "")
        current_price = get_current_price(symbol)
        max_price = get_max_price(symbol, last_time)
        if max_price <= 0:
            continue
        # if max_price < last_price * 1.02:
        # 上涨超过两个点
        max_upper = (max_price-last_price)/last_price
        logger.info("move_stop_profit, profit upper={}, msf_min={}".format(max_upper, move_stop_profit_params.get("msf_min", 0.02)))

        if trade.get("strategy_type", "") == "vol_price_fly":
            if max_upper < 0.5 * move_stop_profit_params.get("msf_min", 0.02):
                continue
        else:
            if max_upper < move_stop_profit_params.get("msf_min", 0.02):
                continue

        # 当前回撤幅度
        down_back_percent = round((max_price - current_price) / (max_price - last_price), 3)

        # 当前盈利
        profit = round(((current_price-last_price)/last_price)*100, 3)

        logger.info(
            "move_stop_profit last_price={}, max_price={}, current_price={}, max_upper={}, down_back_percent={}, last_buy_amount={}, msf_back={}".format(
                last_price, max_price, current_price, max_upper, down_back_percent, last_buy_amount,
                move_stop_profit_params["msf_back"]))

        # 回撤幅度超过25％（涨幅在2个点以内的）, 如果超过两个点，则要求回撤幅度需要缩小，以保证更多的盈利
        if down_back_percent < move_stop_profit_params.get("msf_back", 0.25) * (0.02/max_upper):
            continue

        # 盈利小于１个点不卖
        if profit < 0.01:
            continue

        msg = "[SELL]Move stop profit be trigger sell {},  current price={}, last_price={}, max_price={} max_upper={}, profit={}% down_back_percent={}%".format(
                    symbol, current_price, last_price, max_price, max_upper, profit, down_back_percent)
        if not trade_alarm(msg):
            return False

        bal = get_balance(symbol[0:3], result_type=0)
        if bal and float(bal) <= last_buy_amount:
            last_buy_amount = round(float(bal)*0.95, 3)

        logger.warning(
            "move_stop_profit last_price={}, max_price={}, current_price={}, down_back_percent={}, last_buy_amount={}, profit={}%".format(
                last_price, max_price, current_price, down_back_percent, last_buy_amount, profit))

        ret = sell_market(symbol, last_buy_amount, current_price=current_price)
        if ret[0]:
            trigger = True
            msg_show = "[卖出{}]移动止盈： 上次买入价={}, 最高价={}, 回撤幅度={}%, 当前卖出价={}, 当前卖出量={}个, 盈利比={}%, 盈利金额={}$ ".format(symbol,
                                                                                                               round(
                                                                                                                   last_price,
                                                                                                                   3),
                                                                                                               round(
                                                                                                                   max_price,
                                                                                                                   3),
                                                                                                               round(
                                                                                                                   down_back_percent * 100,
                                                                                                                   2),
                                                                                                               round(
                                                                                                                   current_price,
                                                                                                                   3),
                                                                                                               round(
                                                                                                                   last_buy_amount,
                                                                                                                   3),
                                                                                                               round(
                                                                                                                   profit,
                                                                                                                   2),
                                                                                                               round(
                                                                                                                   last_buy_amount * (
                                                                                                                               current_price - last_price),
                                                                                                                   3))
            log_config.output2ui(msg_show, 7)
            log_config.send_mail(msg_show)
            BUY_RECORD.remove(trade)

    return trigger


def vol_price_fly():
    if vol_price_fly_params.get("check", 1) != 1:
        log_config.output2ui("vol price fily is not check", 2)
        return False

    peroid = vol_price_fly_params.get("peroid", 1)
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], peroid)
    symbol = market.split(".")[1]
    multiple = vol_price_fly_params.get("vol_percent", 1.5)
    peroid_5min = 1
    if peroid == "5min":
        peroid_5min = 1
    elif peroid == "15min":
        peroid_5min = 3
    # elif peroid == "30min":
    #     peroid_5min = 6
    # else:
    #     peroid_5min = 12
    last_peroid_0_3 = get_trade_vol_from_local(symbol, 0, 3 * peroid_5min)
    last_peroid_3_7 = get_trade_vol_from_local(symbol, 3 * peroid_5min, 7 * peroid_5min)
    # result = {"trade_vol": 0, "buy_vol": 0, "sell_vol": 0, "big_buy": 0, "big_sell": 0, "total_buy_cost": 0,
    #           "total_sell_cost": 0, "avg_buy_cost": 0, "avg_sell_cost": 0, "start_time": 0, "end_time": 0}

    logger.info("vol_price_fly last_peroid_0_3={}, last_peroid_3_7={}".format(last_peroid_0_3, last_peroid_3_7))
    log_config.output2ui(
        "vol_price_fly last_peroid_0_3={}, last_peroid_3_7={}".format(last_peroid_0_3, last_peroid_3_7))

    if not last_peroid_0_3 or not last_peroid_3_7:
        return False

    # 最近三个周期的量要大于最近7个周期(3-10)的量
    time_0_3 = (last_peroid_0_3.get("end_time", 0) - last_peroid_0_3.get("start_time", 0)) / (
                1000 * 60 * 5 * peroid_5min)
    time_3_7 = (last_peroid_3_7.get("end_time", 0) - last_peroid_3_7.get("start_time", 0)) / (
                1000 * 60 * 5 * peroid_5min)
    time_0_3 = 3 if time_0_3 == 0 else time_0_3
    time_3_7 = 7 if time_3_7 == 0 else time_3_7
    avg_0_3_vol = last_peroid_0_3.get("trade_vol", 0) / time_0_3
    avg_3_7_vol = last_peroid_3_7.get("trade_vol", 0) / time_3_7
    logger.info("vol_price_fly avg_0_3_vol={}, avg_3_7_vol={}, multiple={}".format(avg_0_3_vol, avg_3_7_vol, multiple))
    log_config.output2ui(
        "vol_price_fly avg_0_3_vol={}, avg_3_7_vol={}, multiple={}".format(avg_0_3_vol, avg_3_7_vol, multiple))
    if not avg_0_3_vol >= avg_3_7_vol * multiple:
        logger.info("vol_price_fly avg_0_3_vol={} not bigger than avg_3_7_vol={}*{} ".format(avg_0_3_vol, avg_3_7_vol,
                                                                                             multiple))
        log_config.output2ui(
            "vol_price_fly avg_0_3_vol={} not bigger than avg_3_7_vol={}*{} ".format(avg_0_3_vol, avg_3_7_vol,
                                                                                     multiple))
        return False

    # 最近三个周期的平均买量要大于上7个周期的平均卖盘
    # avg_0_3_buy_vol = last_peroid_0_3.get("buy_vol", 0)
    # avg_0_3_sell_vol = last_peroid_0_3.get("sell_vol", 0)
    # logger.info("vol_price_fly avg_0_3_buy_vol={}, avg_0_3_sell_vol={}, vol_buy_sell={}".format(avg_0_3_buy_vol,
    #                                                                                             avg_0_3_sell_vol,
    #                                                                                             vol_price_fly_params[
    #                                                                                                 "vol_buy_sell"]))
    # log_config.output2ui(
    #     "vol_price_fly avg_0_3_buy_vol={}, avg_0_3_sell_vol={}, vol_buy_sell={}".format(avg_0_3_buy_vol,
    #                                                                                     avg_0_3_sell_vol,
    #                                                                                     vol_price_fly_params[
    #                                                                                         "vol_buy_sell"]))
    # if not avg_0_3_buy_vol > avg_0_3_sell_vol * vol_price_fly_params["vol_buy_sell"]:
    #     return False

    # k, d, j = get_kdj(market)
    # logger.info("vol_price_fly k={}, d={}".format(k, d))
    # log_config.output2ui("vol_price_fly k={}, d={}".format(k, d))
    # if k > 80 and d > 80:
    #     return False

    # (5分钟）当前周期的交易量是上一个周期的3倍以上， 且当前周期的交易量要大于1.1倍的最近21个周期平均交易量
    last_peroid_0 = get_trade_vol_from_local(symbol, 0, 1).get("trade_vol", 0)
    last_peroid_1 = get_trade_vol_from_local(symbol, 1, 1).get("trade_vol", 0)
    last_peroid_2 = get_trade_vol_from_local(symbol, 2, 1).get("trade_vol", 0)
    high_than_last = vol_price_fly_params.get("high_than_last", 3)
    local_21 = get_trade_vol_from_local(symbol, 3, 7 * 1).get("trade_vol", 0)
    if not all([last_peroid_0, last_peroid_1, last_peroid_2, local_21]):
        return False

    if last_peroid_0 < last_peroid_1*high_than_last and last_peroid_1<high_than_last*last_peroid_2:
        logger.info("current vol not bigger than 3*last vol. current trade vol={}, last vol={}".format(last_peroid_0, last_peroid_1))
        return False

    last_peroid_21 = local_21 / 7
    if last_peroid_0 < 1.1*last_peroid_21:
        logger.info("current vol not bigger than 1.1*last vollast_peroid_21. current trade vol={}, last_peroid_21={}".format(last_peroid_0, last_peroid_21))
        return False


    # 当前价格不能超过前面第三个周期的收盘价*（1+规定涨幅）
    current_price = get_current_price(symbol)
    close_before_2 = (get_close(market, before=3) + get_close(market, before=4) + get_close(market, before=5))/3
    # close_before1 = get_close(market, before=1)
    logger.info("vol_price_fly current_price={} , close_before_2={}, * 1+price_up_limit= {}".format(current_price,
                                                                                                    close_before_2,
                                                                                                    vol_price_fly_params[
                                                                                                        "price_up_limit"]))
    log_config.output2ui(
        "vol_price_fly current_price={}, close_before_2={} * 1+price_up_limit{}".format(current_price, close_before_2,
                                                                                        vol_price_fly_params[
                                                                                            "price_up_limit"]))

    if (current_price > close_before_2 * (1 + vol_price_fly_params.get("price_up_limit", 0.02))) or (current_price < close_before_2 * (1 + 0.01)):
        logger.info("vol_price_fly current_price={} > close_before_2={} * {}".format(current_price, close_before_2,
                                                                                     1 + vol_price_fly_params.get(
                                                                                         "price_up_limit", 0.02)))
        log_config.output2ui(
            "vol_price_fly current_price={} > close_before_2={} * {}".format(current_price, close_before_2,
                                                                             1 + vol_price_fly_params.get(
                                                                                 "price_up_limit", 0.02)))
        return False

    # if close_before1 < close_before_2:
    #     logger.info("close_before1={} < close_before_2={} ".format(close_before1, close_before_2))
    #     log_config.output2ui("close_before1={} < close_before_2={} ".format(close_before1, close_before_2))
    #     return False

    percent = vol_price_fly_params["buy_percent"]
    msg = "[BUY]vol_price_fly buy {} percent={}, current price={}".format(symbol, percent, current_price)
    if not trade_alarm(msg):
        return False

    ret = buy_market(symbol, percent=percent, strategy_type="vol_price_fly", current_price=current_price)
    if ret[0]:
        logger.info("[BUY SUCCESS]vol_price_fly buy {} percent={}, amount={}, current price={}".format(symbol, percent, ret[1], current_price))
        msg_show = "[买入{}]量价齐升 买入比例={}%, 买入金额数={}$, 当前价格={}".format(symbol, round(percent*100, 2), round(ret[1],2), round(current_price, 3))
        log_config.output2ui(msg_show, 6)
        log_config.send_mail(msg_show)

    return ret


def trade_alarm(message, show_time=0):
    if not config.ALARM_NOTIFY:
        return True

    logger.warning("Trade Alarm: {}".format(message))
    if show_time>0:
        pop = PopupTrade(message, show_time)
    else:
        pop = PopupTrade(message, config.ALARM_TIME)

    config.ROOT.wait_window(pop)

    # 如果用户未处理，走默认值
    if not pop.is_ok and not pop.is_cancel:
        return config.ALARM_TRADE_DEFAULT
    else:
        if pop.is_ok:
            return True
        else:
            return False


def buy_market(symbol, amount=0, percent=0.2, record=True, strategy_type="", current_price=0):
    # 按余额比例买
    currency = symbol[3:]
    balance = get_balance(currency)
    if amount <= 0:
        if percent > 0:
            if balance and balance > 0:
                amount = round(balance * percent, 2)
            else:
                return False, amount
        else:
            return False, 0
    else:
        # 余额不足
        if amount > balance:
            amount = balance*0.95

    # 市价amount代表买多少钱的
    if amount < config.TRADE_MIN_LIMIT_VALUE:
        # 如果余钱够的话，按最小交易额买
        if balance > config.TRADE_MIN_LIMIT_VALUE:
            amount = config.TRADE_MIN_LIMIT_VALUE
        else:
            logger.info(
                "buy {} amount {}, current price={}, balance={} total value less than {}$. trade cancel!".format(
                    symbol, amount, current_price, balance, config.TRADE_MIN_LIMIT_VALUE))
            return False, amount

    # 超限时按最大钱或当前所有余钱数买
    if amount > config.TRADE_MAX_LIMIT_VALUE:
        if balance >= config.TRADE_MAX_LIMIT_VALUE:
            amount = config.TRADE_MAX_LIMIT_VALUE
        else:
            amount = balance

    amount = round(amount, 2)
    logger.warning(
        "buy {} amount {}$, current price={}, balance={}$, min trade={} max trade={}".format(
            symbol, amount, current_price, balance, config.TRADE_MIN_LIMIT_VALUE, config.TRADE_MAX_LIMIT_VALUE))

    hrs = HuobiREST(config.CURRENT_REST_MARKET_URL, config.CURRENT_REST_TRADE_URL, config.ACCESS_KEY, config.SECRET_KEY, config.PRIVATE_KEY)
    ret = hrs.send_order(amount=amount, source="api", symbol=symbol, _type="buy-market")
    # (True, '6766866273')
    if ret[0] == 200 and ret[1]:
        logger.info("buy market success, symbol={}, amount={}, record={}".format(symbol, amount, record))
        log_config.output2ui("buy market success, symbol={}, amount={}, record={}".format(symbol, amount, record))
        if record:
            order_id = ret[1]
            order_response = hrs.order_info(order_id)
            # (200, {'status': 'ok',
            #        'data': {'id': 6766866273, 'symbol': 'ethusdt', 'account-id': 4091798, 'amount': '1.000000000000000000',
            #                 'price': '0.0', 'created-at': 1530233353821, 'type': 'buy-market',
            #                 'field-amount': '0.002364960741651688', 'field-cash-amount': '0.999999999999999753',
            #                 'field-fees': '0.000004729921483303', 'finished-at': 1530233354117, 'source': 'api',
            #                 'state': 'filled', 'canceled-at': 0}})
            if order_response[0] == 200:
                if order_response[1].get("status", "") == config.STATUS_OK:
                    order_detail = order_response[1].get("data", {})
                    order_detail["strategy_type"] = strategy_type
                    BUY_RECORD.append(order_detail)
        update_balance()
        return True, amount
    logger.error("buy market failed, symbol={}, amount={}, record={}".format(symbol, amount, record))
    log_config.output2ui("buy market error, symbol={}, amount={}, record={}".format(symbol, amount, record), 3)
    return False, amount


def sell_market(symbol, amount=0, percent=0.1, record=True, current_price=0):
    currency = symbol[0:3]
    balance = get_balance(currency)

    if amount <= 0:
        if percent > 0:
            if balance and balance > 0:
                amount = round(balance * percent, 4)
            else:
                return False, amount
        else:
            return False, 0
    else:
        # 余币不足
        if amount > balance:
            amount = balance*0.95

    # 市价卖时表示卖多少币
    if current_price:
        total_value = amount*current_price
        if total_value < config.TRADE_MIN_LIMIT_VALUE:
            # 如果余币够的话，按最小交易额卖
            if balance*current_price > config.TRADE_MIN_LIMIT_VALUE:
                amount = config.TRADE_MIN_LIMIT_VALUE/current_price
            else:
                logger.info("sell {} amount {}, current price={}, balance={},total value={} less than {}$. trade cancel!".format(symbol, amount, current_price, balance, amount*current_price, config.TRADE_MIN_LIMIT_VALUE))
                return False, amount
        elif total_value > config.TRADE_MAX_LIMIT_VALUE:
            amount = round(config.TRADE_MAX_LIMIT_VALUE/current_price, 4)
            if amount > balance:
                amount = balance*0.95

    amount = round(amount, 4)
    logger.warning(
        "sell {} amount {}(个), current price={}, balance={}(个),total value={}$, min trade={}$, max trade={}$. trade cancel!".format(symbol,
                                                                                                             amount,
                                                                                                             current_price,
                                                                                                             balance,
                                                                                                             total_value,
                                                                                                             config.TRADE_MIN_LIMIT_VALUE, config.TRADE_MAX_LIMIT_VALUE))
    hrs = HuobiREST(config.CURRENT_REST_MARKET_URL, config.CURRENT_REST_TRADE_URL, config.ACCESS_KEY, config.SECRET_KEY, config.PRIVATE_KEY)
    ret = hrs.send_order(amount=amount, source="api", symbol=symbol, _type="sell-market")
    # (True, '6766866273')
    if ret[0] == 200 and ret[1]:
        logger.info("sell market success, symbol={}, amount={}, record={}".format(symbol, amount, record))
        log_config.output2ui("sell market success, symbol={}, amount={}, record={}".format(symbol, amount, record))
        if record:
            order_id = ret[1]
            order_response = hrs.order_info(order_id)
            # order_info = (200, {'status': 'ok', 'data': {'id': 6767239276, 'symbol': 'ethusdt', 'account-id': 4091798,
            #                                              'amount': '0.001000000000000000', 'price': '0.0',
            #                                              'created-at': 1530233815111, 'type': 'sell-market',
            #                                              'field-amount': '0.001000000000000000',
            #                                              'field-cash-amount': '0.422820000000000000',
            #                                              'field-fees': '0.000845640000000000',
            #                                              'finished-at': 1530233815527, 'source': 'api',
            #                                              'state': 'filled', 'canceled-at': 0}})
            if order_response[0] == 200:
                if order_response[1].get("status", "") == config.STATUS_OK:
                    order_detail = order_response[1].get("data", {})
                    SELL_RECORD.append(order_detail)
        update_balance()
        return True, amount

    logger.error("sell market failed, symbol={}, amount={}, record={}, ret={}".format(symbol, amount, record, ret))
    log_config.output2ui("sell market error, symbol={}, amount={}, record={}, ret={}".format(symbol, amount, record, ret), 3)
    return False, amount


# pos--0 代表实时价，1--代表上一次收盘价
def get_close(market, before=1):
    df = process.KLINE_DATA.get(market, None)
    if df is None:
        logger.error("get_close -1, market={}, before={}".format(market, before))
        return -1

    try:
        # print(len(df))
        close = df.loc[len(df) - 1 - before, "close"]
    except Exception as e:
        logger.exception("get_close")
        print(len(df))
        close = df.loc[len(df) - 1 - before - 1, "close"]
    return close


def get_open(market, before=1):
    df = process.KLINE_DATA.get(market, None)
    if df is None:
        logger.error("get_open -1, market={}, before={}".format(market, before))
        return -1

    try:
        print(len(df))
        open_price = df.loc[len(df) - 1 - before, "open"]
    except Exception as e:
        logger.exception("get_open")
        print(len(df))
        open_price = df.loc[len(df) - 1 - before - 1, "open"]
    return open_price

#获取涨跌幅
def get_up_down(market, before=1):
    df = process.KLINE_DATA.get(market, None)
    if df is None:
        logger.error("get_up_down -1, market={}, before={}".format(market, before))
        return -1

    try:
        # print(len(df))
        open_price = df.loc[len(df) - before, "open"]
        close_price = df.loc[len(df) - before, "close"]
        up_dwon = round((close_price - open_price) / open_price, 4)
    except Exception as e:
        logger.exception("get_open")
        # print(len(df))
        open_price = df.loc[len(df) - 1 - before, "open"]
        close_price = df.loc[len(df) - 1 - before, "close"]
        up_dwon = round((close_price - open_price) / open_price, 4)
    logger.info("get_up_down = {}".format(up_dwon))
    return up_dwon


def get_current_price(symbol):
    df = process.KLINE_DATA.get(symbol, None)
    if df is None:
        return -1

    # return df.loc[len(df) - 1, "close"]
    try:
        # print(len(df))
        price = df.loc[len(df) - 1, "close"]
    except Exception as e:
        logger.exception("get_close e={}".format(e))
        print(len(df))
        price = df.loc[len(df) - 1 - 1, "close"]

    logger.info("get_current_price sysmbol={}, price={}".format(symbol, price))
    return price


def get_max_price(symbol, last_time, current=0):
    df = process.KLINE_DATA.get(symbol, None)
    if df is None:
        return -1

    if current>0:
        # 默认取五分钟之前往前的最大价格
        # current = ((int(time.time()) * 1000) - 5*60*1000) if current <= 0 else current
        try:
            tmp_df = df.loc[df["ts"] >= last_time]
            max_price = tmp_df.loc[tmp_df["ts"]<current].high.max()
            if pd.isna(max_price):
                max_price = tmp_df.loc[tmp_df["ts"] < current].close.max()
        except Exception as e:
            logger.exception("get_max_price catch e={}, last_time={}, current={}".format(e, last_time, current))
            temp_df = df[["ts", "high"]][df.ts >= last_time]
            temp_df = temp_df.loc[temp_df["ts"]<current]
            max_price = temp_df.high.max()
    else:
        try:
            max_price = df.loc[df["ts"] >= last_time].high.max()
            if pd.isna(max_price):
                max_price = df.loc[df["ts"] >= last_time].close.max()
        except Exception as e:
            logger.exception("get_max_price catch e={}, last_time={}, current={}".format(e, last_time, current))
            temp_df = df[["ts", "high"]][df.ts >= last_time]
            temp_df = temp_df.loc[temp_df["ts"] < current]
            max_price = temp_df.high.max()

    logger.info("get_max_price, symbol={}, last time={}, current={}, max_price={}".format(symbol, last_time, current, max_price))
    if not max_price or pd.isna(max_price):
        return -1
    else:
        return max_price


def get_min_price(symbol, last_time, current=0):
    # 默认取五分钟之前往前的最低价格
    # current = ((int(time.time()) * 1000)-5*60*1000) if current <= 0 else current

    df = process.KLINE_DATA.get(symbol, None)
    if df is None:
        return -1

    if current>0:
        try:
            temp_df = df.loc[df["ts"] >= last_time]
            min_price = temp_df.loc[temp_df["ts"]<current].low.min()
            if pd.isna(min_price):
                min_price = temp_df.loc[temp_df["ts"]<current].close.min()
        except Exception as e:
            logger.exception("get_min_price catch e={}, last_time={}, current={}".format(e, last_time, current))
            temp_df = df[["ts", "low"]][df.ts >= last_time][df.ts < current]
            min_price = temp_df.low.min()

    else:
        try:
            min_price = df.loc[df["ts"] >= last_time].low.min()
            if pd.isna(min_price):
                min_price = df.loc[df["ts"] >= last_time].close.min()
        except Exception as e:
            logger.exception("get_min_price catch e={}, last_time={}, current={}".format(e, last_time, current))
            temp_df = df[["ts", "low"]][df.ts >= last_time]
            min_price = temp_df.low.min()

    logger.info("get_min_price, symbol={}, last time={}, current={}, min_price={}".format(symbol, last_time, current, min_price))

    if not min_price or pd.isna(min_price):
        return -1
    else:
        return min_price


def get_boll(market, pos=0, update2ui=True):
    upper, middle, lower = -1, -1, -1
    df = process.KLINE_DATA.get(market, None)
    if df is None:
        return upper, middle, lower

    temp_df = df.head(len(df) - pos)
    temp_df["upper"], temp_df["middle"], temp_df["lower"] = talib.BBANDS(temp_df.close.values, timeperiod=15, nbdevup=2, nbdevdn=2, matype=0)
    # a,b,c=talib.BBANDS(temp_df.close.values, timeperiod=15, nbdevup=2, nbdevdn=2, matype=talib.MA_Type.T3)
    # d,e,f=talib.BBANDS(temp_df.close.values, timeperiod=15, nbdevup=2, nbdevdn=2, matype=0)
    # g, h, k = talib.BBANDS(temp_df.close.values, timeperiod=15, nbdevup=2, nbdevdn=2, matype=0)
    # temp_df = df.head(len(df) - 1)
    # u, m, l = talib.BBANDS(temp_df.close.values, timeperiod=15, nbdevup=2, nbdevdn=2, matype=0)
    upper = temp_df.loc[len(temp_df) - 1, "upper"]
    middle = temp_df.loc[len(temp_df) - 1, "middle"]
    lower = temp_df.loc[len(temp_df) - 1, "lower"]
    if update2ui:
        process.REALTIME_UML.put((upper, middle, lower))
    return upper, middle, lower
    # plt.plot(upper)
    # plt.plot(middle)
    # plt.plot(lower)
    # plt.grid()
    # plt.show()
    # diff1 = upper - middle
    # diff2 = middle - lower
    # print
    # diff1
    # print
    # diff2


# pos=0代表将当前价格纳入计算，pos越大代表数据离目前越远
def get_kdj(market, pos=0, fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=3):
    k, d, j = -1, -1, -1
    df = process.KLINE_DATA.get(market, None)
    if df is None:
        return k, d, j

    temp_df = df.head(len(df) - pos)
    temp_df["k"], temp_df["d"] = talib.STOCH(temp_df.high.values,
                                             temp_df.low.values,
                                             temp_df.close.values,
                                             fastk_period=fastk_period,
                                             slowk_period=slowk_period,
                                             slowk_matype=slowk_matype,
                                             slowd_period=slowd_period,
                                             slowd_matype=slowd_matype)

    k = temp_df.loc[len(temp_df) - 1, "k"]
    d = temp_df.loc[len(temp_df) - 1, "d"]
    temp_df["j"] = temp_df.k * 3 - temp_df.d * 2
    j = temp_df.loc[len(temp_df) - 1, "j"]

    # temp_df[['k', 'd']].plot(figsize=(9, 6), title=flag)
    # plt.legend(loc='upper left')
    # plt.show()
    # plt.savefig("picture//{}.png".format(flag))
    # process.REALTIME_KDJ.put((k, d, j))
    return k, d, j


def kdj_5min_update():
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], "5min")
    k,d,j = get_kdj(market)
    process.REALTIME_KDJ_5MIN.put((k, d, j))
    return k, d, j

def kdj_15min_update():
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], "15min")
    k,d,j = get_kdj(market)
    process.REALTIME_KDJ_15MIN.put((k, d, j))
    return k, d, j


def kdj_30min_update():
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], "30min")
    k,d,j = get_kdj(market)
    process.REALTIME_KDJ_30MIN.put((k, d, j))
    return k, d, j

def kdj_1day_update():
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], "1day")
    k,d,j = get_kdj(market)
    process.REALTIME_KDJ_1DAY.put((k, d, j))
    return k, d, j



# 本地存储的是以5分钟为周期的，beg=0代表从后往前推
def get_trade_vol_from_local(symbol, beg=0, size=3):
    trade_vol_history = process.TRADE_VOL_HISTORY.get(symbol, [])
    trades_size = len(trade_vol_history)
    logger.info(
        "get_trade_vol_from_local symbol={}, beg={}, size={}, trades_size={}".format(symbol, beg, size, trades_size))
    if beg + size > trades_size:
        return None

    # result = {"trade_vol": 0, "buy_vol": 0, "sell_vol": 0, "big_buy": 0, "big_sell": 0, "total_buy_cost": 0,
    #           "total_sell_cost": 0, "avg_buy_cost": 0, "avg_sell_cost": 0, "start_time": 0, "end_time": 0}
    result = {}
    for data in trade_vol_history[trades_size - (beg + size):trades_size - beg]:
        for k in data.keys():
            result[k] = result.get(k, 0) + data[k]

    if result["sell_vol"]<=0 or result["buy_vol"]<=0:
        return None
    result["avg_sell_cost"] = result["total_sell_cost"] / result["sell_vol"]
    result["avg_buy_cost"] = result["total_buy_cost"] / result["buy_vol"]
    result["start_time"] = trade_vol_history[trades_size - (beg + size)].get("start_time", 0)
    result["end_time"] = trade_vol_history[trades_size - beg - 1].get("end_time", 0)
    logger.info(
        "get_trade_vol_from_local symbol={}, beg={}, size={}, trades_size={}, result={}".format(symbol, beg, size,
                                                                                                trades_size, result))
    return result


def update_balance(is_first=False):
    try:
        for symbol in config.NEED_TOBE_SUB_SYMBOL:
            s0 = symbol[0:3]
            s1 = symbol[3:]
            bal0 = get_balance(s0, result_type=2)
            str_balance = ""
            if bal0:
                str_balance += "{}:{}/{}".format(s0.upper(), round(bal0.get("trade", 0), 3),
                                                 round(bal0.get("frozen", 0), 3))
            bal1 = get_balance(s1, result_type=2)
            if bal1:
                str_balance += ", {}:{}/{}".format(s1.upper(), round(bal1.get("trade", 0), 3),
                                                   round(bal1.get("frozen", 0), 3))
            logger.info("update_balance = {}".format(str_balance))
            process.REALTIME_BALANCE.put(str_balance)
            log_config.output2ui("update balance--{}".format(str_balance), 8)

    except Exception as e:
        logger.exception("update_balance e= {}".format(e))


# result_type=0--trade, 1--frozen, 2--all
def get_balance(currency, access_key=None, secret_key=None, retry=2, result_type=0):
    if access_key and secret_key:
        hrs = HuobiREST(config.CURRENT_REST_MARKET_URL, config.CURRENT_REST_TRADE_URL, access_key, secret_key, config.PRIVATE_KEY)
    else:
        hrs = HuobiREST(config.CURRENT_REST_MARKET_URL, config.CURRENT_REST_TRADE_URL, config.ACCESS_KEY,
                        config.SECRET_KEY, config.PRIVATE_KEY)
    while retry > 0:
        balance = hrs.get_balance(currency=currency)
        if balance[0] == 200 and balance[1]:
            balance_data = balance[1]
            logger.info("balance = {}".format(balance_data))
            log_config.output2ui("balance = {}".format(balance_data))
            if result_type == 0:
                return balance_data.get("trade", -1)
            elif result_type == 1:
                return balance_data.get("frozen", -1)
            else:
                return balance_data
        else:
            retry -= 1
    return None
    # def __init__(self, func, check_period, execute_times=-1, after_execute_sleep=0,
    #              state=1, is_after_execute_pause=False, name=""):

def buy_low():
    now = int(time.time()) * 1000
    symbol = config.NEED_TOBE_SUB_SYMBOL[0]
    market = "market.{}.kline.{}".format(symbol, "15min")

    min_price_5 = get_min_price(symbol, now - (15 * 60 * 1000)*5, current=now - (10 * 60 * 1000))
    min_price_20 = get_min_price(symbol, now - (15 * 60 * 1000) * 20, now - (10 * 60 * 1000))
    min_price_60 = get_min_price(symbol, now - (15 * 60 * 1000) * 60, now - (10 * 60 * 1000))

    if min_price_5<=0 or min_price_20<=0 or min_price_60<=0:
        return False

    current_price = get_current_price(symbol)
    if current_price<=0:
        return False

    logger.info("buy low called. current price={}, min_price_5={}, min_price_20={}, min_price_60={}".format(current_price, min_price_5, min_price_20, min_price_60))
    buy_percent = 0
    # 比最低价还低1％以上，且最近三个周期都在跌
    if current_price*1.01 < min_price_5 and get_open(market, 1) > get_close(market, 1) \
            and get_open(market, 2) > get_close(market, 2) and get_open(market, 3) > get_close(market, 3):
        buy_percent += 0.1

    if current_price*1.01 < min_price_20:
        buy_percent += 0.2

    if current_price*1.01 < min_price_60:
        buy_percent += 0.3

    if buy_percent > 0:
        msg = "[买入{}]抄底 买入比例={}%, 当前价格={}, 最近5/20/60周期内最低价={}/{}/{}.".format(
            symbol, round(buy_percent*100, 2), round(current_price, 3), round(min_price_5, 3), round(min_price_20, 3), round(min_price_60, 3))

        if not trade_alarm(msg):
            return False

        ret = buy_market(symbol, percent=buy_percent, current_price=current_price)
        if ret[0]:
            msg = "[买入{}]抄底 买入比例={}%, 买入金额={}$, 当前价格={}, 最近5/20/60周期内最低价={}/{}/{}.".format(
                symbol, round(buy_percent * 100, 2), round(ret[1], 2), round(current_price, 3), round(min_price_5, 3),
                round(min_price_20, 3), round(min_price_60, 3))

            logger.info(msg)
            log_config.output2ui(msg, 6)
            log_config.send_mail(msg)
            # log_config.send_mail(
            #     "[BUY SUCCESS]buy {} percent: {}, current price: {}".format(symbol, buy_percent, current_price))
        logger.info("-----BUY_RECORD = {}".format(BUY_RECORD))
        return True
    else:
        return False


def sell_high():
    now = int(time.time()) * 1000
    symbol = config.NEED_TOBE_SUB_SYMBOL[0]
    market = "market.{}.kline.{}".format(symbol, "15min")

    max_price_5 = get_max_price(symbol, now - (15 * 60 * 1000) * 5, now - (10 * 60 * 1000))
    max_price_20 = get_max_price(symbol, now - (15 * 60 * 1000) * 20, now - (10 * 60 * 1000))
    max_price_60 = get_max_price(symbol, now - (15 * 60 * 1000) * 60, now - (10 * 60 * 1000))

    if max_price_5<=0 or max_price_20<=0 or max_price_60<=0:
        return False

    current_price = get_current_price(symbol)
    logger.info("sell high called. current price={}, max_price_5={}, max_price_20={}, max_price_60={}".format(current_price, max_price_5, max_price_20, max_price_60))
    sell_percent = 0
    # 比最高价还高1％，且最近三个周期都在涨
    if current_price >= max_price_5*1.01 and get_open(market, 1) < get_close(market, 1) and get_open(market, 2) < get_close(
            market, 2) and get_open(market, 3) < get_close(market, 3):
        sell_percent += 0.2

    if current_price >= 1.01 * max_price_20:
        sell_percent += 0.2

    if current_price >= max_price_60 * 1.01:
        sell_percent += 0.3

    if sell_percent > 0:
        msg = "[卖出{}]高抛 卖出比例={}%,　当前价格={}, 最近5/20/60周期内最高价={}/{}/{}.".format(
            symbol, round(sell_percent * 100, 2), round(current_price, 3), round(max_price_5, 3),
            round(max_price_20, 3), round(max_price_60, 3))

        # msg = "[BUY]sell_high sell {} percent: {}, current price={}, max_price_5={}, max_price_20={}, max_price_60={}".format(
        #     symbol, sell_percent, current_price, max_price_5, max_price_20, max_price_60)
        if not trade_alarm(msg):
            return False

        ret = sell_market(symbol, percent=sell_percent, current_price=current_price)
        if ret[0]:
            msg = "[卖出{}]高抛 卖出比例={}%, 卖出量={}个, 当前价格={}, 最近5/20/60周期内最高价={}/{}/{}.".format(
                symbol, round(sell_percent * 100, 2), round(ret[1], 2), round(current_price, 3), round(max_price_5, 3),
                round(max_price_20, 3), round(max_price_60, 3))

            logger.info(msg)
            log_config.output2ui(msg, 7)
            log_config.send_mail(msg)
            # log_config.send_mail(
            #     "[SELL SUCCESS]sell {} percent: {}, current price: {}".format(symbol, sell_percent, current_price))
        logger.info("-----SELL_RECORD = {}".format(SELL_RECORD))
        return True
    else:
        return False



STRATEGY_LIST = [
    # Strategy(macd_strategy_5min, 15, 1, "macd_strategy_5min"),
    # Strategy(macd_strategy_1min, 10, 1, "macd_strategy_1min"),
    # Strategy(macd_strategy_1day, 20, 1, "macd_strategy_1day"),
    # Strategy(kdj_strategy_buy, 240, -1, after_execute_sleep=900 * 3, name="kdj_strategy_buy"),
    # Strategy(kdj_strategy_sell, 240, -1, after_execute_sleep=900 * 3, name="kdj_strategy_sell"),
    Strategy(kdj_strategy_buy, 30, -1, after_execute_sleep=900 * 3, name="kdj_strategy_buy"),
    Strategy(kdj_strategy_sell, 45, -1, after_execute_sleep=900 * 3, name="kdj_strategy_sell"),
    Strategy(stop_loss, 35, -1, after_execute_sleep=120, name="stop_loss"),
    Strategy(move_stop_profit, 30, -1, after_execute_sleep=120, name="move_stop_profit"),
    Strategy(vol_price_fly, 35, -1, name="vol_price_fly", after_execute_sleep=900 * 2),
    Strategy(boll_strategy, 30, -1, name="boll strategy", after_execute_sleep=900 * 2),
    # Strategy(kdj_5min_update, 30, -1, name="kdj_5min_update", after_execute_sleep=1),
    Strategy(kdj_15min_update, 40, -1, name="kdj_15min_update", after_execute_sleep=1),
    Strategy(buy_low, 25, -1, name="buy_low", after_execute_sleep=900*2),
    Strategy(sell_high, 30, -1, name="sell_high", after_execute_sleep=900*2),


]


def test_get_trade_info():
    ret = huobi.get_trade_vol("ethusdt")
    print(ret)
    ret = huobi.get_trade_vol_by_time("ethusdt", beg=300, before_time=900)
    print(ret)
    exit(1)
    huobi.save_history_trade_vol(["ethusdt", "btcusdt"])
    time.sleep(60)
    logger.info("1111111")
    print(get_trade_vol_from_local("ethusdt", 0, 1))
    print(get_trade_vol_from_local("btcusdt", 0, 1))
    time.sleep(200)
    logger.info("222222")
    print(get_trade_vol_from_local("ethusdt", 0, 2))
    print(get_trade_vol_from_local("btcusdt", 0, 2))
    print(get_trade_vol_from_local("ethusdt", 1, 1))
    print(get_trade_vol_from_local("btcusdt", 1, 1))
    time.sleep(200)
    logger.info("3333333")
    print(get_trade_vol_from_local("ethusdt", 0, 3))
    print(get_trade_vol_from_local("btcusdt", 0, 3))
    print(get_trade_vol_from_local("ethusdt", 2, 1))
    print(get_trade_vol_from_local("btcusdt", 2, 1))


if __name__ == "__main__":
    import log_config

    log_config.init_log_config()
    test_get_trade_info()
