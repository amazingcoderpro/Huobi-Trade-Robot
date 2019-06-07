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
kdj_buy_params = {"check": 1, "k": 23, "d": 21, "buy_percent": 0.22, "up_percent": 0.004, "peroid": "15min"}
kdj_sell_params = {"check": 1, "k": 82, "d": 80, "sell_percent": 0.3, "down_percent": 0.005, "peroid": "15min"}
vol_price_fly_params = {"check": 1, "vol_percent": 1.2, "high_than_last": 2, "price_up_limit": 0.01, "buy_percent": 0.3,
                        "peroid": "5min"}
boll_strategy_params = {"check": 1, "peroid": "15min", "open_diff1_percent": 0.025, "open_diff2_percent": 0.025,
                        "close_diff1_percent": 0.0025, "close_diff2_percent": 0.0025, "open_down_percent": -0.02,
                        "open_up_percent": 0.003, "open_buy_percent": 0.35, "trade_percent": 1.5, "close_up_percent": 0.03,
                        "close_buy_percent": 0.5}

# BUY_LOW_RECORD = {}
# SELL_HIGH_RECORD = {}

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
    symbol = config.NEED_TOBE_SUB_SYMBOL[0]

    # if is_still_up(symbol):
    #     logger.info(u"boll_strategy　still up")
    #     return False
    #
    # if is_still_down(symbol):
    #     logger.info(u"boll_strategy　still down")
    #     return False

    market = "market.{}.kline.{}".format(symbol, peroid)
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


def auto_trade():
    for trade_group in config.TRADE_RECORDS_NOW:
        interval_ref = trade_group.get("interval_ref", 0)
        if interval_ref == 0:
            avg_price = trade_group.get("avg_price", 0)
            coin_name = trade_group.get("coin", "")
            money_name = trade_group.get("money", "")
            symbol = "{}{}".format(coin_name, money_name).lower()
            trade_mode_name = trade_group.get("mode", "robust")
            trade_mode = config.TRADE_MODE.get(trade_mode_name, {})
            fill_interval = trade_mode.get("interval", 0.08)    # 补仓间隔
            current_price = get_current_price(symbol)

            if current_price < avg_price*(1-fill_interval):
                buy_amount_plan = trade_group.get("last_buy_amount", 0) * 2      # 先直接按倍投的方式来弄
                ret = buy_market(symbol, buy_amount_plan)
                # 买入成功
                if ret[0] == 1:

                    buy_amount_actual = ret[1]
                    buy_coin_actual = ret[1]
                    buy_price_actual = ret[1]
                    time_now = datetime.now()
                    trade = {
                        "buy_type": "buy_auto",  # 买入模式：buy_auto 自动买入(机器策略买入)，buy_man手动买入,
                        "sell_type": "sell_profit",# 要求的卖出模式，机器买入的一般都为动止盈卖出。可选：sell_profit 止盈卖出， sell_no-不要卖出，针对手动买入的单，sell_auto-使用高抛，kdj等策略卖出
                        "buy_time": time_now,
                        "sell_time": None,
                        "coin": coin_name,
                        "coin_num": buy_coin_actual,  # 买入或卖出的币量
                        "coin_price_plan": current_price,  # 计划买入币的价格
                        "coin_price": buy_price_actual,  # 实际挂单成交的价格
                        "money": money_name,
                        "money_num_plan": buy_amount_plan,  # 计划买入的量
                        "money_num": buy_amount_actual,  # 实际花费的计价货币量
                        "is_sell": 0,  # 是否已经卖出
                        "profit_percent": 0,  # 盈利比，卖出价格相对于买入价格
                        "profit": 0,  # 盈利额，只有卖出后才有
                    }
                    trade_group["trades"].append(trade)


        trades = trade_group.get("trades", [])
        for trade in trades:
            if trade.get("is_sell", 0):
                continue





def kdj_strategy_buy():
    if kdj_buy_params.get("check", 1) != 1:
        log_config.output2ui("kdj_buy is not check", 2)
        return False

    peroid = kdj_buy_params.get("peroid", "15min")
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], peroid)
    symbol = market.split(".")[1]

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
    position, buy_factor, sell_factor = get_current_position()
    if position > 0:
        limit_kd /= buy_factor

    # 如果最近15分钟已经买过，则提高买入门槛
    already = is_already_buy()
    if already[0]:
        limit_kd /= already[1]

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
        if position > 0:
            up_percent *= buy_factor

        if already[0]:
            up_percent *= already[1]

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
                if position > 0:
                    need_k /= buy_factor
                    need_d /= buy_factor

                # 是否买过了
                if already[0]:
                    need_k /= already[1]
                    need_d /= already[1]

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

    msg = "[买入{}]KD 计划买入比例={}%, 买入价格={}, 指标K={}, D={}, k1={}, D1={}, 阶段最低价格={}, 回暖幅度={}%".format(
        symbol, round(buy_percent * 100, 2), round(current_price, 6), round(cur_k, 2), round(cur_d, 2), round(last_k, 2), round(last_d, 2), round(min_price, 6),
         round(actual_up_percent * 100, 2))

    if not trade_alarm(msg):
        return False

    ret = buy_market(symbol, percent=buy_percent, current_price=current_price)
    if ret[0]:
        msg = "[买入{}]KD 计划买入比例={}%, 实际买入金额={}$, 买入价格={}, 指标K={}, D={}, 阶段最低价格={}, 回暖幅度={}%, 买入策略={}.".format(
            symbol, round(buy_percent * 100, 2), round(ret[1], 3), round(current_price, 6), round(cur_k, 2), round(cur_d, 2),
            round(min_price, 6), round(actual_up_percent * 100, 2), strategy_flag)

        if ret[0] == 1:
            msg += "-交易成功！"
        elif ret[0] == 2:
            msg += "-交易被取消, 取消原因: {}!".format(ret[2])
        elif ret[0] == 3:
            msg += "-交易失败, 失败原因: {}！".format(ret[2])

        log_config.output2ui(msg, 6)
        logger.warning(msg)
        log_config.notify_user(msg, own=True)
        log_config.notify_user(log_config.make_msg(0, symbol, current_price=current_price, percent=buy_percent))
        logger.info("-----BUY_RECORD = {}".format(BUY_RECORD))
        return True
    return False


def kdj_strategy_sell(currency=[], max_trade=1):
    if kdj_sell_params.get("check", 1) != 1:
        log_config.output2ui("kdj_sell is not check", 2)
        return False

    peroid = kdj_sell_params.get("peroid", "15min")
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], peroid)
    symbol = config.NEED_TOBE_SUB_SYMBOL[0]

    # if is_still_up(symbol):
    #     logging.info("kdj sell checking, still up!")
    #     return False

    current_price = get_current_price(symbol)
    # if TRADE_RECORD:

    cur_k, cur_d, cur_j = get_kdj(market)

    limit_diff_kd = 5 - (config.RISK-1)*5
    diff_kd = cur_k - cur_d

    entry_msg = "kdj_strategy_sell peroid={}, current k={}, d={}, current_price={}, actural diff_kd={}, limit diff_kd={}"\
        .format(peroid, cur_k, cur_d, current_price, diff_kd, limit_diff_kd)
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
    peroid = boll_strategy_params.get("peroid", "15min")
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], peroid)
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

    peroid = vol_price_fly_params.get("peroid", "5min")
    market = "market.{}.kline.{}".format(config.NEED_TOBE_SUB_SYMBOL[0], peroid)
    symbol = market.split(".")[1]
    multiple = vol_price_fly_params.get("vol_percent", 1.2) * (1/config.RISK)
    mul_21 = 1.1

    # 根据当前仓位动态调整买入卖出的难度系数
    position, buy_factor, sell_factor = get_current_position()
    if position > 0:
        multiple *= buy_factor
        mul_21 *= buy_factor

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
    # currency = symbol[3:]
    currency = config.SUB_RIGHT

    balance = get_balance(currency)
    if amount <= 0:
        if percent > 0:
            if balance and balance > 0:
                amount = round(balance * percent, 2)
            else:
                return 0, amount, "Have no balance for buying."
        else:
            return 0, 0, "buy percent less than zero."

    # 余额不足
    if amount > balance:
        amount = balance*0.95

    # 市价amount代表买多少钱的
    if amount < config.TRADE_MIN_LIMIT_VALUE:
        # 如果余钱够的话，按最小交易额买
        if balance > config.TRADE_MIN_LIMIT_VALUE:
            amount = config.TRADE_MIN_LIMIT_VALUE
        else:
            msg = "买入时余额不足, 当前可交易金额：{}.".format(round(balance, 2))
            logger.warning(msg)
            return 2, amount, msg

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
        return 1, amount, "Trade buy succeed."
    logger.error("buy market failed, symbol={}, amount={}, record={}".format(symbol, amount, record))
    log_config.output2ui("buy market error, symbol={}, amount={}, record={}".format(symbol, amount, record), 3)
    return 3, amount, "Trade failed. reason={}".format(ret)


def sell_market(symbol, amount=0, percent=0.1, record=True, current_price=0):
    # currency = symbol[0:3]
    currency = config.SUB_LEFT
    balance = get_balance(currency)
    # total_coin_value = process.CURRENT_TOTAL_COIN_VALUE
    # if total_coin_value:
    #     total = total_coin_value

    if amount <= 0:
        if percent > 0:
            if balance and balance > 0:
                amount = round(balance * percent, 4)
            else:
                return 0, amount, "Have no balance for selling."
        else:
            return 0, 0, "sell percent less than zero."

    if amount > balance:
        amount = balance*0.99

    # 市价卖时表示卖多少币
    if current_price:
        #　判断卖出时和卖出后的持仓比例是否满足用户设置的最低持仓比例，如果不满足则需要取消卖出，或者减少卖出量
        if config.LIMIT_MIN_POSITION > 0.0001 and config.FORCE_POSITION_MIN:
            bal0, bal0_f, bal1, bal1_f = update_balance()
            total = (bal0 + bal0_f) * current_price + bal1 + bal1_f
            current_chicang = ((bal0 + bal0_f) * current_price) / total     #当前持仓比
            limit_chicang_coin = config.LIMIT_MIN_POSITION * total / current_price  #要求的最低持仓币数
            if current_chicang <= config.LIMIT_MIN_POSITION:
                msg = "当前持仓比为{}%, 已经小于用户指定的强制最低持仓比{}%".format(round(current_chicang*100, 2), round(config.LIMIT_MIN_POSITION*100, 2))
                logger.warning(msg)
                return 2, amount, msg
            elif balance-amount < limit_chicang_coin:
                logger.warning("卖出后仓位将低于最小持仓比，需要减少卖出量，原计划卖出{}, 调整后卖出{}".format(round(amount, 4), round(balance-limit_chicang_coin,4)))
                amount = balance-limit_chicang_coin

        total_value = amount*current_price
        if total_value < config.TRADE_MIN_LIMIT_VALUE:
            # 如果余币够的话，按最小交易额卖
            if balance*current_price > config.TRADE_MIN_LIMIT_VALUE:
                amount = config.TRADE_MIN_LIMIT_VALUE/current_price
            else:
                msg = "卖出时余币不足, 当前可交易币量{}个, 价值：{}$.".format(round(balance, 4), round(balance*current_price, 2))
                logger.warning(msg)
                return 2, amount, msg
        elif total_value > config.TRADE_MAX_LIMIT_VALUE:
            amount = round(config.TRADE_MAX_LIMIT_VALUE/current_price, 4)
            if amount > balance:
                amount = balance*0.99

    if current_price > 1:
        amount = round(amount, 4)
    else:
        amount = round(amount, 2)
    logger.warning(
        "sell {} amount {}(个), current price={}, balance={}(个), total value={}$, min trade={}$, max trade={}$!record={}".format(symbol,
                                                                                                             amount,
                                                                                                             current_price,
                                                                                                             balance,
                                                                                                             total_value,
                                                                                                             config.TRADE_MIN_LIMIT_VALUE, config.TRADE_MAX_LIMIT_VALUE, record))
    hrs = HuobiREST(config.CURRENT_REST_MARKET_URL, config.CURRENT_REST_TRADE_URL, config.ACCESS_KEY, config.SECRET_KEY, config.PRIVATE_KEY)
    ret = hrs.send_order(amount=amount, source="api", symbol=symbol, _type="sell-market")
    # (True, '6766866273')
    if ret[0] == 200 and ret[1]:
        logger.warning("sell market success, symbol={}, amount={}, record={}".format(symbol, amount, record))
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
        return 1, amount, "Trade buy succeed."

    logger.error("sell market failed, symbol={}, amount={}, record={}, ret={}".format(symbol, amount, record, ret))
    log_config.output2ui("sell market error, symbol={}, amount={}, record={}, ret={}".format(symbol, amount, record, ret), 3)
    return 3, amount, "Trade failed. reason={}".format(ret)


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


def update_balance(is_first=False):
    try:
        # for symbol in config.NEED_TOBE_SUB_SYMBOL:
        s0 = config.SUB_LEFT    #symbol[0:3]
        s1 = config.SUB_RIGHT   #symbol[3:]
        bal0 = get_balance(s0, result_type=2)
        bal1 = get_balance(s1, result_type=2)
        str_balance = ""
        if bal0 and bal1:
            str_balance += "{}/{}".format(round(bal0.get("trade", 0), 4),
                                             round(bal0.get("frozen", 0), 4))

            str_balance += ", {}/{}".format(round(bal1.get("trade", 0), 2),
                                               round(bal1.get("frozen", 0), 2))
            logger.info("update_balance = {}".format(str_balance))
            process.REALTIME_BALANCE = str_balance #.put(str_balance)
            return bal0.get("trade", 0), bal0.get("frozen", 0), bal1.get("trade", 0), bal1.get("frozen", 0)
        else:
            logger.warning("update_balance failed.")
            return 0,0,0,0

    except Exception as e:
        logger.exception("update_balance e= {}".format(e))
        return 0,0,0,0


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
            # log_config.output2ui("balance = {}".format(balance_data))
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


def is_still_down2(cp, mp, bp=0.0035):
    if (cp-mp)/mp > bp:
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


def is_still_up2(cp, mp, bp=0.0035):
    # 根据最大价格与当前价格的回撤幅度判断是否还在涨
    if (mp-cp)/mp > bp:
        logger.info("is still up2 return False cp={}, mp={}, bp={}".format(cp,mp,bp))
        return False
    else:
        logger.info("is still up2 return True cp={}, mp={}, bp={}".format(cp, mp, bp))
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
    Strategy(kdj_strategy_buy, 10, -1, after_execute_sleep=900 * 2, name="kdj_strategy_buy"),
    Strategy(kdj_strategy_sell, 10, -1, after_execute_sleep=900 * 2, name="kdj_strategy_sell"),
    Strategy(stop_loss, 20, -1, after_execute_sleep=300, name="stop_loss"),
    Strategy(move_stop_profit, 12, -1, after_execute_sleep=300, name="move_stop_profit"),
    Strategy(vol_price_fly, 20, -1, name="vol_price_fly", after_execute_sleep=900 * 2),
    Strategy(boll_strategy, 20, -1, name="boll strategy", after_execute_sleep=900 * 2),
    # Strategy(kdj_5min_update, 30, -1, name="kdj_5min_update", after_execute_sleep=1),
    Strategy(kdj_15min_update, 10, -1, name="kdj_15min_update", after_execute_sleep=3),
    Strategy(trade_advise_update, 3600, -1, name="advise_msg", after_execute_sleep=10),
    Strategy(buy_low, 10, -1, name="buy_low", after_execute_sleep=600),
    Strategy(sell_high, 11, -1, name="sell_high", after_execute_sleep=600),
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
