#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/19
# Function:
import time
# import matplotlib.pyplot as plt
# import numpy as np
from datetime import datetime
from requests import get
import pandas as pd
import talib
from threading import Thread
from strategy_pool import Strategy
import process
import config
from rs_util import HuobiREST
import log_config
import logging
import huobi
from popup_trade import PopupTrade
import random
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

move_stop_profit_params = {"check": 1, "msf_min": 0.018, "msf_back": 0.21}
stop_loss_params = {"check": 0, "percent": 0.03}
kdj_buy_params = {"check": 1, "k": 30, "d": 28, "buy_percent": 0.25, "up_percent": 0.002, "period": "15min"}
kdj_sell_params = {"check": 1, "k": 82, "d": 80, "sell_percent": 0.3, "down_percent": 0.005, "period": "15min"}
vol_price_fly_params = {"check": 1, "vol_percent": 1.2, "high_than_last": 2, "price_up_limit": 0.01, "buy_percent": 0.3,
                        "period": "5min"}
boll_strategy_params = {"check": 1, "period": "15min", "open_diff1_percent": 0.025, "open_diff2_percent": 0.025,
                        "close_diff1_percent": 0.0025, "close_diff2_percent": 0.0025, "open_down_percent": -0.02,
                        "open_up_percent": 0.003, "open_buy_percent": 0.35, "trade_percent": 1.5, "close_up_percent": 0.03,
                        "close_buy_percent": 0.5}

should_update_ui_tree = True
# BUY_LOW_RECORD = {}
# SELL_HIGH_RECORD = {}

last_notify_smart_patch = {

}


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

    # plt.show()
    # plt.savefig("picture//macd_strategy_5min.png")


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

    # plt.show()
    # plt.savefig("picture//macd_strategy_1min.png")


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

    # plt.show()
    # plt.savefig("picture//macd_strategy_1day.png")


def is_kdj_5min_buy(market, times=3):
    df = process.KLINE_DATA.get(market, None)
    if df is None:
        logger.warning("is_kdj_5min_buy can't be run.dw is empty.")
        log_config.output2ui("is_kdj_5min_buy can't be run.dw is empty", 7)
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
            log_config.output2ui("is_kdj_5min_buy return False.", 7)
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
        log_config.output2ui("boll_strategy is not check", 7)
        return False

    period = boll_strategy_params.get("period", "15min")
    symbol = config.NEED_TOBE_SUB_SYMBOL[0]

    # if is_still_up(symbol):
    #     logger.info(u"boll_strategy　still up")
    #     return False
    #
    # if is_still_down(symbol):
    #     logger.info(u"boll_strategy　still down")
    #     return False

    market = "market.{}.kline.{}".format(symbol, period)
    upper, middle, lower = get_boll(market, 0)
    price = get_current_price(symbol)
    diff1 = upper - middle
    diff2 = middle - lower
    state = 0
    # 先初步判断是否开或缩，参数松
    open_diff1_percent = boll_strategy_params.get("open_diff1_percent", 0.025)
    open_diff2_percent = boll_strategy_params.get("open_diff2_percent", 0.025)
    open_diff1_percent *= config.RISK
    open_diff2_percent *= config.RISK

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
    # up_down = get_up_down(market)

    open_now = get_open(market, 0)
    up_down = (price-open_now)/open_now #当前这个周期的涨跌幅

    now = int(time.time()) * 1000
    history_open_close = None
    if state == 1 or state == -1:
        # 历史开口幅度大于opp
        history_open_close = is_history_open_close(market, 3, open_diff1_percent, close_diff1_percent)

    if state == 1:
        if price < lower:
            # 跌幅超过open_down_percent（0.03）
            down_percent = boll_strategy_params.get("open_down_percent", -0.02)
            if up_down <= down_percent and up_down > -0.05:
                # 超跌在右侧
                open_up_percent = boll_strategy_params.get("open_up_percent", 0.01)
                # 最近一段时间上涨幅度超过open_up_percent（0.01）
                if price > get_min_price(symbol, now - 5 * 60 * 1000) * (1+open_up_percent):
                    # 历史开口幅度大于open_diff1_percent
                    if history_open_close == "open":
                        logger.info("开口超跌")
                        log_config.output2ui("开口超跌", 7)
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
                                log_config.output2ui("缩口向上", 7)
                                buy_percent = boll_strategy_params.get("close_buy_percent", 0.2)

    sell_percent = 0
    if price/upper > 1.12:
        sell_percent = 0.15
        logger.info("boll strategy price > upper, upper={}, price={}, middle={}".format(upper, price, middle))
        # log_config.output2ui("boll strategy price > upper, upper={}, price={}, middle={}".format(upper, price, middle))

        diff1 = (upper - middle) / middle
        if diff1 > open_diff1_percent:
            sell_percent += 0.1 * (diff1/open_diff1_percent)
            logger.info(u"超过上轨，且(upper-middle)/middle={} > open_diff1_percent={}".format(diff1, open_diff1_percent))
            # log_config.output2ui("超过上轨，且(upper-middle)/middle >open_diff1_percent")
        if up_down > 0.015:
            logger.info(u"超过上轨，up_down={} > 0.015".format(up_down))
            # log_config.output2ui("超过上轨，up_down > 0.05")
            sell_percent += 0.1*(up_down/0.015)

        if open_now > upper:
            logger.info("boll sell, open now={}>uppper={}".format(open_now, upper))
            sell_percent *= 1.5


    # max_price = get_max_price(symbol, now - 10 * 60 * 1000)

    # if max_price > price and max_price > middle:
    #     if price <= middle:
    #         logger.info("下跌到中轨， max_price={}， middle={}, price={}".format(max_price, middle, price))
    #         log_config.output2ui("下跌到中轨， max_price={}， middle={}, price={}".format(max_price, middle, price))
    #         sell_percent = 0.2

    logger.info(
        "boll_strategy call buy percent: {},sell_percent={}, current price={}, upper={}, middle={}, lower={}, pdiff1={}, pdiff2={}".format(
            buy_percent, sell_percent, price, upper, middle, lower, pdiff1, pdiff2))

    global G_BOLL_BUY
    if buy_percent > 0:
        buy_percent *= config.RISK
        now = int(time.time()) * 1000
        min_price = get_min_price(symbol, last_time=now - (15 * 60 * 1000))
        if is_still_down2(price, min_price):
            logger.info("boll buy, still down, 0.8")
            # buy_percent *= 0.8
            return False
        else:
            logger.info("boll buy, not still down, 1.2")
            # buy_percent *= 1.2

        # msg = "[BUY]boll_strategy buy {} percent: {}, current price={}, upper={}, middle={}, lower={}, pdiff1={}, pdiff2={}".format(symbol, buy_percent, price, upper, middle, lower, pdiff1, pdiff2)
        msg = "[买入{}]BLL 买入比例={}%, 买入价格={}, 上轨={}, 中轨={}, 下轨={}, 上－中／价={}, 中－下／价={}".format(symbol, round(
            buy_percent * 100, 2), round(price, 6), round(upper, 6), round(middle, 6),
                                                                                                     round(lower, 6),
                                                                                                     round(pdiff1, 6),
                                                                                                     round(pdiff2, 6))
        if not trade_alarm(msg):
            return False

        ret = buy_market(symbol, percent=buy_percent, current_price=price)
        if ret[0]:
            msg = "[买入{}]BLL 计划买入比例={}%, 实际买入金额={}$, 买入价格={}$, UL={}, ML={}, LL={}.".format(symbol, round(
                buy_percent * 100, 2), round(ret[1], 3), round(price, 6), round(upper, 6), round(middle, 6), round(lower, 6))

            success = False
            if ret[0] == 1:
                msg += "-交易成功！"
                success = True
                G_BOLL_BUY += 1
            elif ret[0] == 2:
                msg += "-交易被取消, 取消原因: {}!".format(ret[2])
            elif ret[0] == 3:
                msg += "-交易失败, 失败原因: {}！".format(ret[2])

            log_config.output2ui(msg, 6)
            logger.warning(msg)
            log_config.notify_user(msg, own=True)
            log_config.notify_user(log_config.make_msg(0, symbol, current_price=price, percent=buy_percent))

            return True

    # if sell_percent > 0 and G_BOLL_BUY > 0:
    if sell_percent > 0:
        sell_percent *= config.RISK
        now = int(time.time()) * 1000
        max_price = get_max_price(symbol, last_time=now - (15 * 60 * 1000))
        if is_still_up2(price, max_price):
            logger.info("boll sell, still up, 0.8")
            # sell_percent *= 0.8
            return False
        else:
            logger.info("boll sell, not still up, 1.2")
            # sell_percent *= 1.2

        msg = "[卖出{}]BLL 卖出比例={}%, 卖出价格={}, UL={}, ML={}, LL={}".format(symbol, round(sell_percent*100, 2), round(price,3), round(upper,2), round(middle,2), round(lower,2))
        if not trade_alarm(msg):
            return False

        ret = sell_market(symbol, percent=sell_percent, current_price=price)
        if ret[0]:
            msg = "[卖出{}]BLL 计划卖出比例={}%, 实际卖出量={}个, 卖出价格={}$, UL={}, ML={}, LL={}.".format(symbol, round(
                sell_percent * 100, 2), round(ret[1], 3), round(price, 6), round(upper, 6), round(middle, 6), round(lower, 6),
                                                                                                 round(pdiff1, 6),
                                                                                                 round(pdiff2, 6))

            success = False
            if ret[0] == 1:
                msg += "-交易成功！"
                G_BOLL_BUY -= 1
                success = True
            elif ret[0] == 2:
                msg += "-交易被取消, 取消原因: {}!".format(ret[2])
            elif ret[0] == 3:
                msg += "-交易失败, 失败原因: {}！".format(ret[2])

            log_config.output2ui(msg, 7)
            logger.warning(msg)
            log_config.notify_user(msg, own=True)
            log_config.notify_user(log_config.make_msg(1, symbol, current_price=price, percent=sell_percent))
            return True

    return False


def trade_advise_update():
    def boll_status(market):
        u5, m5, l5 = get_boll_avrg(market, -5, -1)
        boll5 = (u5 + m5 + l5) / 3
        u10, m10, l10 = get_boll_avrg(market, -10, -6)
        boll10 = (u10 + m10 + l10) / 2
        if boll5<0 or boll10<0:
            return 100

        status = 0
        if boll5 >= boll10 * 1.03:
            status = 2
        elif boll5 > boll10:
            status = 1
        elif boll5 * 1.03 > boll10:
            status = -1
        else:
            status = -2
        return status

    def trade_advise_update_process():
        logger.info("trade_advise_update_process start")
        day_market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], "1day")
        hour_market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], "60min")

        day_open = get_open(day_market, 0)
        day_upper, day_middle, day_lower = get_boll(day_market)

        hour_open = get_open(hour_market, 0)
        hour_upper, hour_middle, hour_lower = get_boll(hour_market)
        status_day = boll_status(day_market)
        status_hour = boll_status(hour_market)
        msg_dict = {-2: u"整体行情走低, 建议以观望为主, 持仓宜低, 波段操作需谨慎．", -1: u"整体行情低迷, 建议仓位4成以下, 以高抛低吸波段操作为宜．",
               0: u"整体行情稳定, 震幅较小, 建议减少交易次数, 持续观望, 注意成交量变化．",
               1: u"整体行情逐渐回暖, 建议以持有, 观望为主, 可逐步逢低建仓.", 2: u"整体行情处于上升通道中, 谨慎追高, 注意行情变化, 以持有和逢高出货为主．"}

        msg_day = msg_dict.get(status_day, u"行情变幻, 需谨慎操作！")
        if day_open > day_upper:
            msg_day = u"涨幅过大, 切忌追高, 建议逢高卖出！"
        if day_open < day_lower:
            msg_day = u"跌幅过大, 反弹可期, 可适当逢低吸货, 波段操作, 留意行情变化, 仓位不宜过重！"

        msg_hour = msg_dict.get(status_hour, u"行情变幻, 需谨慎操作！")
        if hour_open > hour_upper:
            msg_hour = u"涨幅过大, 谨慎追高, 以逢高卖出为主！"
        if hour_open < hour_lower:
            msg_hour = u"跌幅过大, 反弹可期, 可适当逢低吸货, 波段操作, 留意行情变化, 仓位不宜过重！"

        advise_day = u"大盘近几日" + msg_day
        advise_hour = u"大盘近几小时" + msg_hour

        process.REALTIME_ADVISE = (advise_day, advise_hour)

        notify_msg = ""
        try:
            host = "47.75.10.215"
            ret = get("http://{}:5000/notify/{}".format(host, config.ACCESS_KEY), timeout=3)
            if ret.status_code == 200:
                notify_msg = ret.text
        except Exception as e:
            logger.exception("get notify exception={}".format(e))

        logger.info(u"建议do={}, du={}, dm={}, dl={}\nho={}, hu={}, hm={}, hl={}\n advise_day={} \nadvise_hour={}\nnotify_msg={}".format(day_open, day_upper, day_middle, day_lower, hour_open, hour_upper, hour_middle, hour_lower, advise_day, advise_hour, notify_msg))

        process.REALTIME_SYSTEM_NOTIFY = notify_msg
        return advise_day, advise_hour, notify_msg

    th = Thread(target=trade_advise_update_process)
    th.setDaemon(True)
    th.start()
    return False


def global_limit_profit(mode=""):
    """
    全局配置的止盈比例
    :return:
    """
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("limit_profit", 0.25)


def global_back_profit(mode=""):
    """
    全局配置的回撤比例
    :return:
    """
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("back_profit", 0.05)


def global_risk(mode=""):
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("risk", 1.04)


def global_track(mode=""):
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("track", 1)


def global_gird(mode=""):
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("grid", 1)


def global_patch_interval(mode=""):
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("patch_interval", 0.05)

def global_smart_patch(mode=""):
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("smart_patch", 1)

def global_smart_profit(mode=""):
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("smart_profit", 1)

def global_patch_ref(mode=""):
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("patch_ref", 0)


def global_smart_first(mode=""):
    mode = config.TRADE_MODE if not mode else mode
    return config.TRADE_MODE_CONFIG.get(mode, {}).get("smart_first", 1)


def patch_multiple(index, mode="multiple", patch_limits=7):
    # 根据当前的补仓模式和补仓序数(第几次补仓)计算出本次的补仓倍数, 这个倍数是相对于首单的哦
    patch = 1
    # 最多买入10次, 即最多补仓9次
    if index > patch_limits:
        patch = 0
    elif index <= 0:
        patch = 1
    else:
        if mode == "multiple":
            patch = (2*index)/1
        elif mode == "flat":
            patch = 1/1
        elif mode == "fibonacci":
            fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
            patch = fib[index]/1
        elif mode == "lucas":
            lucas = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199]
            patch = lucas[index]/1
        elif mode == 'square':
            square = [2, 4, 16, 256]#平方队列最多补3次
            if index > 3:
                patch = 0
            else:
                patch = square[index]/2
        else:
            patch = (2 * index) / 1

    return patch


last_notify_smart_profit = {}


def should_stop_profit(symbol, buy_price, limit_profit, back_profit, monitor_start, track=1, smart_profit=1):
    limit_price = buy_price*(1+limit_profit)
    current_price = get_current_price(symbol)
    if not track:
        # 如果不追踪，价格超过规定的利润就卖
        if current_price >= limit_price:
            return True
            # 如果还在涨，再等会
            # if smart_profit and is_still_up2(symbol, 0.0020):
            #     return False
            # else:
            #     return True
        else:
            return False
    else:
        limit_delta = buy_price*back_profit
        max_price = get_max_price(symbol, monitor_start)
        if max_price >= limit_price:
            # 至少保证有一个点的盈利，否则不卖
            if current_price <= max_price-limit_delta and current_price>=(buy_price*1.005):
                return True
                # if smart_profit and is_still_up2(symbol, 0.0020):
                #     logger.warning("should_stop_profit but still up!!")
                #     log_config.output2ui(u"[{}]已达到预设的追踪止盈条件, 系统智能分析当前币价仍在上升, 系统将自动延迟卖出, 以扩大盈利额!".format(symbol.upper()), 2)
                #     return False
                # else:
                #     return True

    return False


def should_patch(symbol, ref_price, patch_interval, smart_patch=1):
    current_price = get_current_price(symbol=symbol)

    # 如果当前价格小于整体均价的一定比例，则补单
    if current_price < ref_price * (1 - patch_interval):
        # 如果还在跌，暂时不补仓
        if smart_patch and is_still_down2(symbol, 0.0015, 30):
            notify = False
            global last_notify_smart_patch
            if symbol in last_notify_smart_patch.keys():
                if (datetime.now()-last_notify_smart_patch[symbol]).total_seconds() > 180:
                    last_notify_smart_patch[symbol] = datetime.now()
                    notify = True
                else:
                    notify = False
            else:
                last_notify_smart_patch[symbol] = datetime.now()
                notify = True

            if notify:
                log_config.output2ui(u"[{}]已达到预设的补仓间隔条件, 系统智能分析当前币价仍在下跌, 系统将自动延迟补仓, 以降低持仓成本和交易风险!".format(symbol.upper()), 2)
            return False    #　暂停一下
        else:
            return True

    return False


def format_float(num, pos=2):
    if pos <= 0:
        return int(num)

    num_split = str(num).split('.')
    if len(num_split) == 1:
        return num

    num = float(num_split[0] + '.' + num_split[1][0:pos])
    return num


def stg_smart_profit():
    make_deal = False
    for trade_group in config.TRADE_RECORDS_NOW:
        #已经结束，或者trades为空
        if trade_group["end_time"] or not trade_group["trades"]:
            logger.info("trade group is ended or empty.")
            continue

        if trade_group.get("last_sell_failed", None):
            # 对于刚刚失败过的订单，15分钟内不再尝试卖出
            if (datetime.now() - trade_group["last_sell_failed"]).total_seconds() < 600:
                continue

        # logger.info("trade group={}".format(trade_group))
        trades = trade_group.get("trades", [])

        # 如果没有单独设置，则使用全局的止盈参数
        group_mode_name = trade_group.get("mode", "")
        group_mode_name = config.TRADE_MODE if not group_mode_name else group_mode_name

        group_limit_profit = trade_group.get("limit_profit", -1)
        group_limit_profit = global_limit_profit(group_mode_name) if group_limit_profit < 0 else group_limit_profit

        group_back_profit = trade_group.get("back_profit", -1)
        group_back_profit = global_back_profit(group_mode_name) if group_back_profit < 0 else group_back_profit

        group_track = trade_group.get("track", -1)
        group_track = global_track(group_mode_name) if group_track < 0 else group_track

        #如果没有设置，则依据全局的网格参数
        grid = trade_group.get("grid", -1)   # 是否开启网格
        grid = global_gird(group_mode_name) if grid < 0 else grid

        smart_profit = trade_group.get("smart_profit", -1)
        smart_profit = global_smart_profit(group_mode_name) if smart_profit < 0 else smart_profit


        coin_name = trade_group.get("coin", "")
        money_name = trade_group.get("money", "")
        symbol = "{}{}".format(coin_name, money_name).lower()
        #
        # current_price = get_current_price(symbol)

        # 判断是否要开始收割了
        if grid == 1:
            # 网格收割法，倒序依次判断所有可以收割的单子
            len_trades = len(trades)

            for trade in trades[::-1]:
                # 已经卖出
                if trade.get("is_sell", 0):
                    len_trades -= 1
                    continue

                # 要求的卖出方式不是止盈卖出, 则另作处理
                if trade.get("sell_type", "profit") != "profit":
                    continue

                if trade.get("last_sell_failed", None):
                    # 对于刚刚失败过的订单，15分钟内不再尝试卖出
                    if (datetime.now() - trade["last_sell_failed"]).total_seconds() < 600:
                        continue

                # 以尾单价格判断是否该收割尾单
                ref_price = trade['buy_price']
                ref_cost = trade["cost"]
                ref_amount = trade['amount']    # 卖出时以币算
                plan_sell_amount = format_float(ref_amount, 6)
                ref_time = trade["buy_time"]
                symbol = "{}{}".format(trade["coin"], trade["money"]).lower()

                # 如果没有设置则使用group的
                trade_limit_profit = trade.get("limit_profit", -1)
                trade_limit_profit = group_limit_profit if trade_limit_profit < 0 else trade_limit_profit
                trade_back_profit = trade.get('back_profit', -1)
                trade_back_profit = group_back_profit if trade_back_profit < 0 else trade_back_profit
                trade_track = trade.get("track", -1)
                trade_track = group_track if trade_track < 0 else trade_track
                # 判断是否该卖出了
                if should_stop_profit(symbol, ref_price, trade_limit_profit, trade_back_profit, ref_time, track=trade_track, smart_profit=smart_profit):
                    ret = sell_market(symbol, amount=plan_sell_amount, currency=coin_name.lower())
                    make_deal = True
                    if ret.get("code", 0) == 1:
                        len_trades -= 1
                        time_now = datetime.now()
                        detail = ret.get("data", {})
                        field_amount = detail.get("field_amount", 0)  # 币
                        field_cash_amount = detail.get("field_cash_amount", 0)  # 金
                        deal_price = detail.get("price", 0) #这里的成交价格已经是刨除手续之外的了，
                        deal_price = get_current_price(symbol) if deal_price<=0 else deal_price
                        fees = detail.get("fees", 0)

                        # 卖出盈利
                        sell_profit = (deal_price - ref_price) * field_amount
                        # sell_profit = field_cash_amount - ref_amount
                        sell_profit_percent = sell_profit / ref_cost

                        # 修改尾单的信息，置为已卖出，修改卖出价格等
                        trade["is_sell"] = 1
                        trade['sell_type'] = 'profit'
                        trade["sell_price"] = deal_price
                        trade["profit"] = sell_profit
                        trade["profit_percent"] = sell_profit_percent
                        trade["sell_time"] = time_now

                        # 更改group信息
                        trade_group["profit"] += sell_profit
                        trade_group["last_profit_percent"] = sell_profit_percent    #尾单收益比
                        trade_group["profit_percent"] = trade_group["profit"] / trade_group["max_cost"]

                        # 从整体持仓量和成本减去实际卖掉量和钱，止盈，成本会被渐渐拉低，甚至为负
                        trade_group["amount"] -= field_amount
                        trade_group["cost"] -= (field_cash_amount-fees)

                        # 持仓成本得用总成本减去卖掉的这单的成本
                        # trade_group["cost"] -= ref_cost#不对
                        trade_group["cost"] = 0 if trade_group["cost"] < 0.0001 else trade_group["cost"]
                        trade_group["amount"] = 0 if trade_group["amount"] < 0.0001 else trade_group["amount"]

                        trade_group["last_update"] = time_now
                        if trade_group["amount"] >= 0.0001 and trade_group["cost"] >= 0.0001:
                            trade_group["avg_price"] = trade_group["cost"] / trade_group["amount"]

                        trade_group["sell_counts"] += 1
                        trade_group["patch_index"] -= 1     #每卖掉一单，补仓次数减一，以保证下次补仓的正确

                        msg = "[网格止盈{}] 实际卖出币量： {}, 卖出金额: {}, 卖出成交价格: {}, 上次买入价格： {}, 盈利金额： {}, 盈利比： {}%". \
                            format(symbol.upper(), round(field_amount, 4), round(field_cash_amount, 6),
                                   round(deal_price, 6),
                                   round(ref_price, 6), round(sell_profit, 6), round(sell_profit_percent * 100, 3))

                        log_config.output2ui(msg, 5)
                        logger.warning(msg)
                        log_config.notify_user(msg, own=True)
                    else:
                        log_config.output2ui(u"[{}]网格止盈失败, 请检查您的持仓情况, 计划止盈卖出币量： {}".format(symbol.upper(), round(plan_sell_amount, 4)), 3)
                        time_now = datetime.now()
                        trade["last_sell_failed"] = time_now
                        if "failed_times" in trade.keys():
                            trade["failed_times"] += 1
                        else:
                            trade["failed_times"] = 1

                        if trade.get("failed_times", 0) >= 3:
                            len_trades -= 1
                            trade["is_sell"] = 1
                            trade['sell_type'] = 'failed'
                            trade["sell_price"] = 0
                            trade["profit"] = 0
                            trade["profit_percent"] = 0
                            trade["sell_time"] = time_now

                            # 更改group信息
                            # 从整体持仓量和成本减去实际卖掉量和钱，止盈，成本会被渐渐拉低，甚至为负
                            trade_group["amount"] -= trade["amount"]
                            trade_group["cost"] -= trade["cost"]
                            trade_group["cost"] = 0 if trade_group["cost"] < 0.0001 else trade_group["cost"]
                            trade_group["amount"] = 0 if trade_group["amount"] < 0.0001 else trade_group["amount"]

                            trade_group["last_update"] = time_now
                            if trade_group["amount"] >= 0.0001 and trade_group["cost"] >= 0.0001:
                                trade_group["avg_price"] = trade_group["cost"] / trade_group["amount"]

                            trade_group["patch_index"] -= 1  # 每卖掉一单，补仓次数减一，以保证下次补仓的正确
                            log_config.output2ui(u"网格止盈[{}]连续失败次数超限, 为不影响后续交易的监控, 放弃对本次交易的监控．".format(symbol.upper()), 3)

                        pause = True

            # 判断是不是全部卖出了
            if len_trades <= 0:
                trade_group["end_time"] = datetime.now()
                trade_group["is_sell"] = 1
                msg = "[整组完成{}] 本组交易最大持仓本金： {}, 共盈利{}次, 总盈利金额： {}, 盈利比： {}%, 持续时间： {}分钟". \
                    format(symbol.upper(), round(trade_group["max_cost"], 6), trade_group["sell_counts"],
                           round(trade_group["profit"], 4),
                           round(trade_group["profit_percent"]*100, 3), int((trade_group["end_time"]-trade_group["start_time"]).total_seconds()/60))
                log_config.output2ui(msg, 5)
                logger.warning(msg)
                log_config.notify_user(msg, own=True)
            else:
                # 修改最后一次买入价格为最后一单未卖出的买入价格
                trade_group["last_buy_price"] = trades[len_trades-1]["buy_price"]

                # 卖出一单后，平均价格应该是所有未卖出的单子的总成本除以总量
                not_sell_cost = 0
                not_sell_amount = 0
                for trade in trades:
                    if not trade.get("is_sell", 0):
                        not_sell_cost += trade["cost"]
                        not_sell_amount += trade["amount"]
                trade_group["avg_price"] = not_sell_cost / not_sell_amount

        else:
            # 以整体均价判断是否该卖出所有
            avg_price = trade_group.get("avg_price", 0)
            amount = trade_group.get("amount", 0)   # 持币量
            # cost = trade_group.get("cost", 0)       # 当前持仓成本
            ref_price = avg_price
            plan_sell_amount = format_float(amount, 6)
            ref_time = trade_group.get("start_time", None)

            # 判断是否该卖出了
            if trade_group.get("sell_out", 0) or should_stop_profit(symbol, ref_price, group_limit_profit, group_back_profit, ref_time, track=group_track):
                ret = sell_market(symbol, amount=plan_sell_amount, currency=coin_name.lower())
                make_deal = True
                if ret.get("code", 0) == 1:
                    time_now = datetime.now()
                    detail = ret.get("data", {})
                    field_amount = detail.get("field_amount", 0)  # 币
                    field_cash_amount = detail.get("field_cash_amount", 0)  # 金
                    deal_price = detail.get("price", 0)
                    deal_price = get_current_price(symbol) if deal_price<=0 else deal_price
                    fees = detail.get("fees", 0)

                    sell_profit = 0
                    last_profit_percent = 0
                    # 整体卖出后，把每一单都设置为已卖出状态
                    for trade in trade_group["trades"]:
                        if trade["is_sell"] == 0:
                            trade["is_sell"] = 1
                            trade["sell_type"] = "profit"
                            trade["sell_time"] = time_now
                            trade["sell_price"] = deal_price
                            trade["profit"] = (deal_price-trade["buy_price"]) * trade["amount"]
                            trade["profit_percent"] = trade["profit"]/trade["cost"]
                            if last_profit_percent == 0:
                                last_profit_percent = trade["profit_percent"]

                        sell_profit += trade["profit"]

                    #卖出盈利
                    # sell_profit = (deal_price - ref_price) * field_amount
                    # sell_profit = field_cash_amount - ref_amount
                    # sell_profit_percent = sell_profit / ref_cost

                    trade_group["profit"] = sell_profit
                    trade_group["profit_percent"] = trade_group["profit"]/trade_group["max_cost"]
                    trade_group["last_profit_percent"] = last_profit_percent
                    trade_group["amount"] -= field_amount
                    trade_group["cost"] -= (field_cash_amount-fees)
                    trade_group["amount"] = 0 if trade_group["amount"] < 0.0001 else trade_group["amount"]
                    trade_group["cost"] = 0 if trade_group["cost"] < 0.0001 else trade_group["cost"]
                    trade_group["last_update"] = time_now
                    trade_group["sell_counts"] += 1
                    trade_group["end_time"] = time_now
                    trade_group["patch_index"] = 0  # 全部卖完，补仓序号置为0
                    trade_group["is_sell"] = 1

                    msg = "[整体止盈{}] 实际卖出币量： {}, 卖出金额: {}, 卖出成交价格: {}, 买入均价： {}, 本次盈利金额： {}, 盈利比： {}%, 本组交易整体盈利额： {}, 盈利比: {}%". \
                        format(symbol.upper(), round(field_amount, 4), round(field_cash_amount, 6),
                               round(deal_price, 6),
                               round(ref_price, 6), round(sell_profit, 6), round(sell_profit_percent * 100, 4),
                               round(trade_group["profit"], 6), round(trade_group["profit_percent"] * 100, 4))

                    log_config.output2ui(msg, 5)
                    logger.warning(msg)
                    log_config.notify_user(msg, own=True)

                    msg = "[整组完成{}] 本组交易最大持仓本金： {}, 共盈利{}次, 总盈利金额： {}, 盈利比： {}%, 持续时间： {}分钟". \
                        format(symbol.upper(), round(trade_group["max_cost"], 6), trade_group["sell_counts"],
                               round(trade_group["profit"], 4),
                               round(trade_group["profit_percent"] * 100, 3),
                               int((trade_group["end_time"] - trade_group["start_time"]).total_seconds() / 60))
                    log_config.output2ui(msg, 5)
                    logger.warning(msg)
                    log_config.notify_user(msg, own=True)
                else:
                    log_config.output2ui(u"整体止盈失败, 请检查您的持仓情况, 计划卖出[{}]币量： {}".format(symbol.upper(), round(plan_sell_amount, 4)), 3)
                    time_now = datetime.now()
                    trade_group["last_profit_percent"] = 0
                    trade_group["amount"] = 0
                    trade_group["cost"] = 0
                    trade_group["last_update"] = time_now
                    trade_group["sell_counts"] += 1
                    trade_group["end_time"] = time_now
                    trade_group["patch_index"] = 0  # 全部卖完，补仓序号置为0
                    trade_group["is_sell"] = 1

    if make_deal:
        global should_update_ui_tree
        should_update_ui_tree = True


def stg_smart_patch():
    make_deal = False
    for trade_group in config.TRADE_RECORDS_NOW:
        coin = trade_group['coin'].upper()
        money = trade_group['money'].upper()
        symbol = "{}{}".format(coin, money).lower()

        if trade_group["end_time"]:
            logger.info("trade group is ended.")
            continue

        if trade_group.get("stop_patch", 0):
            # log_config.output2ui(u"[{}]该组交易被设置为不再补仓".format(symbol))
            continue

        if trade_group.get("last_buy_failed", None):
            # 对于刚刚补仓失败过的订单，15分钟内不再尝试买入
            if (datetime.now() - trade_group["last_buy_failed"]).total_seconds() < 600:
                continue

        group_mode_name = trade_group.get("mode", "")
        group_mode_name = config.TRADE_MODE if not group_mode_name else group_mode_name

        patch_ref = trade_group.get("patch_ref", -1)
        patch_ref = global_patch_ref(group_mode_name) if patch_ref<0 else patch_ref
        patch_ref = 0 if patch_ref > 1 else patch_ref

        patch_interval = trade_group.get("patch_interval", -1)
        patch_interval = global_patch_interval(group_mode_name) if patch_interval < 0 else patch_interval

        smart_patch = trade_group.get("smart_patch", -1)
        smart_patch = global_smart_patch(group_mode_name) if smart_patch < 0 else smart_patch

        # 是否需要补仓
        if patch_ref == 0:   #参考是整体均价
            ref_price = trade_group.get("avg_price", 0)
            patch_name = u"整体补仓"
        else:   # 参考上一次买入价
            ref_price = trade_group.get("last_buy_price", 0)
            patch_name = u"尾单补仓"

        group_mode = config.TRADE_MODE_CONFIG.get(group_mode_name)

        if should_patch(symbol=symbol, ref_price=ref_price, patch_interval=patch_interval, smart_patch=smart_patch):
            # 这个交易对如果设置了单独的预算则使用单独的邓预算，否则使用全局预算
            principal = trade_group.get("principal", 0)
            if principal <= 0:
                principal = config.CURRENT_SYMBOLS.get(money, {}).get("principal", 0)
                if principal <= 0:
                    principal = config.CURRENT_SYMBOLS.get(money, {}).get("balance", 0)*2

                coins_num = len(config.CURRENT_SYMBOLS.get(money).get("coins", []))
                coins_num = 1 if coins_num == 0 else coins_num
                principal = principal/coins_num     #当前货币的本金预算除以需要监控的币对数，就是这个交易对的预算

            patch_mode = trade_group.get("patch_mode", "multiple")
            patch_mode = group_mode.get("patch_mode", "multiple") if not patch_mode else patch_mode

            patch_times = trade_group.get("limit_patch_times", -1)
            patch_times = group_mode.get("limit_patch_times", 5) if patch_times < 0 else patch_times

            if trade_group["patch_index"] >= patch_times:
                log_config.output2ui(u"[{}]已经达到补仓次数上限({}次), 停止补仓!".format(symbol.upper(), patch_times), 2)
                continue

            multiple = patch_multiple(trade_group["patch_index"]+1, patch_mode, patch_times)
            if multiple == 0:
                log_config.output2ui(u"[{}]已经达到补仓次数上限, 停止补仓!".format(symbol.upper()), 2)
                continue

            # plan_buy_cost = principal*group_mode['first_trade']*multiple
            plan_buy_cost = trade_group["first_cost"] * multiple    # 修改成参考为第一单的买入量
            ret = buy_market(symbol, currency=money.lower(), amount=plan_buy_cost)
            make_deal = True
            # 买入成功
            if ret.get("code", 0) == 1:
                time_now = datetime.now()
                # current_price = get_current_price(symbol)
                detail = ret.get("data", {})
                field_amount = detail.get("field_amount", 0)  # 币
                field_cash_amount = detail.get("field_cash_amount", 0)  # 金
                deal_price = detail.get("price", 0)     # 成交价格
                deal_price = get_current_price(symbol) if deal_price <= 0 else deal_price
                fees = detail.get("fees", 0)

                trade = {
                    "buy_type": "auto",  # 买入模式：auto 自动买入(机器策略买入)，man手动买入,
                    "sell_type": "profit",# 要求的卖出模式，机器买入的一般都为动止盈卖出。可选：profit 止盈卖出， no-不要卖出，针对手动买入的单，smart-使用高抛，kdj等策略卖出
                    "buy_time": time_now,
                    "sell_time": None,
                    "coin": coin,
                    "amount": field_amount-fees,     # 买入或卖出的币量
                    "buy_price": deal_price,        # 实际挂单成交的价格
                    "sell_price": 0,
                    "money": money,
                    "cost": field_cash_amount,  # 实际花费的计价货币量
                    "is_sell": 0,  # 是否已经卖出
                    "profit_percent": 0,  # 盈利比，卖出价格相对于买入价格
                    "profit": 0,  # 盈利额，只有卖出后才有
                    "limit_profit": -1,
                    "back_profit": -1,
                    "track": -1,
                    "failed_times": 0,
                    "uri": "{}{}".format(time_now.strftime("%Y%m%d%H%M%S"), random.randint(100, 999)),
                    "group_uri": trade_group["uri"],
                    "user": config.CURRENT_ACCOUNT,
                    "platform": config.CURRENT_PLATFORM
                }

                trade_group["trades"].append(trade)
                trade_group["amount"] += (field_amount-fees)
                trade_group["cost"] += field_cash_amount
                trade_group["max_cost"] = trade_group["cost"] if trade_group["max_cost"] < trade_group["cost"] else trade_group["max_cost"]   #整体过程中最大持仓成本

                # 这样算出来的不对，因为成本是刨除利润了的
                # trade_group["avg_price"] = trade_group["cost"]/trade_group["amount"]

                trade_group["profit_percent"] = trade_group["profit"]/trade_group["max_cost"]
                trade_group["buy_counts"] += 1
                trade_group["patch_index"] += 1
                trade_group["last_buy_price"] = deal_price
                if not trade_group["start_time"]:
                    trade_group["start_time"] = time_now
                trade_group["last_update"] = time_now

                # 卖出一单后，平均价格应该是所有未卖出的单子的总成本除以总量
                not_sell_cost = 0
                not_sell_amount = 0
                for trade in trade_group["trades"]:
                    if not trade.get("is_sell", 0):
                        not_sell_cost += trade["cost"]
                        not_sell_amount += trade["amount"]
                trade_group["avg_price"] = not_sell_cost / not_sell_amount

                smart_patch_interval = (ref_price-deal_price)/ref_price
                msg = "[{}{}] 计划买入金额： {}, 实际买入币量： {}, 实际买入金额: {}, 补仓参考价格: {}, 补仓成交价格: {}, 计划补仓间隔: {}%, 智能补仓间隔: {}%, 第{}次补仓, 补仓系数: {}". \
                    format(patch_name, symbol.upper(), round(plan_buy_cost, 6), round(field_amount, 6), round(field_cash_amount, 6),
                           round(ref_price, 6), round(deal_price, 6), round(patch_interval*100, 4),
                           round(smart_patch_interval*100, 4), trade_group["patch_index"], multiple)
                log_config.output2ui(msg, 4)
                logger.warning(msg)
                log_config.notify_user(msg, own=True)
            else:
                log_config.output2ui(u"补仓{}失败, 请检查您的可操配资金是否足够, 并及时充值以或调小资金预算额, 以免影响系统正常补仓. 本次计划补仓： {}".format(symbol.upper(), round(plan_buy_cost, 6)), 3)
                trade_group["last_buy_failed"] = datetime.now()
                pause = True

    if make_deal:
        global should_update_ui_tree
        should_update_ui_tree = True
    # 如果有买入失败的情况，则返回True 这样会暂停15钟，不再尝试买入
    # return pause


#
# def auto_trade():
#     logger.info("auto trade trigger...group num={}".format(len(config.TRADE_RECORDS_NOW)))
#
#     for trade_group in config.TRADE_RECORDS_NOW:
#         if trade_group["end_time"]:
#             logger.info("trade group is ended.")
#             continue
#
#         logger.info("trade group={}".format(trade_group))
#         interval_ref = trade_group.get("interval_ref", 0)
#         trades = trade_group.get("trades", [])
#         grid = trade_group.get("grid", 1)   # 是否开启网格
#         avg_price = trade_group.get("avg_price", 0)
#         amount = trade_group.get("amount", 0)     # 持币量
#         cost = trade_group.get("cost", 0)           # 当前持仓成本
#         max_cost = trade_group.get("max_cost", 0)   # 最大持仓成本
#         last_buy_price = trade_group.get("last_buy_price", 0)
#         last_buy_amount = trade_group.get("last_buy_amount", 0)
#         last_buy_cost = trade_group.get("last_buy_cost", 0)
#
#         # 如果没有单独设置，则使用全局的止盈参数
#         limit_profit = trade_group.get("limit_profit", 0)
#         limit_profit = global_limit_profit() if limit_profit < 0 else limit_profit
#         back_profit = trade_group.get("back_profit", 0)
#         back_profit = global_back_profit() if back_profit < 0 else back_profit
#
#         last_update = trade_group.get("last_update", None)
#         coin_name = trade_group.get("coin", "")
#         money_name = trade_group.get("money", "")
#         symbol = "{}{}".format(coin_name, money_name).lower()
#         current_price = get_current_price(symbol)
#
#         trade_mode_name = trade_group.get("mode", "")
#         trade_mode_name = config.TRADE_MODE if not trade_mode_name else trade_mode_name
#         trade_mode = config.TRADE_MODE_CONFIG.get(trade_mode_name, {})
#
#         # 判断是否要开始收割了
#         if grid == 1:
#             # 以尾单价格判断是否该收割尾单
#             ref_price = last_buy_price
#             ref_cost = last_buy_cost
#             plan_sell_amount = last_buy_amount
#             profit_name = u"尾单止盈"
#         else:
#             # 以整体均价判断是否该卖出所有
#             ref_price = avg_price
#             ref_cost = cost
#             plan_sell_amount = amount
#             profit_name = u"整体止盈"
#
#         # 判断是否该卖出了
#         if should_stop_profit(symbol.lower(), ref_price, limit_profit, back_profit, last_update):
#             logger.info("auto trade should_stop_profit, grid={}, plan_sell_coin_num={}, ref_price={}, "
#                         "ref_amount={} cp={}, \ntrade group={}".format(grid, plan_sell_amount, ref_price, ref_cost, current_price, trade_group))
#
#             ret = sell_market(symbol, amount=plan_sell_amount, currency=coin_name.lower())
#             if ret.get("code", 0) == 1:
#                 time_now = datetime.now()
#                 detail = ret.get("data", {})
#                 field_amount = detail.get("field_amount", 0)  # 币
#                 field_cash_amount = detail.get("field_cash_amount", 0)  # 金
#                 fees = detail.get("fees", 0)
#
#                 #卖出盈利
#                 sell_profit = (current_price - ref_price) * field_amount
#                 # sell_profit = field_cash_amount - ref_amount
#                 sell_profit_percent = sell_profit / ref_cost
#
#                 # 找到最后一单没有卖出的
#                 last_index = len(trades)-1
#                 for trade in reversed(trades):
#                     if trade.get("is_sell") == 0:
#                         # 修改尾单的信息，置为已卖出，修改卖出价格等
#                         trade["is_sell"] = 1
#                         trade["sell_price"] = current_price
#                         trade["profit"] = sell_profit
#                         trade["profit_percent"] = sell_profit_percent
#                         trade["sell_time"] = time_now
#                         break
#                     last_index -= 1
#
#                 trade_group["profits"].append({"time": time_now, "profit": sell_profit})
#                 trade_group["last_profit_percent"] = sell_profit_percent
#                 trade_group["profit_percent"] = sell_profit/trade_group["max_cost"]
#
#                 trade_group["amount"] = trade_group["amount"]-field_amount
#                 trade_group["cost"] = trade_group["cost"] - field_cash_amount
#
#                 trade_group["last_update"] = time_now
#                 trade_group["avg_price"] = trade_group["cost"]/trade_group["amount"]
#                 trade_group["sell_counts"] += 1
#                 # trade_group["buy_counts"] -= 1
#                 trade_group["last_buy_sell"] += 1
#
#                 # 全部卖完了, ,或者是整体卖出了，这组策略结束
#                 if last_index <= 0 or grid == 0:
#                     trade_group["end_time"] = time_now
#                 else:
#                     # 将倒数第二单的买入价、买入量置为尾单信息
#                     new_last_trade = trade_group["trades"][last_index-1]
#                     trade_group["last_buy_amount"] = new_last_trade["amount"]
#                     trade_group["last_buy_price"] = new_last_trade["buy_price"]
#                     trade_group["last_buy_cost"] = new_last_trade["cost"]
#
#                 logger.info("sell succeed! symbol={}, sell_coin_actual={}， sell profit={}, percent={}".format(symbol,
#                                                                                                               field_amount,
#                                                                                                               sell_profit,
#                                                                                                               sell_profit_percent))
#
#                 msg = "[{}{}] 实际卖出币量： {}, 卖出金额: {}, 卖出价格: {}, 上次买入价格： {}, 盈利金额： {}, 盈利比： {}%". \
#                     format(profit_name, symbol.upper(), round(field_amount, 4), round(field_cash_amount, 6),
#                            round(current_price, 6),
#                            round(ref_price, 6), round(sell_profit, 6), round(sell_profit_percent * 100, 4))
#
#                 log_config.output2ui(msg, 5)
#                 logger.warning(msg)
#                 log_config.notify_user(msg, own=True)
#
#             else:
#                 log_config.output2ui(u"移动止盈失败, 请检查您的持仓情况, 计划卖出币量： {}".format(round(plan_sell_amount, 4)), 3)
#
#         # 是否需要补仓
#         if interval_ref == 0:   #参考是整体均价
#             ref_price = avg_price
#             patch_name = u"整体补仓"
#         else:   # 参考上一次买入价
#             ref_price = last_buy_price
#             patch_name = u"尾单补仓"
#
#         fill_interval = trade_mode.get("interval", 0.01)    # 补仓间隔
#         # 如果当前价格小于整体均价的一定比例，则补单
#         if current_price < ref_price*(1-fill_interval):
#             plan_buy_amount = trade_group.get("last_buy_amount", 0)
#             plan_buy_cost = trade_group.get("last_buy_cost", 0) * 2      # 先直接按倍投的方式来弄
#             ret = buy_market(symbol, currency=money_name.lower(), amount=plan_buy_cost)
#             # 买入成功
#             if ret.get("code", 0) == 1:
#                 time_now = datetime.now()
#                 detail = ret.get("data", {})
#                 field_amount = detail.get("field_amount", 0)  # 币
#                 field_cash_amount = detail.get("field_cash_amount", 0)  # 金
#                 fees = detail.get("fees", 0)
#
#                 msg = "[{}{}] 计划买入金额： {}, 实际买入币量： {}, 实际买入金额: {}, 参考价格: {}, 当前价格: {}, 补仓间隔: {}%". \
#                     format(patch_name, symbol.upper(), round(plan_buy_cost, 4), round(field_amount, 6), round(field_cash_amount, 6),
#                            round(ref_price, 6), round(current_price, 6), round(fill_interval*100, 2))
#                 log_config.output2ui(msg, 4)
#                 logger.warning(msg)
#                 log_config.notify_user(msg, own=True)
#
#                 buy_price_actual = current_price
#                 time_now = datetime.now()
#                 trade = {
#                     "buy_type": "auto",  # 买入模式：auto 自动买入(机器策略买入)，man手动买入,
#                     "sell_type": "profit",# 要求的卖出模式，机器买入的一般都为动止盈卖出。可选：profit 止盈卖出， no-不要卖出，针对手动买入的单，smart-使用高抛，kdj等策略卖出
#                     "buy_time": time_now,
#                     "sell_time": None,
#                     "coin": coin_name,
#                     "amount": field_amount,  # 买入或卖出的币量
#                     "buy_price": buy_price_actual,  # 实际挂单成交的价格
#                     "money": money_name,
#                     "cost": field_cash_amount,  # 实际花费的计价货币量
#                     "is_sell": 0,  # 是否已经卖出
#                     "profit_percent": 0,  # 盈利比，卖出价格相对于买入价格
#                     "profit": 0,  # 盈利额，只有卖出后才有
#                 }
#                 logger.info("auto trade buy succeed, trade={}".format(trade))
#                 trade_group["trades"].append(trade)
#                 trade_group["amount"] += field_amount
#                 trade_group["cost"] += field_cash_amount
#                 trade_group["max_cost"] = trade_group["cost"] if trade_group["max_cost"]<trade_group["cost"] else trade_group["max_cost"]   #整体过程中最大持仓成本
#                 trade_group["avg_price"] = trade_group["cost"]/trade_group["amount"]
#                 trade_group["all_profit_percent"] = (current_price-trade_group["avg_price"])/trade_group["avg_price"]
#                 trade_group["buy_counts"] += 1
#                 trade_group["patch_intervals"].append(fill_interval)
#                 trade_group["last_buy_cost"] = field_cash_amount
#                 trade_group["last_buy_amount"] = field_amount
#                 trade_group["last_buy_price"] = buy_price_actual
#                 if not trade_group["start_time"]:
#                     trade_group["start_time"] = time_now
#                 trade_group["last_update"] = time_now
#                 logger.info("auto trade buy succeed, trade group={}".format(trade_group))
#             else:
#                 log_config.output2ui(u"补仓{}失败, 请检查您的可用余额是否足够, 计划买入币量: {}, 价值金额： {}".format(symbol.upper(), plan_buy_amount, plan_buy_cost), 3)
#
#         avg_price = trade_group.get("avg_price", 0)
#         trade_group["all_profit_percent"] = (current_price-avg_price)/avg_price


def should_kdj_buy(symbol, period="15min", risk=1.04):
    """
    用kdj指标判断是否该买入了，返回买入指数范围在0－－1, 0代表不支持买入，越趋近１越代表支持买入
    :param symbol:
    :param period:
    :param risk: 当前选择的交易策略的风险承受系数
    :return:
    """
    if kdj_buy_params.get("check", 1) != 1:
        log_config.output2ui("kdj_buy_params is not check", 7)
        return 0

    market = "market.{}.kline.{}".format(symbol, period)
    buy_percent = 0
    cur_k2, cur_d2, cur_j2 = get_kdj(market, pos=2)
    cur_k1, cur_d1, cur_j1 = get_kdj(market, pos=1)
    last_diff_kd = cur_k1 - cur_d1
    last_diff_kd2 = cur_k2 - cur_d2

    cur_k, cur_d, cur_j = get_kdj(market)
    diff_kd = cur_k - cur_d

    current_price = get_current_price(symbol)
    upper, middle, lower = get_boll(market=market)

    # 低位即将金叉
    if last_diff_kd < 0 and diff_kd >= 0 and diff_kd > last_diff_kd and cur_k > cur_k1 and diff_kd > last_diff_kd2:
        if cur_k < 22 and cur_d < 20:
            buy_percent += 0.22
        elif cur_k <= 55 and cur_d <= 55 and current_price < middle and cur_d >= cur_d1:  # 中位金叉,且未出中轨
            buy_percent += 0.12

    # 低位回弹
    # kd不能大于40
    limit_kd = 40 * risk

    limit_kd = 15 if limit_kd < 15 else limit_kd
    limit_kd = 35 if limit_kd > 35 else limit_kd
    now = int(time.time()) * 1000
    min_price = get_min_price(symbol, last_time=now - (15 * 60 * 1000))

    if cur_k <= limit_kd or cur_d <= limit_kd:
        # 回暖幅度超过0.008
        up_percent = kdj_buy_params.get("up_percent", 0.003)
        up_percent *= (1 / risk)

        if min_price and min_price > 0:
            actual_up_percent = round((current_price - min_price) / min_price, 4)
            if actual_up_percent >= up_percent:
                # 最近三个周期内出现过kd小于20
                last_k, last_d, last_j = get_kdj(market, 1)
                last_k_2, last_d_2, last_j_2 = get_kdj(market, 2)
                need_k = kdj_buy_params.get("k", 22) * config.RISK * (
                            actual_up_percent / up_percent)  # 回弹幅度越大，自然kd值也会变大，需要放宽限制条件
                need_d = kdj_buy_params.get("d", 22) * config.RISK * (
                            actual_up_percent / up_percent)  # 回弹幅度越大，自然kd值也会变大，需要放宽限制条件

                need_k = 16 if need_k < 16 else need_k
                need_d = 14 if need_d < 14 else need_d
                need_k = 26 if need_k > 25 else need_k
                need_d = 24 if need_d > 24 else need_d

                if (last_k <= need_k and last_d <= need_d and cur_k > last_k) or (
                        cur_k < 15 and cur_d < 15 and (cur_k - cur_d) > -5) or (
                        last_k_2 < need_k and last_d_2 < need_d):
                    if cur_k - cur_d > 0:
                        buy_percent += kdj_buy_params.get("buy_percent", 0.2)

                        if cur_k < 20:
                            logger.info("kdj lb curk<20")
                            buy_percent += (20 - cur_k) / 100

                        ret = is_buy_big_than_sell(symbol, 2)
                        if ret:
                            buy_percent += 0.05
    if buy_percent > 0:
        buy_percent *= risk
        logger.warning("[{}]should_kdj_buy={}".format(symbol, buy_percent))

    return buy_percent


def should_boll_buy(symbol, period="15min", risk=1.04):
    """

    :param symbol:
    :param period:
    :param risk:
    :return:
    """
    if boll_strategy_params.get("check", 1) != 1:
        log_config.output2ui("boll_strategy is not check", 7)
        return 0

    market = "market.{}.kline.{}".format(symbol, period)
    upper, middle, lower = get_boll(market, 0)
    price = get_current_price(symbol)

    buy_percent = 0

    if price <= lower:
        buy_percent += 0.2
        buy_percent += (lower-price)/lower  #低得越多加的越多

    diff1 = upper - middle
    diff2 = middle - lower
    state = 0
    # 先初步判断是否开或缩，参数松
    open_diff1_percent = boll_strategy_params.get("open_diff1_percent", 0.025)
    open_diff2_percent = boll_strategy_params.get("open_diff2_percent", 0.025)
    open_diff1_percent *= risk
    open_diff2_percent *= risk

    pdiff1 = diff1 / price
    pdiff2 = diff2 / price
    if pdiff1 > open_diff1_percent * 0.8 and pdiff2 > open_diff2_percent * 0.8:
        state = 1  # 张口
    close_diff1_percent = boll_strategy_params.get("close_diff1_percent", 0.0025)
    close_diff2_percent = boll_strategy_params.get("close_diff2_percent", 0.0025)
    if pdiff1 < close_diff1_percent * 1.25 and pdiff2 < close_diff2_percent * 1.25:
        state = -1  # 缩口

    # 判断是否开口超跌
    # up_down = get_up_down(market)

    open_now = get_open(market, 0)
    up_down = (price - open_now) / open_now  # 当前这个周期的涨跌幅

    now = int(time.time()) * 1000
    history_open_close = None
    if state == 1 or state == -1:
        # 历史开口幅度大于opp
        history_open_close = is_history_open_close(market, 3, open_diff1_percent, close_diff1_percent)
    if state == 1:
        if price < lower:
            # 跌幅超过open_down_percent（0.03）
            down_percent = boll_strategy_params.get("open_down_percent", -0.02)
            if up_down <= down_percent and up_down > -0.05:
                # 超跌在右侧
                open_up_percent = boll_strategy_params.get("open_up_percent", 0.01)
                # 最近一段时间上涨幅度超过open_up_percent（0.01）
                if price > get_min_price(symbol, now - 5 * 60 * 1000) * (1 + open_up_percent):
                    # 历史开口幅度大于open_diff1_percent
                    if history_open_close == "open":
                        logger.info("开口超跌")
                        buy_percent += boll_strategy_params.get("open_buy_percent", 0.2)

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
                        return buy_percent
                    trade_percent = boll_strategy_params.get("trade_percent", 1.5)
                    # 交易量0-3 大于 1.5 倍的 3-6
                    if t1_vol > trade_percent * t2_vol:
                        close_up_percent = boll_strategy_params.get("close_up_percent", 0.03)
                        # 当天上涨幅度不能超过3%
                        if up_down < close_up_percent:
                            # 历史开口幅度大于open_diff1_percent
                            if history_open_close == "close":
                                logger.info("缩口向上")
                                buy_percent += boll_strategy_params.get("close_buy_percent", 0.2)

    if buy_percent > 0:
        buy_percent *= risk
        logger.warning("[{}]should_boll_buy={}".format(symbol, buy_percent))
    return buy_percent


def first_buy(coin, money, principal, multiple=1, build="smart"):
    trade_mode = config.TRADE_MODE_CONFIG.get(config.TRADE_MODE, {})
    plan_buy_amount = principal * trade_mode.get("first_trade", 0.05) * multiple
    symbol = "{}{}".format(coin, money).lower()

    # current_price = get_current_price(symbol)

    ret = buy_market(symbol, amount=plan_buy_amount, currency=money.lower())
    if ret.get("code", 0) == 1:
        detail = ret.get("data", {})
        field_amount = detail.get("field_amount", 0)  # 币
        field_cash_amount = detail.get("field_cash_amount", 0)  # 金
        fees = detail.get("fees", 0)
        deal_price = detail.get("price", 0)
        deal_price = get_current_price(symbol) if deal_price <= 0 else deal_price
        msg = "[建仓{}] 计划买入金额: {}, 实际成交金额: {}, 实际买入币量： {}, 买入成交价格: {}".\
            format(symbol.upper(), round(plan_buy_amount, 6), round(field_cash_amount, 6), round(field_amount-fees, 6), round(deal_price, 6))

        time_now = datetime.now()
        trade = {
            "buy_type": "auto",  # 买入模式：auto 自动买入(机器策略买入)，man手动买入,
            "sell_type": "profit",
            # 要求的卖出模式，机器买入的一般都为止盈卖出。可选：sell_profit 止盈卖出（默认）， sell_no-不要卖出，针对手动买入的单，sell_smart-使用高抛，kdj等策略卖出
            "limit_profit": -1,  # 大于零有效，否则参考其所属的交易组的参数
            "back_profit": -1,  # 追踪回撤系数
            "track": -1,
            "buy_time": time_now,
            "sell_time": None,
            "coin": coin.upper(),
            "money": money.upper(),
            "amount": field_amount-fees,  # 实际得到的币量，实际买到的币被平台扣了千二
            "buy_price": deal_price,  # 实际买入成交的价格
            "cost": field_cash_amount,  # 实际花费的计价货币量
            "is_sell": 0,  # 是否已经卖出
            "sell_price": 0,  # 实际卖出的价格
            "profit_percent": 0,  # 盈利比，卖出价格相对于买入价格
            "profit": 0,        # 盈利额，只有卖出后才有
            "uri": "{}{}".format(time_now.strftime("%Y%m%d%H%M%S"), random.randint(100, 999)),
            "user": config.CURRENT_ACCOUNT,
            "platform": config.CURRENT_PLATFORM
        }

        trade_group = {
            "build": build,  # 首单触发原因，
            "mode": "",     # 按何种交易风格执行
            "coin": coin.upper(),
            "money": money.upper(),
            "trades": [],  # 每一次交易记录，
            "grid": -1,      # 是否开启网格交易
            "track": -1,     # 是否开启追踪止盈
            "smart_profit": -1,  # 是否启用智能止盈
            "smart_patch": -1,  # 是否启用智能补仓
            "patch_mode": "",  # 补仓的模式，默认为倍投
            "last_sell_failed": None,

            "amount": field_amount-fees,  # 持仓数量（币）
            "cost": field_cash_amount,  # 持仓费用（计价货币）
            "max_cost": field_cash_amount,
            "avg_price": deal_price,  # 持仓均价
            "profit": 0,  # 这组策略的总收益， 每次卖出后都进行累加
            "profit_percent": 0,  # 整体盈利比（整体盈利比，当前价格相对于持仓均价,）
            "last_profit_percent": 0,  # 尾单盈利比（最后一单的盈利比）
            "limit_profit": -1,  # 止盈比例
            "back_profit": -1,  # 追踪比例
            "buy_counts": 1,  # 已建单数，目前处理买入状态的单数
            "sell_counts": 0,  # 卖出单数，卖出的次数，其实就是尾单收割次数
            "patch_index": 0,   # 还没补过
            "patch_ref": -1,  # 间隔参考
            "patch_interval": -1,
            "last_buy_price": deal_price,  # 最后一次买入价格，用来做网格交易，如果最后一单已经卖出，则这个价格需要变成倒数第二次买入价格，以便循环做尾单
            "start_time": time_now,
            "end_time": None,
            "last_update": time_now,
            "uri": "{}{}".format(time_now.strftime("%Y%m%d%H%M%S"), random.randint(100, 999)),
            "principal": -1,
            "is_sell": 0,
            "stop_patch": 0,
            "first_cost": trade["cost"],
            "user": config.CURRENT_ACCOUNT,
            "platform": config.CURRENT_PLATFORM,
            "limit_patch_times": -1,
        }
        trade["group_uri"] = trade_group["uri"]
        trade_group["trades"].append(trade)
        # 把最新插在最前面
        config.TRADE_RECORDS_NOW.insert(0, trade_group)
        log_config.output2ui(msg, 4)
        logger.warning(msg)
        log_config.notify_user(msg, own=True)
        return True
    else:
        logger.warning("first buy {} failed".format(symbol))
        return False


def stg_smart_first():
    """
    智能建仓
    :return:
    """
    make_deal = False
    pause = False
    for money, value in config.CURRENT_SYMBOLS.items():
        coins = value.get("coins", [])
        if not coins:
            continue

        principal = value.get("principal", 0)
        coins_num = len(coins)
        principal = principal/coins_num
        if principal <= 0:
            log_config.output2ui(u"当前设置的预算本金为零, 系统不会建仓, 请在主界面设置合理的预算本金数值！", 3)
            continue

        for coin_info in coins:
            # 保存交易对, 用于加载历史数据
            coin = coin_info["coin"]
            symbol = "{}{}".format(coin, money).lower()
            if is_already_buy_first(symbol):
                continue

            if is_still_down2(symbol, bp=0.0030):
                continue

            smart_first = global_smart_first()
            build_mode = "smart"
            risk = global_risk()
            if smart_first:
                kdj_buy = should_kdj_buy(symbol, period="15min", risk=risk)
                boll_buy = should_boll_buy(symbol, period="15min", risk=risk)
                low_buy = should_low_buy(symbol, period="15min", risk=risk)
                fly_buy = should_fly_buy(symbol, period="5min", risk=risk)
                buy_multiple = kdj_buy + boll_buy + low_buy + fly_buy
            else:
                # 如果没有开启智能建仓模式, 则不作任何分析处理，直直接以当前价格建仓
                buy_multiple = 0.15
                build_mode = "auto"

            if buy_multiple > 0:
                buy_multiple *= risk    # 能承担的风险系数越大，首单买的越多
                ret = first_buy(coin, money, principal, buy_multiple/0.1, build=build_mode)
                if ret:
                    make_deal = True
                    if smart_first:
                        log_config.output2ui(
                            u"[{}]智能建仓成功, 智能分析建仓推荐指数: {}".format(symbol.upper(), round(buy_multiple, 4)), 0)
                    else:
                        log_config.output2ui(u"[{}]市价建仓成功, 因未开启智能建仓, 当前行情已稳定, 直接以当前市价建仓！".format(symbol.upper()))
                else:
                    log_config.output2ui(u"[{}]建仓失败! 请关注您的账户可操配资金是否充足！".format(symbol.upper()), 3)
                    pause = True

    if make_deal:
        global should_update_ui_tree
        should_update_ui_tree = True
    return pause


def kdj_strategy_buy():
    if kdj_buy_params.get("check", 1) != 1:
        log_config.output2ui("kdj_buy is not check", 2)
        return False

    buy_in = False
    period = kdj_buy_params.get("period", "15min")
    for money, value in config.CURRENT_SYMBOLS.items():
        coins = value.get("coins", [])
        principal = value.get("principal", 0)
        coins_num = len(coins)
        coins_num = 1 if coins_num <= 0 else coins_num
        principal = principal/coins_num
        if principal <= 0:
            continue

        if coins:
            for coin_info in coins:
                # 保存交易对, 用于加载历史数据
                coin = coin_info["coin"]
                symbol = "{}{}".format(coin, money).lower()
                if is_already_buy_first(symbol):
                    continue

                market = "market.{}.kline.{}".format(symbol, period)

                buy_percent = 0

                # # 如果继续跌，暂时不买
                # if is_still_down(symbol):
                #     logging.info("kdj buy checking, still down!")
                #     return False

                cur_k2, cur_d2, cur_j2 = get_kdj(market, pos=2)
                cur_k1, cur_d1, cur_j1 = get_kdj(market, pos=1)
                last_diff_kd = cur_k1 - cur_d1
                last_diff_kd2 = cur_k2 - cur_d2

                cur_k, cur_d, cur_j = get_kdj(market)
                diff_kd = cur_k - cur_d

                current_price = get_current_price(symbol)
                upper, middle, lower = get_boll(market=market)

                strategy_flag = []
                # 低位即将金叉
                if last_diff_kd < 0 and diff_kd >= 0 and diff_kd > last_diff_kd and cur_k > cur_k1 and diff_kd > last_diff_kd2:
                    if cur_k < 22 and cur_d < 20:
                        logging.warning(u"KDJ LGX, k1={}, k={}, d1={}, d={}, cp={}. curk2={}, last_diff_kd2={}".format(cur_k1, cur_k, cur_d1, cur_d, current_price, cur_k2, last_diff_kd2))
                        buy_percent += 0.22
                        strategy_flag.append(u"LGX")
                    elif cur_k <= 55 and cur_d <= 55 and current_price < middle and cur_d >= cur_d1:  # 中位金叉,且未出中轨
                        logging.warning(u"KDJ MGX, k1={}, k={}, d1={}, d={}, cp={}, upper={}, curk2={}, last_diff_kd2={}".format(cur_k1, cur_k, cur_d1, cur_d, current_price, upper, cur_k2, last_diff_kd2))
                        buy_percent += 0.12
                        strategy_flag.append(u"MGX")
                else:
                    logger.info(u"没有趋近金叉, k1={}, k={}, d1={}, d={}, last_diff_kd={}, diff_kd={}, cp={}. curk2={}, last_diff_kd2={}".format(cur_k1, cur_k, cur_d1, cur_d, last_diff_kd, diff_kd, current_price, cur_k2, last_diff_kd2))

                # 低位回弹
                # kd不能大于40
                limit_kd = 40*config.RISK

                # 如果当前持仓比低于用户预设的值，则降低买入门槛，尽快达到用户要求的持仓比, 否则升高买入标准
                # position, buy_factor, sell_factor = get_current_position()
                # if position > 0:
                #     limit_kd /= buy_factor

                # 如果最近15分钟已经买过，则提高买入门槛
                # already = is_already_buy()
                # if already[0]:
                #     limit_kd /= already[1]

                limit_kd = 15 if limit_kd < 15 else limit_kd
                limit_kd = 35 if limit_kd > 35 else limit_kd
                now = int(time.time()) * 1000
                min_price = get_min_price(symbol, last_time=now - (15 * 60 * 1000))
                actual_up_percent = 0

                if cur_k <= limit_kd or cur_d <= limit_kd:
                    # 回暖幅度超过0.008
                    up_percent = kdj_buy_params.get("up_percent", 0.003)
                    up_percent *= (1/config.RISK)

                    # 如果当前持仓比低于用户预设的值，则降低买入门槛，尽快达到用户要求的持仓比
                    # if position > 0:
                    #     up_percent *= buy_factor
                    #
                    # if already[0]:
                    #     up_percent *= already[1]

                    if min_price and min_price > 0:
                        actual_up_percent = round((current_price - min_price) / min_price, 4)
                        logger.info("kdj buy min_price={}, current_price={},  need up_percent={} actual up_percent = {}".format(min_price,
                                                                                                                                current_price,
                                                                                                                                up_percent,
                                                                                                                                actual_up_percent))
                        if actual_up_percent >= up_percent:
                            logger.info("kdj buy actual_up_percent{} big than need up_percent{}.".format(actual_up_percent, up_percent))
                            # 最近三个周期内出现过kd小于20
                            last_k, last_d, last_j = get_kdj(market, 1)
                            last_k_2, last_d_2, last_j_2 = get_kdj(market, 2)
                            need_k = kdj_buy_params.get("k", 22)*config.RISK*(actual_up_percent/up_percent) # 回弹幅度越大，自然kd值也会变大，需要放宽限制条件
                            need_d = kdj_buy_params.get("d", 22)*config.RISK*(actual_up_percent/up_percent) # 回弹幅度越大，自然kd值也会变大，需要放宽限制条件

                            # 如果当前持仓比低于用户预设的值，则降低买入门槛，尽快达到用户要求的持仓比
                            # if position > 0:
                            #     need_k /= buy_factor
                            #     need_d /= buy_factor
                            #
                            # # 是否买过了
                            # if already[0]:
                            #     need_k /= already[1]
                            #     need_d /= already[1]

                            need_k = 16 if need_k < 16 else need_k
                            need_d = 14 if need_d < 14 else need_d
                            need_k = 26 if need_k > 25 else need_k
                            need_d = 24 if need_d > 24 else need_d
                            logger.info("kdj buy, need_k={}, need_d={}, cur_k={} cur_d={}, lk1={} ld1={} lk2={} ld2={}".format(need_k, need_d, cur_k, cur_d, last_k, last_d, last_k_2, last_d_2))

                            # if (cur_k <= need_k and cur_d <= need_d) \
                            #         or (last_k <= need_k and last_d <= need_d) \
                            #         or (last_k_2 <= need_k and last_d_2 <= need_d):

                            if (last_k <= need_k and last_d <= need_d and cur_k > last_k) or (cur_k<15 and cur_d<15 and (cur_k-cur_d)>-5) or (last_k_2<need_k and last_d_2<need_d):
                                if cur_k-cur_d > 0:
                                    logging.warning(u"KDJ LB, k={}, d={}, k1={}, d1={}, cp={}, upp={}".format(cur_k, cur_d, last_k, last_d, current_price, actual_up_percent))

                                    buy_percent += kdj_buy_params.get("buy_percent", 0.2)

                                    if cur_k < 20:
                                        logger.info("kdj lb curk<20")
                                        buy_percent += (20-cur_k)/100

                                    strategy_flag.append(u"LB")
                                    ret = is_buy_big_than_sell(symbol, 2)
                                    if ret:
                                        logger.info("is_buy_big_than_sell return True")
                                        log_config.output2ui("is_buy_big_than_sell return True")
                                        buy_percent += 0.05
                                        strategy_flag.append(u"BA")
                        else:
                            logger.info("kdj buy actual_up_percent={}<limit_up_percent={}".format(actual_up_percent, up_percent))

                else:
                    logger.info("kdj buy, curk={}, curd={}>limit_kd={}".format(cur_k, cur_d, limit_kd))

                if buy_percent <= 0:
                    return False

                if is_still_down2(current_price, min_price):
                    logger.info("kdj buy still down")
                    return False

                buy_percent *= config.RISK

                msg = "[买入{}]KD 计划买入比例={}%, 买入价格={}, 指标K={}, D={}".format(
                    symbol, round(buy_percent * 100, 2), round(current_price, 6), round(cur_k, 2), round(cur_d, 2))

                if not trade_alarm(msg):
                    return False
                trade_mode = config.TRADE_MODE_CONFIG.get(config.TRADE_MODE, {})
                plan_buy_amount = principal*trade_mode.get("first_trade", 0.05)

                ret = buy_market(symbol, amount=plan_buy_amount, currency=money.lower())
                if ret.get("code", 0) == 1:
                    detail = ret.get("data", {})
                    field_amount = detail.get("field_amount", 0)                # 币
                    field_cash_amount = detail.get("field_cash_amount", 0)      # 金
                    fees = detail.get("fees", 0)
                    msg = "[建仓{}] 实际买入币量： {}, 实际买入金额: {}, 买入价格: {}".format(symbol.upper(), round(field_amount, 6), round(field_cash_amount, 6), round(current_price, 6))
                    log_config.output2ui(msg, 4)
                    logger.warning(msg)
                    log_config.notify_user(msg, own=True)

                    time_now = datetime.now()
                    trade = {
                        "buy_type": "auto",  # 买入模式：auto 自动买入(机器策略买入)，man手动买入,
                        "sell_type": "profit",
                        # 要求的卖出模式，机器买入的一般都为止盈卖出。可选：sell_profit 止盈卖出（默认）， sell_no-不要卖出，针对手动买入的单，sell_smart-使用高抛，kdj等策略卖出
                        "limit_profit": 0,  # 大于零代表要求必须盈利,否则由系统智能卖出
                        "back_profit": 0,  # 追踪回撤系数
                        "buy_time": time_now,
                        "sell_time": None,
                        "coin": coin,
                        "money": money,
                        "amount": field_amount,  # 买入或卖出的币量
                        "buy_price": current_price,  # 实际买入成交的价格
                        "cost": field_cash_amount,  # 实际花费的计价货币量
                        "is_sell": 0,  # 是否已经卖出
                        "sell_price": 0,  # 实际卖出的价格
                        "profit_percent": 0,  # 盈利比，卖出价格相对于买入价格
                        "profit": 0,  # 盈利额，只有卖出后才有
                    }

                    trade_group = {
                        "trigger_reason": "KDJ",    # 首单触发原因，如kdj/boll/low
                        "mode": "",           # 按何种交易风格执行
                        "coin": coin,
                        "money": money,
                        "trades": [trade],            # 每一次交易记录，
                        "grid": -1,                 # 是否开启网格交易
                        "amount": field_amount,         # 持仓数量（币）
                        "cost": field_cash_amount,           # 持仓费用（计价货币）
                        "max_cost": field_cash_amount,
                        "avg_price": current_price,      # 持仓均价
                        "profit": 0,                #这组策略的总收益， 每次卖出后都进行累加
                        "profit_percent": 0,        # 整体盈利比（整体盈利比，当前价格相对于持仓均价,）
                        "last_profit_percent": 0,   # 尾单盈利比（最后一单的盈利比）
                        "limit_profit": 0,   # 止盈比例
                        "back_profit": 0,    # 追踪比例
                        "track": -1,
                        "buy_counts": 1,           # 已建单数，目前处理买入状态的单数
                        "sell_counts": 0,          # 卖出单数，卖出的次数，其实就是尾单收割次数
                        "patch_index": 0,
                        "patch_ref": 0,         # 间隔参考
                        "last_buy_price": current_price,    # 最后一次买入价格，用来做网格交易，如果最后一单已经卖出，则这个价格需要变成倒数第二次买入价格，以便循环做尾单
                        "start_time": time_now,
                        "end_time": None,
                        "last_update": time_now,
                        "uri": "{}{}".format(time_now.strftime("%Y%m%d%H%M%S"), random.randint(100, 999)),
                        "principal": 0,
                        "is_sell": 0,
                        "user": config.CURRENT_ACCOUNT
                        }
                    #把最新插在最前面
                    config.TRADE_RECORDS_NOW.insert(0, trade_group)

    return buy_in


def is_already_buy_first(symbol):
    for grp in config.TRADE_RECORDS_NOW:
        if not grp.get("end_time", None):
            already_symbol = "{}{}".format(grp.get("coin", ""), grp.get("money", "")).lower()
            if already_symbol == symbol:
                return True
    return False


def kdj_strategy_sell(currency=[], max_trade=1):
    if kdj_sell_params.get("check", 1) != 1:
        log_config.output2ui("kdj_sell is not check", 2)
        return False

    period = kdj_sell_params.get("period", "15min")
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], period)
    symbol = config.NEED_TOBE_SUB_SYMBOL[0]

    # if is_still_up(symbol):
    #     logging.info("kdj sell checking, still up!")
    #     return False

    current_price = get_current_price(symbol)
    # if TRADE_RECORD:

    cur_k, cur_d, cur_j = get_kdj(market)

    limit_diff_kd = 5 - (config.RISK-1)*5
    diff_kd = cur_k - cur_d

    entry_msg = "kdj_strategy_sell period={}, current k={}, d={}, current_price={}, actural diff_kd={}, limit diff_kd={}"\
        .format(period, cur_k, cur_d, current_price, diff_kd, limit_diff_kd)
    logger.info(entry_msg)
    log_config.output2ui(entry_msg)

    # kd要大于50
    limit_kd = 50 * config.RISK

    # 如果最近15分钟已经卖出过，则提高卖出门槛
    already = is_already_sell()
    if already[0]:
        limit_kd *= already[1]

    # 如果当前持仓比低于用户预设的值，则提高卖出门槛，保证仓位
    position, buy_factor, sell_factor = get_current_position()
    if position > 0:
        if sell_factor == 0:
            logger.warning("kdj_strategy_sell be cancelled. force lock.")
            return False

        limit_kd += (sell_factor-1)*limit_kd/2

    limit_kd = 35 if limit_kd < 35 else limit_kd
    limit_kd = 90 if limit_kd > 90 else limit_kd
    if cur_k < limit_kd or cur_d < limit_kd or cur_k-cur_d > 1:
        logger.info("cur_k={} or cur_d={} < {}".format(cur_k, cur_d, limit_kd))
        return False

    cur_k1, cur_d1, cur_j1 = get_kdj(market, pos=1)
    diff_kd1 = cur_k1 - cur_d1
    # kd是差距是否在缩小，其至死叉
    if diff_kd > limit_diff_kd:
        logger.info(u"kd的差距未小于指定值，暂不卖出．　diff_kd {} > limit_diff_kd {},  curk={}, curd={}".format(diff_kd, limit_diff_kd, cur_k, cur_d))
        return False

    if diff_kd > diff_kd1:
        logger.info(u"kdj在高位的差距相比上个周期没有缩小，暂不卖出． diff_kd={} > diff_kd1={}, curk={}, curd={}".format(diff_kd, diff_kd1, cur_k, cur_d))
        return False

    now = int(time.time()) * 1000
    max_price = get_max_price(symbol, last_time=now - (15 * 60 * 1000))
    if not max_price or max_price <= 0:
        return False

    #回撤超过0.005
    down_percent = kdj_sell_params.get("down_percent", 0.005)*config.RISK
    if already[0]:
        down_percent *= already[1]

    if position:
        down_percent *= sell_factor

    down_percent = 0.02 if down_percent > 0.02 else down_percent
    down_percent = 0.001 if down_percent < 0.001 else down_percent
    actual_down_percent = round((max_price - current_price) / max_price, 4)
    logger.info(
        "kdj sell max_price={}, current_price={}, need down_percent={}, actual_down_percent={}".format(max_price,
                                                                                                       current_price,
                                                                                                       down_percent,
                                                                                                       actual_down_percent))
    if actual_down_percent < down_percent:
        logger.info("kdj_sell 回撤幅度不足, need down_percent={}, actual_down_percent={}".format(down_percent, actual_down_percent))
        return False

    # 最近三个周期内出现过kd大于80
    last_k, last_d, last_j = get_kdj(market, 1)
    last_k_2, last_d_2, last_j_2 = get_kdj(market, 2)

    need_k = kdj_sell_params.get("k", 82)
    need_k += (config.RISK-1)*(100-need_k)

    need_d = kdj_sell_params.get("d", 78)
    need_d += (config.RISK-1)*(100-need_d)

    # 根据是否买卖过来调整kd
    if already[0]:
        need_k += (already[1]-1) * need_k
        need_d += (already[1]-1) * need_d

    # 根据仓位调整kd的高低
    if position > 0:
        need_k += (sell_factor-1) * (100-need_k)
        need_d += (sell_factor-1) * (100-need_d)

    # need_k = 95 if need_k > 95 else need_k
    # need_d = 85 if need_d > 85 else need_d
    # need_k = 75 if need_k < 75 else need_k
    # need_d = 72 if need_d < 72 else need_d

    if (cur_k >= need_d and cur_d >= need_d) \
            or (last_k >= need_k and last_d >= need_d) \
            or (last_k_2 >= need_k and last_d_2 >= need_d):

        if is_still_up2(current_price, max_price):
            logger.info("kdj sell, still up")
            return False
        else:
            logger.info("kdj sell, not still up ")

        percent = kdj_sell_params.get("sell_percent", 0.3)
        percent *= config.RISK

        msg_show = "[卖出{}]KD 卖出比例={}%, 卖出价格={}, 阶段最高价格={}, 回撤幅度={}%, 指标K={}, D={}．".format(
            symbol, round(percent * 100, 2), round(current_price, 6), round(max_price, 6),
            round(actual_down_percent * 100, 2), round(cur_k, 2), round(cur_d, 2), )

        if not trade_alarm(msg_show):
            return False

        ret = sell_market(symbol, percent=percent, current_price=current_price)
        if ret[0]:
            msg = "[卖出{}]KD 计划卖出比例={}%, 实际卖出数量={}个, 卖出价格={}, 阶段最高价格={}, 回撤幅度={}%, 指标K={}, D={}.".format(
                symbol, round(percent * 100, 2), round(ret[1], 3), round(current_price, 6), round(max_price, 6),
                round(actual_down_percent * 100, 2), round(cur_k, 2), round(cur_d, 2), )

            success = False
            if ret[0] == 1:
                msg += "-交易成功！"
                success = True
            elif ret[0] == 2:
                msg += "-交易被取消, 取消原因: {}!".format(ret[2])
            elif ret[0] == 3:
                msg += "-交易失败, 失败原因: {}！".format(ret[2])

            log_config.output2ui(msg, 7)
            logger.warning(msg)
            log_config.notify_user(msg, own=True)
            log_config.notify_user(log_config.make_msg(1, symbol, current_price=current_price, percent=percent))
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
        logger.warning("stop loss is not check")
        return False

    #最近10分钟内有买入策略被触发，则暂时不卖
    already = is_already_buy(last_time=int(time.time()) * 1000 - 10 * 60 * 1000)
    if already[0]:
        logger.info(u"最近十分钟有买入, 暂不止损．")
        return False

    # 根据仓位调整止损比例
    position, buy_factor, sell_factor = get_current_position()
    if position > 0:
        if sell_factor == 0:
            logger.warning("stop_loss be cancelled, lock postion")
            return False

    precision = 0.000000001
    trigger = False
    for trade in BUY_RECORD:
        last_buy_amount = float(trade.get("field-amount", 0))
        last_time = trade.get('created-at', 0)
        last_price = float(trade.get("price", 0))
        if last_price < precision and last_buy_amount > 0:
            last_price = float(trade.get('field-cash-amount', 0)) / last_buy_amount

        if last_buy_amount <= precision or last_price <= precision:
            continue

        symbol = trade.get("symbol")
        current_price = get_current_price(symbol)

        loss_percent = (last_price - current_price) / last_price
        limit_loss = stop_loss_params["percent"]*config.RISK
        limit_loss = 0.1 if limit_loss > 0.1 else limit_loss    #再激进也不能亏10个点都不止损

        # 如果仓位已经很低了，提高止损门槛
        limit_loss *= sell_factor

        if loss_percent >= limit_loss:
            msg = "[SELL] stop loss execute, sell {}, loss percent={}, config loss percent={}, last_buy_price={}, last_buy_amount={}, current_price={}".format(
                    symbol, loss_percent, limit_loss, last_price, last_buy_amount, current_price)
            if not trade_alarm(msg):
                return False

            logger.info(
                "stop loss execute, loss percent={}, config loss percent={}, last_buy_price={}, last_buy_amount={}, current_price={}".format(
                    loss_percent, limit_loss, last_price, last_buy_amount, current_price))
            log_config.output2ui(
                "stop loss execute, loss percent={}, config loss percent={}, last_buy_price={}, last_buy_amount={}, current_price={}".format(
                    loss_percent, limit_loss, last_price, last_buy_amount, current_price))

            ret = sell_market(symbol, last_buy_amount, current_price=current_price)
            if ret[0]:
                BUY_RECORD.remove(trade)
                trigger = True
                logger.info(
                    "stop_loss sell {} amount={}, last buy price={}, current price={}, loss_percent={}".format(
                        symbol, last_buy_amount, last_price,
                        current_price, loss_percent))

                msg = "[卖出{}]MSL 计划卖出量={}个, 实际卖出量={}个, 之前买入价={}$, 当前卖出价={}$, 损失比例={}%.".format(
                        symbol, round(last_buy_amount, 3), round(ret[1], 3), round(last_price, 6),
                        round(current_price, 6), round(loss_percent*100, 2))

                if ret[0] == 1:
                    msg += "-交易成功！"
                elif ret[0] == 2:
                    msg += "-交易被取消, 取消原因: {}!".format(ret[2])
                elif ret[0] == 3:
                    msg += "-交易失败, 失败原因: {}！".format(ret[2])

                log_config.output2ui(msg, 7)
                logger.warning(msg)
                log_config.notify_user(msg, own=True)
                log_config.notify_user(log_config.make_msg(1, symbol, current_price=current_price))

    return trigger


def move_stop_profit():
    """
    移动止盈，根据之前的买入记录来卖出
    :return:
    """
    # market = "market.ethusdt.kline.15min"
    precision = 0.00001
    logger.info("move_stop_profit checking params={}".format(move_stop_profit_params))
    log_config.output2ui("move_stop_profit checking params={}".format(move_stop_profit_params))
    if move_stop_profit_params.get("check", 1) != 1:
        log_config.output2ui("move_stop_profit is not check", 2)
        return False

    trigger = False

    # 根据当前仓位动态调整买入卖出的难度系数
    position, buy_factor, sell_factor = get_current_position()
    if position > 0:
        if sell_factor == 0:
            # 当前仓位小于用户指定的最低仓位，　强制锁仓，　不卖
            logger.warning("move_stop_profit have been cancelled. sell_factor=0")
            return False

    # 获取布林的上轨，当前价格突破上轨后，降低卖出难度，尽快卖出
    period = boll_strategy_params.get("period", "15min")
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], period)
    upper, middle, lower = get_boll(market, 0)

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

        # 上涨需要超过两个点才止盈
        max_upper = (max_price-last_price)/last_price
        limit_max_upper = config.RISK*move_stop_profit_params.get("msf_min", 0.02)

        # 根据当前仓位，动态调整卖出门槛
        if position > 0:
            limit_max_upper *= sell_factor

        # 最少盈利超过1.5个点
        limit_max_upper = 0.015 if limit_max_upper < 0.015 else limit_max_upper
        logger.info("move_stop_profit, profit upper={}, msf_min={}".format(max_upper, limit_max_upper))

        if max_upper < limit_max_upper:
            continue

        # 当前回撤幅度
        down_back_percent = round((max_price - current_price) / (max_price - last_price), 5)

        # 回撤幅度超过25％（涨幅在2个点以内的）, 如果超过两个点，则要求回撤幅度需要缩小，以保证更多的盈利, 激进者可以承受更大的风险
        limit_down_back_percent = move_stop_profit_params.get("msf_back", 0.20) * (0.02/max_upper) * config.RISK

        logger.info(
            "[check]move_stop_profit last_price={}, max_price={}, current_price={}, max_upper={}, dbp={}, last_buy={}, limit_msf_back={}, upper={}".format(
                last_price, max_price, current_price, max_upper, down_back_percent, last_buy_amount, limit_down_back_percent, upper))

        # 判断当前价格有没有超过上轨，如果超过了，则认为在危险区域，需要更快的卖出，如果没有超过，则相对安全，可以容忍更大的回撤幅度
        if upper > 0:
            if max_price > upper*1.01:
                # 超过的越多，越危险, 可容忍的回撤幅度越低，这样可以在更高的价格卖出
                limit_down_back_percent_old = limit_down_back_percent
                factor = 1 - ((max_price - upper) / upper * 5)
                limit_down_back_percent *= factor
                logger.info(
                    "max price>upper*1.01, max={}, upper={}, ldb={}, ldb_new={} factor={}".format(max_price, upper,
                                                                                                  limit_down_back_percent_old, limit_down_back_percent,
                                                                                                  factor))
            else:
                # 这样可以避免被洗盘洗出来
                limit_down_back_percent_old = limit_down_back_percent
                factor = 1 + ((upper-max_price)/max_price * 2)
                limit_down_back_percent *= factor
                logger.info(
                    "max price<upper*1.01, max={}, upper={}, ldb={}, ldb_new={} factor={}".format(max_price, upper,
                                                                                                  limit_down_back_percent_old,
                                                                                                  limit_down_back_percent,
                                                                                                  factor))

        # 最多允许回撤一半, 最小回撤5个点
        limit_down_back_percent = 0.10 if limit_down_back_percent < 0.10 else limit_down_back_percent
        limit_down_back_percent = 0.30 if limit_down_back_percent > 0.30 else limit_down_back_percent
        logger.info("move_stop_profit limit_down_back_percent={}, down_back_percent={}".format(limit_down_back_percent, down_back_percent))
        if down_back_percent < limit_down_back_percent:
            continue

        # 当前盈利
        profit = (current_price-last_price)/last_price
        # 盈利小于１个点不卖
        limit_profit = 0.013*config.RISK
        limit_profit *= sell_factor
        limit_profit = 0.01 if limit_profit < 0.01 else limit_profit
        if profit < limit_profit:
            logger.info("Move stop profit  profit{} less than limit profit({})".format(profit, limit_profit))
            continue

        profit = round(profit*100, 2)
        msg = "[SELL]Move stop profit be trigger sell {},  current price={}, last_price={}, max_price={} max_upper={}, profit={}% down_back_percent={}%".format(
                    symbol, current_price, last_price, max_price, max_upper, profit, down_back_percent)
        if not trade_alarm(msg):
            continue

        bal = get_balance(config.SUB_LEFT, result_type=0)
        if bal and float(bal) <= last_buy_amount:
            last_buy_amount = round(float(bal)*0.98, 3)

        logger.warning("[msp_sell]move_stop_profit last_price={}, max_price={}, current_price={}, down_back_percent={}, last_buy_amount={}, profit={}%".format(
                last_price, max_price, current_price, down_back_percent, last_buy_amount, profit))

        ret = sell_market(symbol, last_buy_amount, current_price=current_price)
        if ret[0]:
            trigger = True
            BUY_RECORD.remove(trade)
            msg = "[卖出{}]MSP： 上次买入价={}, 最高价={}, 回撤幅度={}%, 当前卖出价={}, 计划卖出量={}个, 实际卖出量={}个, 盈利比={}%, 盈利金额={}$.".format(symbol,
                                                                                                               round(
                                                                                                                   last_price,
                                                                                                                   6),
                                                                                                               round(
                                                                                                                   max_price,
                                                                                                                   6),
                                                                                                               round(
                                                                                                                   down_back_percent * 100,
                                                                                                                   2),
                                                                                                               round(
                                                                                                                   current_price,
                                                                                                                   6),
                                                                                                               round(
                                                                                                                   last_buy_amount,
                                                                                                                   3),
                                                                                                                round(
                                                                                                                   ret[1],
                                                                                                                   3),
                                                                                                               round(
                                                                                                                   profit,
                                                                                                                   2),
                                                                                                               round(
                                                                                                                   last_buy_amount * (
                                                                                                                               current_price - last_price),
                                                                                                                   3))

            if ret[0] == 1:
                msg += "-交易成功！"
            elif ret[0] == 2:
                msg += "-交易被取消, 取消原因: {}!".format(ret[2])
            elif ret[0] == 3:
                msg += "-交易失败, 失败原因: {}！".format(ret[2])

            log_config.output2ui(msg, 7)
            logger.warning(msg)
            log_config.notify_user(msg, own=True)
            log_config.notify_user(log_config.make_msg(1, symbol, current_price=current_price, last_price=last_price))

    return trigger


def vol_price_fly():
    if vol_price_fly_params.get("check", 1) != 1:
        log_config.output2ui("vol price fily is not check", 2)
        return False

    period = vol_price_fly_params.get("period", "5min")
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], period)
    symbol = market.split(".")[1]
    multiple = vol_price_fly_params.get("vol_percent", 1.2) * (1/config.RISK)
    mul_21 = 1.1

    # 根据当前仓位动态调整买入卖出的难度系数
    position, buy_factor, sell_factor = get_current_position()
    if position > 0:
        multiple *= buy_factor
        mul_21 *= buy_factor

    peroid_5min = 1
    if period == "5min":
        peroid_5min = 1
    elif period == "15min":
        peroid_5min = 3
    # elif period == "30min":
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
    high_than_last = vol_price_fly_params.get("high_than_last", 2) * (1/config.RISK)
    local_21 = get_trade_vol_from_local(symbol, 3, 7).get("trade_vol", 0)
    if not all([last_peroid_0, last_peroid_1, last_peroid_2, local_21]):
        return False

    if not last_peroid_0 >= last_peroid_1*high_than_last or not last_peroid_1>=high_than_last*last_peroid_2:
        logger.info("current vol not bigger than {}*last vol. current trade vol={}, last vol={}".format(high_than_last, last_peroid_0, last_peroid_1))
        return False

    last_peroid_21 = local_21 / 7
    if not last_peroid_0 >= mul_21*last_peroid_21:
        logger.info("current vol not bigger than 1.1*last vollast_peroid_21. current trade vol={}, last_peroid_21={}".format(last_peroid_0, last_peroid_21))
        return False

    logger.info("vol_price_fly last_peroid_0={}, last_peroid_1={}, last_peroid_2={}, last_peroid_21={}, high_than_last={}".format(last_peroid_0, last_peroid_1, last_peroid_2, last_peroid_21, high_than_last))

    # 当前价格不能超过前面第三个周期的收盘价*（1+规定涨幅）
    current_price = get_current_price(symbol)
    close_before_2 = (get_close(market, before=3) + get_close(market, before=4) + get_close(market, before=5))/3
    if close_before_2 < 0:
        return False

    # close_before1 = get_close(market, before=1)
    logger.info("vol_price_fly current_price={} , close_before_2={}, * 1+price_up_limit= {}".format(current_price,
                                                                                                    close_before_2,
                                                                                                    vol_price_fly_params[
                                                                                                        "price_up_limit"]))
    log_config.output2ui(
        "vol_price_fly current_price={}, close_before_2={} * 1+price_up_limit{}".format(current_price, close_before_2,
                                                                                        vol_price_fly_params[
                                                                                            "price_up_limit"]))

    if (current_price > close_before_2 * (1 + vol_price_fly_params.get("price_up_limit", 0.02)*config.RISK)):
        logger.info("vol_price_fly current_price={} > close_before_2={} * {}".format(current_price, close_before_2,
                                                                                     1 + vol_price_fly_params.get(
                                                                                         "price_up_limit", 0.02)))
        log_config.output2ui(
            "vol_price_fly current_price={} > close_before_2={} * {}".format(current_price, close_before_2,
                                                                             1 + vol_price_fly_params.get(
                                                                                 "price_up_limit", 0.02)))
        return False

    if current_price < close_before_2:
        logger.info("current_price={} < close_before_2={} ".format(current_price, close_before_2))
        log_config.output2ui("current_price={} < close_before_2={} ".format(current_price, close_before_2))
        return False

    if current_price < get_open(market, before=1):
        return False

    percent = vol_price_fly_params["buy_percent"]
    percent *= config.RISK
    msg = "[BUY]vol_price_fly buy {} percent={}, current price={}".format(symbol, percent, current_price)
    if not trade_alarm(msg):
        return False

    ret = buy_market(symbol, percent=percent, strategy_type="vol_price_fly", current_price=current_price)
    if ret[0]:
        msg = "[买入{}]VPF, 计划买入比例={}%, 实际买入金额={}$, 买入价格={}.".format(symbol, round(percent*100, 2), round(ret[1],2), round(current_price, 6))

        success = False
        if ret[0] == 1:
            msg += "-交易成功！"
            success = True
        elif ret[0] == 2:
            msg += "-交易被取消, 取消原因: {}!".format(ret[2])
        elif ret[0] == 3:
            msg += "-交易失败, 失败原因: {}！".format(ret[2])

        log_config.output2ui(msg, 6)
        logger.warning(msg)
        log_config.notify_user(msg, own=True)
        log_config.notify_user(log_config.make_msg(0, symbol, current_price=current_price, percent=percent))
        return True
    return False


def trade_alarm(message, show_time=0):
    return True
    if not config.ALARM_NOTIFY:
        return True

    logger.warning("Trade Alarm: {}".format(message))
    if show_time > 0:
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


def buy_market(symbol, amount, percent=0.1, currency=""):
    # 按余额比例买
    result = {"code": 0, "data": {}, "msg": ""}
    balance = 0
    # 如果提供了计价货币，则根据余额来检验amount
    if symbol[-4:].lower() == "usdt" and config.TRADE_MIN_LIMIT_VALUE > 0 and amount < config.TRADE_MIN_LIMIT_VALUE:
        log_config.output2ui(u"[{}]当前计划买入价值({})小于设置的最小买入额({} USDT), 直接调整为最小买入限额".format(symbol.upper(), amount, config.TRADE_MIN_LIMIT_VALUE))
        amount = config.TRADE_MIN_LIMIT_VALUE

    if symbol[-4:].lower() == "usdt" and config.TRADE_MAX_LIMIT_VALUE>0 and amount > config.TRADE_MAX_LIMIT_VALUE:
        log_config.output2ui(u"[{}]当前计划买入价值({})大于设置的最大买入额({} USDT), 直接调整为最大买入限额".format(symbol.upper(), amount, config.TRADE_MAX_LIMIT_VALUE))
        amount = config.TRADE_MAX_LIMIT_VALUE

    if currency:
        balance = get_balance(currency)
        if amount <= 0:
            if percent > 0:
                if balance and balance > 0:
                    amount = round(balance * percent, 6)
                else:
                    result["msg"] = "Have no balance for buying."
                    return result
            else:
                result["msg"] = "buy amount and percent less than zero."
                return result
        else:
            if amount >= balance:
                # 余额不足
                log_config.output2ui(u"[{}]买入时余额不足, 计划买入: {}, 余额: {}, 将按照余额数买入！".format(symbol.upper(), round(amount, 4), round(balance, 4)), 2)
                amount = balance

    # 市价amount代表买多少钱的
    amount = format_float(amount, 6)
    logger.warning("buy {} amount={}, balance={}".format(symbol, amount, balance))

    hrs = HuobiREST()
    retry = 6
    while retry >= 0:
        ret = hrs.send_order(amount=amount, source="api", symbol=symbol, _type="buy-market")
        if ret[0] == 200 and ret[1]:
            logger.info("buy market success, symbol={}, amount={}".format(symbol, amount))
            order_id = ret[1]
            order_response = hrs.order_info(order_id)
            # (200, {'status': 'ok',
            #        'data': {'id': 6766866273, 'symbol': 'ethusdt', 'account-id': 4091798, 'amount': '1.000000000000000000',
            #                 'price': '0.0', 'created-at': 1530233353821, 'type': 'buy-market',
            #                 'field-amount': '0.002364960741651688', 'field-cash-amount': '0.999999999999999753',
            #                 'field-fees': '0.000004729921483303', 'finished-at': 1530233354117, 'source': 'api',
            #                 'state': 'filled', 'canceled-at': 0}})
            if order_response[0] == 200 and order_response[1].get("status", "") == config.STATUS_OK:
                order_detail = order_response[1].get("data", {})
                amount = float(order_detail.get("amount", amount))
                field_cash_amount = float(order_detail.get("field-cash-amount", 0))   # 成交金额
                field_amount = float(order_detail.get("field-amount", 0))   #买入币量
                fees = float(order_detail.get("field-fees", 0))
                # price = float(order_detail.get("price", 0))
                price = float(field_cash_amount/field_amount)

                logger.warning("[{}]买入成功, 计划买入额: {}, 实际成交额: {}, 实际买入币量: {}, 买入价格: {}".format(symbol, round(amount, 6), round(field_cash_amount, 6), round(field_amount, 6), round(price, 6)))

                # 买入时买哪个币就是收你千分之二的那个币
                result["code"] = 1
                result["data"] = {
                    "symbol": symbol,
                    "amount": amount,
                    "field_cash_amount": field_cash_amount,
                    "field_amount": field_amount,
                    "finished_at": order_detail.get("finished-at", ""),
                    "price": price,
                    "fees": fees
                }
                result["msg"] = "Buy succeed!"
                update_balance(money_only=True)
                return result
        elif ret[0] == 200:
            #精度有问题，可以降低精度再试试
            amount = format_float(amount, retry-1)
            retry -= 1
        else:
            break

    logger.error("buy market failed, symbol={}, amount={}, ret={}".format(symbol, amount, ret))
    log_config.output2ui("[{}]买入失败, 计划买入币量: {}".format(symbol.upper(), amount), 2)
    result["code"] = 0
    result["msg"] = "Trade buy failed!"
    return result


def sell_market(symbol, amount, percent=0.1, currency=""):
    result = {"code": 0, "data": {}, "msg": ""}
    balance = 0
    #如果提供了计价货币，则根据余额来检验amount
    if currency:
        balance = get_balance(currency)
        if amount <= 0:
            if percent > 0:
                if balance and balance > 0:
                    amount = round(balance * percent, 6)
                else:
                    result['msg'] = "Have no balance for selling."
                    return result
            else:
                result["msg"] = "sell percent less than zero."
                return result
        else:
            # 余额不足
            if amount >= balance:
                log_config.output2ui(u"[{}]卖出时余币不足, 计划卖出: {}, 余币: {}, 将按照余币数卖出！".format(symbol.upper(), amount, balance), 2)
                amount = balance

    # if currency.lower() in ["btc", "eth", "bch", "bsv", "dash", "ltc", "zec", "xmr", "dcr", "neo", "etc", "eos", "qtum"]:
    #     amount = format_float(amount, 4)
    # else:
    #     amount = format_float(amount, 2)

    amount = format_float(amount, 6)
    logger.warning("sell {} amount={}, balance={}".format(symbol, amount, balance))

    # 卖出时amount代表币量

    hrs = HuobiREST()
    retry = 6
    while retry >= 0:
        ret = hrs.send_order(amount=amount, source="api", symbol=symbol, _type="sell-market")
        # (True, '6766866273')
        if ret[0] == 200 and ret[1]:
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
            if order_response[0] == 200 and order_response[1].get("status", "") == config.STATUS_OK:
                order_detail = order_response[1].get("data", {})
                amount = float(order_detail.get("amount", amount))
                field_cash_amount = float(order_detail.get("field-cash-amount", 0))   # 成交金额
                field_amount = float(order_detail.get("field-amount", 0))   #卖出币量
                fees = float(order_detail.get("field-fees", 0))
                # price = float(order_detail.get("price", 0))
                price = float(field_cash_amount / field_amount)

                # price = current_price if price == 0 else price

                logger.warning(
                    "[{}]卖出成功, 计划卖出币量: {}, 实际成交币量: {}, 实际成交金额: {}, 卖出价格: {}".format(symbol,
                                                                                           round(amount, 6),
                                                                                           round(field_amount, 6),
                                                                                           round(field_cash_amount, 6),
                                                                                           round(price, 6)))

                result["code"] = 1
                # 卖出时，你得到了哪种计价货币，就扣你千分之二的这种货币
                result["data"] = {
                    "symbol": symbol,
                    "amount": amount,
                    "field_cash_amount": field_cash_amount,
                    "field_amount": field_amount,
                    "finished_at": order_detail.get("finished-at", ""),
                    "price": price,
                    "fees": fees
                }
                result["msg"] = "Sell succeed!"
                update_balance(money_only=True)
                return result
        elif ret[0] == 200:
            # 精度有问题，可以降低精度再试试
            amount = format_float(amount, retry-1)
            if amount <= 0:
                break
            retry -= 1
        else:
            break

    logger.error("sell market failed, symbol={}, amount={}, ret={}".format(symbol, amount, ret))
    log_config.output2ui("[{}]卖出失败, 计划卖出币量: {}．".format(symbol.upper(), amount), 2)
    result["code"] = 0
    result["msg"] = "Trade sell failed!"
    return result


# pos--0 代表实时价，1--代表上一次收盘价
def get_close(market, before=1):
    try:
        process.data_lock.acquire()
        df = process.KLINE_DATA.get(market, None)
        if df is None:
            logger.error("get_close -1, market={}, before={}".format(market, before))
            return -1

        try:
            # print(len(df))
            close = df.loc[len(df) - 1 - before, "close"]
        except Exception as e:
            logger.exception("get_close, e={}".format(e))
            print(len(df))
            close = df.loc[len(df) - 1 - before - 1, "close"]
        return close
    except:
        logger.exception("get_close, ")
    finally:
        process.data_lock.release()



def get_open(market, before=1):
    try:
        process.data_lock.acquire()
        df = process.KLINE_DATA.get(market, None)
        if df is None:
            logger.error("get_open -1, market={}, before={}".format(market, before))
            return -1

        try:
            open_price = df.loc[len(df) - 1 - before, "open"]
        except Exception as e:
            logger.exception("get_open, e={}".format(e))
            open_price = df.loc[len(df) - 1 - before - 1, "open"]
        return open_price
    except:
        logger.exception("get_open")
    finally:
        process.data_lock.release()

#获取涨跌幅
def get_up_down(market, before=1):
    try:
        process.data_lock.acquire()
        df = process.KLINE_DATA.get(market, None)
        if df is None:
            logger.error("get_up_down -1, market={}, before={}".format(market, before))
            return -1

        try:
            # print(len(df))
            open_price = df.loc[len(df) - before, "open"]
            close_price = df.loc[len(df) - before, "close"]
            up_down = round((close_price - open_price) / open_price, 4)
        except Exception as e:
            logger.exception("get_open")
            # print(len(df))
            open_price = df.loc[len(df) - 1 - before, "open"]
            close_price = df.loc[len(df) - 1 - before, "close"]
            up_down = round((close_price - open_price) / open_price, 4)
        logger.info("get_up_down = {}".format(up_down))
        return up_down
    except:
        logger.exception("get_up_down")
    finally:
        process.data_lock.release()


def get_current_price(symbol):
    try:
        process.data_lock.acquire()
        df = process.KLINE_DATA.get(symbol, None)
        if df is None:
            logger.warning("get_current_price failed.")
            return -1

        try:
            # price = df.loc[len(df) - 1, "close"]
            price = float(df.tail(1)["close"])
        except Exception as e:
            logger.exception("get_current_price e={}, len(df)={}".format(e, len(df)))
            price = df.loc[len(df) - 1 - 1, "close"]

        logger.info("get_current_price sysmbol={}, price={}".format(symbol, price))
        return price
    except:
        logger.exception("get_current_price")
    finally:
        process.data_lock.release()


def get_max_price(symbol, last_time, current=0):
    try:
        process.data_lock.acquire()
        df = process.KLINE_DATA.get(symbol, None)
        if df is None:
            return -1

        if isinstance(last_time, datetime):
            last_time = float(datetime.timestamp(last_time)*1000)

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
                try:
                    temp_df = df[["ts", "high"]][df.ts >= last_time]
                    temp_df = temp_df.loc[temp_df["ts"]<current]
                    max_price = temp_df.high.max()
                except:
                    max_price = -1
        else:
            try:
                max_price = df.loc[df["ts"] > last_time].high.max()
                if pd.isna(max_price):
                    max_price = df.loc[df["ts"] > last_time].close.max()
            except Exception as e:
                logger.exception("get_max_price catch e={}, last_time={}, current={}".format(e, last_time, current))
                try:
                    temp_df = df[["ts", "high"]][df.ts >= last_time]
                    max_price = temp_df.high.max()
                except:
                    max_price=-1

        logger.info("get_max_price, symbol={}, last time={}, current={}, max_price={}".format(symbol, last_time, current, max_price))
        if not max_price or pd.isna(max_price):
            return -1
        else:
            return max_price
    except:
        logger.exception("get_max_price")
    finally:
        process.data_lock.release()


def get_min_price(symbol, last_time, current=0):
    # 默认取五分钟之前往前的最低价格
    # current = ((int(time.time()) * 1000)-5*60*1000) if current <= 0 else current

    try:
        process.data_lock.acquire()
        df = process.KLINE_DATA.get(symbol, None)
        if df is None:
            return -1

        if current > 0:
            try:
                temp_df = df.loc[df["ts"] >= last_time]
                min_price = temp_df.loc[temp_df["ts"]<current].low.min()
                if pd.isna(min_price):
                    min_price = temp_df.loc[temp_df["ts"]<current].close.min()
            except Exception as e:
                logger.exception("get_min_price catch e={}, last_time={}, current={}".format(e, last_time, current))
                try:
                    temp_df = df[["ts", "low"]][df.ts >= last_time][df.ts < current]
                    min_price = temp_df.low.min()
                except:
                    min_price=-1

        else:
            try:
                min_price = df.loc[df["ts"] >= last_time].low.min()
                if pd.isna(min_price):
                    min_price = df.loc[df["ts"] >= last_time].close.min()
            except Exception as e:
                logger.exception("get_min_price catch e={}, last_time={}, current={}".format(e, last_time, current))
                try:
                    temp_df = df[["ts", "low"]][df.ts >= last_time]
                    min_price = temp_df.low.min()
                except:
                    min_price = -1

        logger.info("get_min_price, symbol={}, last time={}, current={}, min_price={}".format(symbol, last_time, current, min_price))

        if not min_price or pd.isna(min_price):
            return -1
        else:
            return min_price
    except:
        logger.exception("get_min_price")
    finally:
        process.data_lock.release()


def get_boll_avrg(market, start=-5, to=-1):
    """
    获取boll平均值
    :param to:
    :return:
    """
    try:
        process.data_lock.acquire()
        upper, middle, lower = -1, -1, -1
        df = process.KLINE_DATA.get(market, None)
        if df is None:
            return upper, middle, lower

        num = 0
        while start <= to:
            temp_df = df.head(len(df) + start)
            temp_df["upper"], temp_df["middle"], temp_df["lower"] = talib.BBANDS(temp_df.close.values, timeperiod=15, nbdevup=2, nbdevdn=2, matype=0)
            upper += temp_df.loc[len(temp_df) +start, "upper"]
            middle += temp_df.loc[len(temp_df) +start, "middle"]
            lower += temp_df.loc[len(temp_df) +start, "lower"]
            num += 1
            start += 1

        return upper/num, middle/num, lower/num
    except:
        logger.exception("get_boll_avrg")
        return upper, middle, lower
    finally:
        process.data_lock.release()


def get_boll(market, pos=0, update2ui=True):
    try:
        process.data_lock.acquire()
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
            process.REALTIME_UML = (upper, middle, lower) #.put((upper, middle, lower))
        return upper, middle, lower
    except:
        logger.exception("get_boll")
    finally:
        process.data_lock.release()
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
    try:
        process.data_lock.acquire()
        k, d, j = -1, -1, -1
        df = process.KLINE_DATA.get(market, None)
        if df is None:
            return k, d, j

        len_df = len(df)
        temp_df = df.head(len_df - pos)
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
        logger.info("get_kdj, df size={}, pos={}, kdj={}/{}/{}".format(len_df, pos, k, d, j))
        return k, d, j
    except Exception as e:
        logger.exception("get_kdj exception={}".format(e))
        return k,d,j
    finally:
        process.data_lock.release()


def kdj_5min_update():
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], "5min")
    k,d,j = get_kdj(market)
    process.REALTIME_KDJ_5MIN = (k,d,j)#.put((k, d, j))
    return k, d, j

def kdj_15min_update():
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], "15min")
    k,d,j = get_kdj(market)
    process.REALTIME_KDJ_15MIN=(k,d,j) #.put((k, d, j))
    # return k, d, j
    return False

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


def update_balance(money_only=False):
    try:
        for money, value in config.CURRENT_SYMBOLS.items():
            coins = value.get("coins", [])
            if coins:
                bal0 = get_balance(money.lower(), result_type=2)
                if bal0:
                    config.CURRENT_SYMBOLS[money]["trade"] = float(bal0.get("trade", 0))
                    config.CURRENT_SYMBOLS[money]["frozen"] = float(bal0.get("frozen", 0))
                    if config.CURRENT_SYMBOLS[money].get("principal", 0) == 0:
                        config.CURRENT_SYMBOLS[money]["principal"] = round(2*float(bal0.get("trade", 0)), 4)
                else:
                    logger.error("get balance error, money={}".format(money))

                if not money_only:
                    for coin_dict in coins:
                        coin = coin_dict["coin"]
                        bal1 = get_balance(coin.lower(), result_type=2)
                        if bal1:
                            coin_dict["trade"] = float(bal1.get("trade", 0))
                            coin_dict["frozen"] = float(bal1.get("frozen", 0))
                        else:
                            logger.error("get balance error, coin={}".format(coin))
    except Exception as e:
        logger.exception("update balance e= {}".format(e))
        return False

    logger.info("update balance: {}".format(config.CURRENT_SYMBOLS))
    return True


# result_type=0--trade, 1--frozen, 2--all
def get_balance(currency, result_type=0, retry=2):
    if config.CURRENT_PLATFORM == 'huobi':
        hrs = HuobiREST()
        while retry > 0:
            balance = hrs.get_balance(currency=currency)
            if balance[0] == 200 and balance[1]:
                balance_data = balance[1]
                if result_type == 0:
                    return balance_data.get("trade", -1)
                elif result_type == 1:
                    return balance_data.get("frozen", -1)
                else:
                    return balance_data
            else:
                retry -= 1
        return None


def is_still_down2(symbol, bp=0.0035, delta_time=310):
    """
    最近五分钟内的最低价格和当前价格对比．如果当前价格未超过最低价格的千分之3,则认为仍处于下跌状态
    :param symbol:
    :param bp:
    :param delta_time:
    :return:
    """
    now = int(time.time()) * 1000
    current_price = get_current_price(symbol)
    min_price = get_min_price(symbol, last_time=now - (delta_time * 1000))
    if (current_price-min_price)/min_price > bp:
        return False
    else:
        return True


def is_still_down(symbol, delta=100, percent=1):
    """
    是否还在下跌，　以近期平均值与远期平均值的关系来衡量，近平大于远平的1.002倍，认为不在下跌了
    :param symbol:
    :param delta:
    :param percent:
    :return:
    """
    process.data_lock.acquire()
    try:
        df = process.KLINE_DATA.get(symbol, None)
        if df is None:
            return False

        now = int(time.time()) * 1000
        last_time_far_beg = now - delta * 1000*2
        last_time_far_end = now - delta * 1000

        last_time_close = now - delta * 1000 / 2

        tmp_df = df.loc[df["ts"] > last_time_far_beg]
        far_mean = tmp_df.loc[tmp_df["ts"] < last_time_far_end].close.mean()

        close_mean = df.loc[df["ts"] > last_time_close].close.mean()
        cp = float(df.tail(1)["close"])

        if close_mean > far_mean*percent and cp > far_mean:
            logger.info("is still down False, far_mean={}, close_mean={}, cp={}".format(far_mean, close_mean, cp))
            return False
        else:
            logger.info("is still down True, far_mean={}, close_mean={}, cp={}".format(far_mean, close_mean, cp))
            return True

    except Exception as e:
        logger.exception("is still down exception. e={}".format(e))
        return False
    finally:
        process.data_lock.release()


def is_still_up2(symbol, bp=0.0035, delta_time=310):
    # 根据最大价格与当前价格的回撤幅度判断是否还在涨
    now = int(time.time()) * 1000
    current_price = get_current_price(symbol)
    max_price = get_max_price(symbol, now - (delta_time * 1000), current=0)

    if (max_price-current_price)/max_price > bp:
        return False
    else:
        return True


def is_still_up(symbol, delta=100, percent=1):
    process.data_lock.acquire()
    try:
        df = process.KLINE_DATA.get(symbol, None)
        if df is None:
            return False

        now = int(time.time()) * 1000
        last_time_far_beg = now - delta * 1000*2
        last_time_far_end = now - delta * 1000

        last_time_close = now - delta * 1000 / 2

        tmp_df = df.loc[df["ts"] > last_time_far_beg]
        far_mean = tmp_df.loc[tmp_df["ts"] < last_time_far_end].close.mean()

        close_mean = df.loc[df["ts"] > last_time_close].close.mean()
        cp = float(df.tail(1)["close"])

        if close_mean*percent < far_mean and cp < far_mean:
            logger.info("is still up False, far_mean={}, close_mean={}, cp={}".format(far_mean, close_mean, cp))
            return False
        else:
            logger.info("is still up True, far_mean={}, close_mean={}, cp={}".format(far_mean, close_mean, cp))
            return True
    except Exception as e:
        logger.exception("is still up exception. e={}".format(e))
        return False
    finally:
        process.data_lock.release()


# def is_still_up(symbol, delta=300, range=1.004):
#     current_price = get_current_price(symbol)
#     if current_price <= 0:
#         return False
#
#     now = int(time.time()) * 1000
#     max_price = get_max_price(symbol, now - (delta * 1000), current=0)
#
#     # 判断是不是还在涨,如果是，暂时不卖
#     if max_price > 0 and current_price * range > max_price:
#         logger.info("still up return True, max_p={}, cp={}！!".format(max_price, current_price))
#         return True
#
#     return False

def should_low_buy(symbol, period="15min", risk=1.04):
    now = int(time.time()) * 1000
    market = "market.{}.kline.{}".format(symbol, period)
    current_price = get_current_price(symbol)

    if current_price <= 0:
        return 0

    k, d, j = get_kdj(market)
    if k - d < -10:
        logging.info(u"BL k远小于d, 暂时不买, k={}, d={}, cp={}".format(k, d, current_price))
        return 0

    min_price_5 = get_min_price(symbol, now - (15 * 60 * 1000) * 5, current=now - (7 * 60 * 1000))
    min_price_20 = get_min_price(symbol, now - (15 * 60 * 1000) * 20, now - (7 * 60 * 1000))
    min_price_60 = get_min_price(symbol, now - (15 * 60 * 1000) * 60, now - (7 * 60 * 1000))
    if min_price_5 <= 0 or min_price_20 <= 0 or min_price_60 <= 0:
        logger.warning("buy low min price <0")
        return 0

    # 比最低价还低1％以上，且最近三个周期都在跌
    # percent_factor = 0  # 价格越代，这个值越大，　买的越多
    low_percent = 1 + (risk - 1) / 100

    # 　如果当前持仓比低于用户预设的值，则降低买入门槛，尽快达到用户要求的持仓比
    low_percent = 0.99 if low_percent < 0.99 else low_percent
    low_percent = 1.01 if low_percent > 1.01 else low_percent

    low_percent_5 = low_percent * 1.05
    low_percent_20 = low_percent
    low_percent_60 = low_percent * 0.995

    buy_percent = 0
    # if current_price * low_percent_5 < min_price_5 and get_open(market, 1) > get_close(market, 1):
    if current_price * low_percent_5 < min_price_5:
        # 跌的越多，percent_factor 越大
        logger.info("buy low 5")
        factor = min_price_5 / current_price - low_percent_5
        buy_percent += 0.15 + factor
    if current_price * low_percent_60 <= min_price_60:
        logger.info("buy low 60")
        factor = min_price_60 / current_price - low_percent_60
        buy_percent += 0.5 + factor
    elif current_price * low_percent_20 <= min_price_20:
        logger.info("buy low 20")
        factor = min_price_20 / current_price - low_percent_20
        buy_percent += 0.3 + factor

    if buy_percent > 0:
        buy_percent *= risk
        logger.warning("[{}]should_low_buy={}".format(symbol, buy_percent))

    return buy_percent


def should_fly_buy(symbol, period="5min", risk=1.04):
    if vol_price_fly_params.get("check", 1) != 1:
        log_config.output2ui("vol price fly is not check", 7)
        return 0

    market = "market.{}.kline.{}".format(symbol, period)
    multiple = vol_price_fly_params.get("vol_percent", 1.2) * (1 / risk)
    mul_21 = 1.05

    peroid_5min = 1
    if period == "5min":
        peroid_5min = 1
    elif period == "15min":
        peroid_5min = 3

    last_peroid_0_3 = get_trade_vol_from_local(symbol, 0, 3 * peroid_5min)
    last_peroid_3_7 = get_trade_vol_from_local(symbol, 3 * peroid_5min, 7 * peroid_5min)

    if not last_peroid_0_3 or not last_peroid_3_7:
        return 0

    try:
        # 最近三个周期的量要大于最近7个周期(3-10)的量
        time_0_3 = (last_peroid_0_3.get("end_time", 0) - last_peroid_0_3.get("start_time", 0)) / (
                1000 * 60 * 5 * peroid_5min)
        time_3_7 = (last_peroid_3_7.get("end_time", 0) - last_peroid_3_7.get("start_time", 0)) / (
                1000 * 60 * 5 * peroid_5min)
        time_0_3 = 3 if time_0_3 == 0 else time_0_3
        time_3_7 = 7 if time_3_7 == 0 else time_3_7
        avg_0_3_vol = last_peroid_0_3.get("trade_vol", 0) / time_0_3
        avg_3_7_vol = last_peroid_3_7.get("trade_vol", 0) / time_3_7
        if not avg_0_3_vol >= avg_3_7_vol * multiple:
            return 0

        # (5分钟）当前周期的交易量是上一个周期的3倍以上， 且当前周期的交易量要大于1.1倍的最近21个周期平均交易量
        last_peroid_0 = get_trade_vol_from_local(symbol, 0, 1).get("trade_vol", 0)
        last_peroid_1 = get_trade_vol_from_local(symbol, 1, 1).get("trade_vol", 0)
        last_peroid_2 = get_trade_vol_from_local(symbol, 2, 1).get("trade_vol", 0)
        high_than_last = vol_price_fly_params.get("high_than_last", 2) * (1 / risk)
        local_21 = get_trade_vol_from_local(symbol, 3, 7)
        if local_21:
            local_21 = local_21.get("trade_vol", 0)
        else:
            return 0

        if not all([last_peroid_0, last_peroid_1, last_peroid_2, local_21]):
            return 0

        if not last_peroid_0 >= last_peroid_1 * high_than_last or not last_peroid_1 >= high_than_last * last_peroid_2:
            return 0

        last_peroid_21 = local_21 / 7
        if not last_peroid_0 >= mul_21 * last_peroid_21:
            return 0

        # 当前价格不能超过前面第三个周期的收盘价*（1+规定涨幅）
        current_price = get_current_price(symbol)
        close_before_2 = (get_close(market, before=3) + get_close(market, before=4) + get_close(market, before=5)) / 3
        if close_before_2 < 0:
            return 0

        if (current_price > close_before_2 * (1 + vol_price_fly_params.get("price_up_limit", 0.02) * risk)):
            return 0

        if current_price < close_before_2:
            return 0

        if current_price < get_open(market, before=1):
            return 0

        percent = vol_price_fly_params["buy_percent"]
        percent *= risk
        logger.warning("[{}]should_fly_buy={}".format(symbol, percent))
    except:
        return 0

    return percent


def should_any_buy(symbol):
    if is_still_down2(symbol):
        return 0
    else:
        return 0.2


def buy_low():
    """
    低吸
    :return:
    """
    now = int(time.time()) * 1000
    symbol = config.NEED_TOBE_SUB_SYMBOL[0]
    market = "market.{}.kline.{}".format(symbol, "15min")
    current_price = get_current_price(symbol)

    if current_price <= 0:
        logger.warning("buy_low get current price error.")
        return False

    min_price = get_min_price(symbol, now - (5*60 * 1000), current=0)

    # 判断是不是还在跌,如果是，暂时不买
    # if is_still_down(symbol):
    #     logger.info("buy low recent 5min min price={}, current price={}, still down！!".format(min_price, current_price))
    #     return False

    k, d, j = get_kdj(market)
    if k-d < -7:
        logging.info(u"BL k远小于d, 暂时不买, k={}, d={}, cp={}".format(k, d, current_price))
        return False

    min_price_5 = get_min_price(symbol, now - (15 * 60 * 1000)*5, current=now - (7 * 60 * 1000))
    min_price_20 = get_min_price(symbol, now - (15 * 60 * 1000) * 20, now - (7 * 60 * 1000))
    min_price_60 = get_min_price(symbol, now - (15 * 60 * 1000) * 60, now - (7 * 60 * 1000))
    if min_price_5 <= 0 or min_price_20 <= 0 or min_price_60 <= 0:
        logger.warning("buy low min price <0")
        return False

    # 比最低价还低1％以上，且最近三个周期都在跌
    # percent_factor = 0  # 价格越代，这个值越大，　买的越多
    low_percent = 1.005 + (config.RISK-1)/100

    # 如果最近15分钟已经买过，则提高买入门槛
    already = is_already_buy()
    if already[0]:
        low_percent = 1 + (low_percent-1) * already[1]

    #　如果当前持仓比低于用户预设的值，则降低买入门槛，尽快达到用户要求的持仓比
    position, buy_factor, sell_factor = get_current_position()
    low_percent += (buy_factor-1) / 100

    low_percent = 1.001 if low_percent < 1.001 else low_percent
    low_percent = 1.01 if low_percent > 1.01 else low_percent

    low_percent_5 = low_percent*1.15
    low_percent_20 = low_percent
    low_percent_60 = low_percent * 0.998
    logger.info("buy low checking. current price={}, mp={}, mp5={}, mp20={}, mp60={}, lowp={}".format(current_price, min_price, min_price_5, min_price_20, min_price_60, low_percent))

    buy_percent = 0
    if current_price*low_percent_5 < min_price_5 and get_open(market, 1) > get_close(market, 1):
        # 跌的越多，percent_factor 越大
        logger.info("buy low 5")
        factor = min_price_5/current_price-low_percent_5
        buy_percent += 0.1 + factor
    if current_price*low_percent_60 <= min_price_60:
        logger.info("buy low 60")
        factor = min_price_60/current_price-low_percent_60
        buy_percent += 0.5+factor
    elif current_price*low_percent_20 <= min_price_20:
        logger.info("buy low 20")
        factor = min_price_20/current_price-low_percent_20
        buy_percent += 0.3 + factor

    if buy_percent > 0:
        buy_percent *= config.RISK

        still_down = False
        if is_still_down2(current_price, min_price):
            logger.info("buy low, still down, return True, don't buy")
            # buy_percent *= 0.5
            # still_down = True
            return False
        else:
            logger.info("buy low, not still down, buy")
            # buy_percent *= 1.3

        logger.warning(
            "buy low buy, current price={}, buy percent={}, mp={}, mp5={}, mp20={}, mp60={}, still down={}".format(
                current_price, buy_percent, min_price, min_price_5, min_price_20, min_price_60, still_down))

        msg = "[买入{}]BL 买入比例={}%, 买入价格={}, MP={}, MP5/20/60={}/{}/{}.".format(
            symbol, round(buy_percent*100, 2), round(current_price, 6), round(min_price, 6),round(min_price_5, 6), round(min_price_20, 6), round(min_price_60, 6))

        if not trade_alarm(msg):
            return False

        ret = buy_market(symbol, percent=buy_percent, current_price=current_price)
        if ret[0]:
            msg = "[买入{}]BL 计划买入比例={}%, 实际买入金额={}$, 买入价格={}, RMP={}, RMP5/20/60={}/{}/{}.".format(
                symbol, round(buy_percent * 100, 2), round(ret[1], 2), round(current_price, 6), round(min_price, 6), round(min_price_5, 6),
                round(min_price_20, 6), round(min_price_60, 6))
            success = False
            if ret[0] == 1:
                msg += "-交易成功！"
                success = True
            elif ret[0] == 2:
                msg += "-交易被取消, 取消原因: {}!".format(ret[2])
            elif ret[0] == 3:
                msg += "-交易失败, 失败原因: {}！".format(ret[2])

            log_config.output2ui(msg, 6)
            logger.warning(msg)
            log_config.notify_user(msg, own=True)
            log_config.notify_user(log_config.make_msg(0, symbol, current_price=current_price, percent=buy_percent))
            logger.info("-----BUY_RECORD = {}".format(BUY_RECORD))
            # if still_down:
            #     return False    #如果还在跌，先少买，但不暂停此策略

            return True

    return False


def sell_high():
    now = int(time.time()) * 1000
    symbol = config.NEED_TOBE_SUB_SYMBOL[0]
    market = "market.{}.kline.{}".format(symbol, "15min")

    max_price = get_max_price(symbol, now - (5*60 * 1000), current=0)
    current_price = get_current_price(symbol)

    # # 判断是不是还在涨,如果是，暂时不卖
    # if max_price > 0 and current_price*1.004 > max_price:
    #     logger.info("sell high max price={}, current price={}, still up！!".format(max_price, current_price))
    #     return False

    # 判断是不是还在涨,如果是，暂时不卖
    # if is_still_up(symbol):
    #     logger.info("sell high max price={}, current price={}, still up！!".format(max_price, current_price))
    #     return False

    max_price_5 = get_max_price(symbol, now - (15 * 60 * 1000) * 5, now - (7 * 60 * 1000))
    max_price_20 = get_max_price(symbol, now - (15 * 60 * 1000) * 20, now - (7 * 60 * 1000))
    max_price_60 = get_max_price(symbol, now - (15 * 60 * 1000) * 60, now - (7 * 60 * 1000))
    if max_price_5 <= 0 or max_price_20 <= 0 or max_price_60 <= 0:
        return False

    sell_percent = 0
    # 比最高价还高1％，且最近三个周期都在涨
    up_percent = 1.005 + (config.RISK-1)/100

    #　如果当前持仓比低于用户预设的值，则提高卖出门槛，以保证用户要求的持仓比
    position, buy_factor, sell_factor = get_current_position()
    if position > 0:
        if sell_factor == 0:
            logger.warning("sell_high be cancelled, lock position")
            return False

    already = is_already_sell()
    if already[0]:
        up_percent = 1 + (up_percent-1)*already[1]

    up_percent += (sell_factor-1) / 100

    up_percent = 1.001 if up_percent < 1.001 else up_percent
    up_percent = 1.01 if up_percent > 1.01 else up_percent

    up_percent_5 = up_percent*1.015
    up_percent_20 = up_percent
    up_percent_60 = up_percent*0.998
    logger.info("sell high checking. current price={}, mp={} mp5={}, mp20={}, mp60={}, upp={}".format(current_price, max_price, max_price_5, max_price_20, max_price_60, up_percent))

    if current_price >= max_price_5*up_percent_5 and get_open(market, 1) < get_close(market, 1):
        logger.info("sell high, cp>5")
        factor = current_price / max_price_5 - up_percent_5
        sell_percent += 0.1+factor
    if current_price >= max_price_60 * up_percent_60:
        logger.info("sell high, cp>60")
        factor = current_price/max_price_60-up_percent_60
        sell_percent += 0.5+factor
    elif current_price >= max_price_20 * up_percent_20:
        logger.info("sell high, cp>20")
        factor = current_price/max_price_20-up_percent_20
        sell_percent += 0.3+factor

    if sell_percent > 0:
        sell_percent *= config.RISK
        k,d,j = get_kdj(market)
        if d < 76:
            sell_percent_old = sell_percent
            zhekou = (1-(76-d)/76)
            sell_percent *= zhekou
            logger.info("sell high d={}<75, sell percent={} * {} = {}".format(d, sell_percent_old, zhekou, sell_percent))

        close1 = get_close(market)
        # 相比上个收盘价涨幅超过2个点
        upper = (current_price - close1) / close1
        if upper > 0.02:
            sell_percent_old = sell_percent
            ewai = ((upper-0.02)/0.02)*8
            sell_percent += ewai
            logger.info("sell high upper={}>0.02, sell percent={}+{}={}".format(upper, sell_percent_old, ewai, sell_percent))

        logger.info("sell high, percent={}, cp={}".format(sell_percent, current_price))
        still_up = False
        if is_still_up2(cp=current_price, mp=max_price):
            logger.info("sell high, still up, don't sell")
            return False
        else:
            logger.info("sell high, not still up, sell")

        logger.warning(
            "sell high sell, current price={}, percent={}, mp={}, m5={}, m20={}, m60={}, upp={}, still up={}".format(current_price,
                                                                                                        sell_percent,
                                                                                                        max_price,
                                                                                                        max_price_5,
                                                                                                        max_price_20,
                                                                                                        max_price_60,
                                                                                                        up_percent, still_up))

        msg = "[卖出{}]SH 计划卖出比例={}%, 实际卖出量={}个, 卖出价格={}, RMP={}, RMP5/20/60={}/{}/{}..".format(
            symbol, round(sell_percent * 100, 2), round(current_price, 6), round(max_price, 6), round(max_price_5, 6),
            round(max_price_20, 6), round(max_price_60, 6))

        # msg = "[BUY]sell_high sell {} percent: {}, current price={}, max_price_5={}, max_price_20={}, max_price_60={}".format(
        #     symbol, sell_percent, current_price, max_price_5, max_price_20, max_price_60)
        if not trade_alarm(msg):
            return False

        ret = sell_market(symbol, percent=sell_percent, current_price=current_price)
        if ret[0]:
            msg = "[卖出{}]SH 计划卖出比例={}%, 实际卖出量={}个, 卖出价格={}, RM={}, RM5/20/60={}/{}/{}.".format(
                symbol, round(sell_percent * 100, 2), round(ret[1], 2), round(current_price, 6), round(max_price, 6),round(max_price_5, 6),
                round(max_price_20, 6), round(max_price_60, 6))

            if ret[0] == 1:
                msg += "-交易成功！"
            elif ret[0] == 2:
                msg += "-交易被取消, 取消原因: {}!".format(ret[2])
            elif ret[0] == 3:
                msg += "-交易失败, 失败原因: {}！".format(ret[2])

            log_config.output2ui(msg, 7)
            logger.warning(msg)
            log_config.notify_user(msg, own=True)
            log_config.notify_user(log_config.make_msg(1, symbol, current_price=current_price, percent=sell_percent))
            logger.info("-----SELL_RECORD = {}".format(SELL_RECORD))

            # if still_up:
            #     return False
            return True
    else:
        logger.info("sell high percent=0")

    return False


def is_already_buy(last_time=0):
    """
    检测最近15分钟内有没有买入过，如果15分钟内有其他策略买入过，则应该提高买入门槛，以避免重复买入
    :param last_time: 检测时间起始值
    :return: 是否买过，再次买入时难度提升系数(取值1--1.1)
    """
    try:
        if not last_time:
            last_time = int(time.time()) * 1000 - 15 * 60 * 1000
        symbol = config.NEED_TOBE_SUB_SYMBOL[0]
        total_buy_amount = 0
        for trade in BUY_RECORD:
            last_buy_time = int(trade.get("finished-at", 0))
            last_buy_amount = float(trade.get("field-cash-amount", 0))  # 上次买入的金额数
            trade_type = trade.get("type", "")
            sym = trade.get("symbol", "")
            if last_buy_time and last_buy_time > last_time and symbol == sym and "buy" in trade_type:
                total_buy_amount += last_buy_amount

        if total_buy_amount > 0:
            bal0, bal0_f, bal1, bal1_f = update_balance()
            current_price = get_current_price(symbol)
            total_money = (bal0 + bal0_f) * current_price + bal1 + bal1_f
            # 上次买的越多, 这次需要买入的门槛就越高, 如一共1000，　刚刚买入300，　当前系数＝１＋（300／1000）＝1.3
            factor = 1+(total_buy_amount/total_money)/10
            factor = 1.1 if factor > 1.1 else factor
            logger.info("is_already_buy return true, factor={}".format(factor))
            return True, factor
    except Exception as e:
        logger.warning("is_already_buy catch exception={}".format(e))

    return False, 1


def is_already_sell(last_time=0):
    """
    检测最近15分钟内有没有卖出过，如果15分钟内有其他策略卖出过，则应该提高卖出门槛，以避免重复卖出
    :param last_time: 检测时间起始值
    :return: 是否卖过，再次卖出时难度提升系数，取值（１--1.1）
    """
    try:
        factor = 1
        if not last_time:
            last_time = int(time.time()) * 1000-15*60*1000

        symbol = config.NEED_TOBE_SUB_SYMBOL[0]
        total_sell_amount = 0
        for trade in SELL_RECORD:
            last_sell_time = int(trade.get("finished-at", 0))
            last_sell_amount = float(trade.get("field-cash-amount", 0))
            trade_type = trade.get("type", "")
            sym = trade.get("symbol", "")
            if last_sell_time and last_sell_time >= last_time and symbol == sym and "sell" in trade_type:
                total_sell_amount += last_sell_amount

        if total_sell_amount > 0:
            bal0, bal0_f, bal1, bal1_f = update_balance()
            current_price = get_current_price(symbol)
            total_money = (bal0 + bal0_f) * current_price + bal1 + bal1_f

            # 上次卖的越多, 这次需要卖出的门槛就越高, 如一共1000，　刚刚卖出300，　当前系数＝１＋（300／1000）＝1.3
            factor = 1+(total_sell_amount/total_money)/10
            factor = 1.1 if factor > 1.1 else factor
            logger.info("is_already_sell return true, factor={}".format(factor))
            return True, factor
    except Exception as e:
        logger.warning("is_already_sell catch exception={}".format(e))

    logger.info("is_already_sell return false, factor={}".format(factor))
    return False, 1


def get_current_position():
    """
    根据当前的仓位与用户期望的仓位大小关系，　来计算买卖系数，
    获取当前的持仓比以及买入＼卖出条件系数，系数小于１代表交易门槛降低，系数大于１代表交易门槛升高, 如果系数为零代表禁止交易
    buy_factor, sell_factor的取值范围在0.7－－1.3之间
    :return:
    """
    position = -1
    buy_factor = 1
    sell_factor = 1
    return position, buy_factor, sell_factor

    try:
        bal0, bal0_f, bal1, bal1_f = update_balance()
        current_price = get_current_price(symbol=config.NEED_TOBE_SUB_SYMBOL[0])
        if current_price < 0:
            return position, buy_factor, sell_factor

        total = (bal0 + bal0_f) * current_price + bal1 + bal1_f
        position = ((bal0 + bal0_f) * current_price) / total  # 当前持仓比
        if config.LIMIT_MIN_POSITION >= 0.01:
            limit_pos_min = config.LIMIT_MIN_POSITION
        else:
            limit_pos_min = 0.2

        if config.LIMIT_MAX_POSITION >= 0.01:
            limit_pos_max = config.LIMIT_MAX_POSITION
        else:
            limit_pos_max = 0.8

        if position < limit_pos_min:
            # 比如用户期望仓位是50％，　当前仓位是20％，　则factor=(0.5-0.2)/0.5/2=0.3, 则买入系数为0.7（更易买）, 卖出系数为1.3（更难卖）
            factor = (limit_pos_min - position) / limit_pos_min/3
            buy_factor = 1 - factor             # 小于１代表买入门槛应该降低
            sell_factor = 1 + factor          # 大于１代表卖出门槛应该增高

            # 如果用户设置了强制锁仓则不能卖出
            if config.FORCE_POSITION_MIN:
                sell_factor = 0
        elif position > limit_pos_max:
            # 比如用户期望仓位是70％，　当前仓位是90％，　则factor=(0.9-0.7)/0.7/3=0.09, 则买入系数为1.009（不易买）, 卖出系数为0.901（更易卖）
            factor = (position - limit_pos_max) / limit_pos_max/3
            sell_factor = 1 - factor             # 小于１代表卖出门槛应该降低
            buy_factor = 1 + factor             # 大于１代表买入门槛应该增高

            # 如果用户设置了强制锁仓则不能卖出
            if config.FORCE_POSITION_MAX:
                buy_factor = 0
        else:
            factor = (position-(limit_pos_max+limit_pos_min)/2) / ((limit_pos_max+limit_pos_min)/2)/10
            if factor < 0:
                sell_factor = 1-factor
                buy_factor = 1+factor
            else:
                sell_factor = 1+factor
                buy_factor = 1-factor

        buy_factor = 0.7 if buy_factor < 0.7 else buy_factor
        buy_factor = 1.3 if buy_factor > 1.3 else buy_factor
        sell_factor = 0.7 if sell_factor < 0.7 else sell_factor
        sell_factor = 1.3 if sell_factor > 1.3 else sell_factor
    except Exception as e:
        logger.exception("get_current_position e={}".format(e))

    logger.info("get_current_position position={}, limit position={}, buy_factor={}, sell_factor={}, ".format(position, config.LIMIT_MIN_POSITION, buy_factor, sell_factor))
    return position, buy_factor, sell_factor


STRATEGY_LIST = [
    # Strategy(macd_strategy_5min, 15, 1, "macd_strategy_5min"),
    # Strategy(macd_strategy_1min, 10, 1, "macd_strategy_1min"),
    # Strategy(macd_strategy_1day, 20, 1, "macd_strategy_1day"),
    # Strategy(kdj_strategy_buy, 240, -1, after_execute_sleep=900 * 3, name="kdj_strategy_buy"),
    # Strategy(kdj_strategy_sell, 240, -1, after_execute_sleep=900 * 3, name="kdj_strategy_sell"),
    # Strategy(kdj_strategy_buy, 10, -1, after_execute_sleep=30, name="kdj_strategy_buy"),#1800
    # Strategy(kdj_strategy_sell, 10, -1, after_execute_sleep=900 * 2, name="kdj_strategy_sell"),
    # Strategy(stop_loss, 20, -1, after_execute_sleep=300, name="stop_loss"),
    # Strategy(move_stop_profit, 12, -1, after_execute_sleep=300, name="move_stop_profit"),
    # Strategy(vol_price_fly, 20, -1, name="vol_price_fly", after_execute_sleep=900 * 2),
    # Strategy(boll_strategy, 20, -1, name="boll strategy", after_execute_sleep=900 * 2),
    # # Strategy(kdj_5min_update, 30, -1, name="kdj_5min_update", after_execute_sleep=1),
    # Strategy(kdj_15min_update, 10, -1, name="kdj_15min_update", after_execute_sleep=3),
    # Strategy(trade_advise_update, 3600, -1, name="advise_msg", after_execute_sleep=10),
    # Strategy(buy_low, 10, -1, name="buy_low", after_execute_sleep=600),
    # Strategy(sell_high, 11, -1, name="sell_high", after_execute_sleep=600),
    # Strategy(auto_trade, 11, -1, name="auto trade", after_execute_sleep=10),
    Strategy(stg_smart_first, 8, -1, name="smart first", after_execute_sleep=900),
    Strategy(stg_smart_profit, 5, -1, name="smart profit", after_execute_sleep=120),
    Strategy(stg_smart_patch, 5, -1, name="smart patch", after_execute_sleep=120),
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
