#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/15
# Function: 
import pandas as pd
from mpl_finance import candlestick2_ohlc
import matplotlib.pyplot as plt
import numpy as np
import config
import db_util
from util import timestamp2time
import queue
import logging
import log_config
logger = logging.getLogger(__name__)


pd.set_option('display.max_rows', None)     #当行太多时全部显示
pd.set_option('display.max_colwidth', 500)
# pd.set_option("display.max_columns", None)
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行

#在内存中以dataframe的格式保存k线数据，方便实时展示，只有"1year"中保存实时数据，其他只保存k线周期性数据，以减少内存消耗
# 用于保存所有关心的交易对的k线数据，该数据的前半部分在程序启动时主动请求回来，然后随着时间推移进行更新(追加），所有指标的计算都可以从这里取数据
"""eg:
    {"market.btcusdt.kline.15min": Dataframe["ts", "tick_id", "open", "high", "low", 'close', 'amount', 'vol', 'count']}
"""
KLINE_DATA = {}
REALTIME_PRICE = queue.Queue()
REALTIME_BALANCE = queue.Queue()
TRADE_VOL_HISTORY = {}
ORG_COIN = None
ORG_DOLLAR = None
REALTIME_KDJ = queue.Queue()
REALTIME_UML = queue.Queue()
#所有的K线订阅响应都在此处理
def kline_sub_msg_process(response):
    if not is_valid(response, "sub"):
        return False

    save_data_df(response)

    #保存数据到数据库（optional)
    if config.DB_SAVE:
        save_data_db(response)

    update_realtime_price(response)


#判断response是否有效,type取值 【"sub", "req"】
def is_valid(response, type="sub"):
    if type == "sub":
        if response.get("ch", config.STATUS_ERROR) == config.STATUS_ERROR:
            logger.error("check [sub msg] valid failed: response={}".format(response))
            log_config.output2ui("check [sub msg] valid failed: response={}".format(response), 3)
            return False
    elif type == "req":
        if response.get("status", "") != config.STATUS_OK or response.get("rep", config.STATUS_ERROR) == config.STATUS_ERROR:
            logger.error("check [req msg] valid failed: response={}".format(response))
            log_config.output2ui("check [req msg] valid failed: response={}".format(response), 3)
            return False
    return True


# 历史请求数据保存
def kline_req_msg_process(response):
    if not is_valid(response, "req"):
        return False

    channel = response.get("rep")
    df_kl = KLINE_DATA.get(channel, None)
    if df_kl is None:
        df_kl = pd.DataFrame([], columns=["ts", "tick_id", "open", "high", "low", 'close', 'amount', 'vol', 'count'])
        KLINE_DATA[channel] = df_kl

    pos = len(df_kl)  # 追加
    data_list = response.get("data", [])
    for tick in data_list:
        df_kl.loc[pos] = [tick["id"]*1000, tick["id"], tick["open"],
                           tick["high"], tick["low"], tick["close"],
                           tick["amount"], tick["vol"], tick["count"]]
        pos += 1
    return True


#更新实时价格至queue供界面调用
def update_realtime_price(data):
    symbol = data.get("ch", "ch_error").split(".")[1]
    tick = data.get("tick", None)
    if tick:
        price = {symbol: tick["close"]}
        # print("REALTIME_PRICE put data: {}".format(price))
        REALTIME_PRICE.put(price)


#对订阅响应数据进行保存，存入dataframe, 分实时和k线两部分
def save_data_df(data):
    channel = data.get("ch", "ch_error")
    #判断KLINE_DATA中否已经存在该channel
    ts = data.get("ts", -1)
    tick = data.get("tick", None)
    if not (ts > 0 and tick):
        logger.error("save_data_df failed, data invalid. data = {}".format(data))
        log_config.output2ui("save_data_df failed, data invalid. data = {}".format(data), 3)
        return False

    if config.KL_REALTIME in channel:
        # 如果是KL_REALTIME则直接追加保存
        symbol = channel.split(".")[1]
        df_rt = KLINE_DATA.get(symbol, None)
        if df_rt is None:
            df_rt = pd.DataFrame([], columns=["ts", "tick_id", "open", "high", "low", 'close', 'amount', 'vol',
                                              'count'])
            KLINE_DATA[symbol] = df_rt

        try:
            pos = len(df_rt)
            df_rt.loc[pos] = [ts, tick["id"], tick["open"], tick["high"],
                                     tick["low"], tick["close"], tick["amount"],
                                     tick["vol"], tick["count"]]
        except Exception as e:
            logger.info("pos-1")
            df_rt.loc[pos-1] = [ts, tick["id"], tick["open"], tick["high"],
                                     tick["low"], tick["close"], tick["amount"],
                                     tick["vol"], tick["count"]]
    else:
        df_kl = KLINE_DATA.get(channel, None)
        if df_kl is None:
            df_kl = pd.DataFrame([], columns=["ts", "tick_id", "open", "high", "low", 'close', 'amount', 'vol', 'count'])
            KLINE_DATA[channel] = df_kl

        if df_kl.empty:
            df_kl.loc[0] = [ts, tick["id"], tick["open"],
                            tick["high"], tick["low"], tick["close"],
                            tick["amount"], tick["vol"], tick["count"]]
        else:
            pos = len(df_kl)  # 追加
            # print(df.loc[len(df)-1, 'tick_id'])
            # 在df_kl中只保存k线最后一次数据+最近一条即时数据(除KL_REALTIME除外），不保存实时数据，避免内存占用太大
            # 如果tick_id和df_kl中最后一条相等，则说明是同一个k线的不同时刻，直接覆盖
            if tick["id"] == df_kl.loc[pos-1, 'tick_id']:
                pos = pos-1     #覆盖最后一条

            try:
                df_kl.loc[pos] = [ts, tick["id"], tick["open"], tick["high"],
                                  tick["low"], tick["close"], tick["amount"],
                                  tick["vol"], tick["count"]]
            except Exception as e :
                logger.info("pos-1")
                df_kl.loc[pos - 1] = [ts, tick["id"], tick["open"], tick["high"],
                                      tick["low"], tick["close"], tick["amount"],
                                      tick["vol"], tick["count"]]

    return True


#保存数据到数据库，可以选择不保存，修改config中DB_SAVE=False
def save_data_db(data):
    # {'ch': 'market.btcusdt.kline.5min', 'ts': 1529208725526,
    #  'tick': {'id': 1529208600, 'open': 6527.09, 'close': 6527.03,
    #           'low': 6526.38, 'high': 6527.3, 'amount': 8.403180119396376,
    #           'vol': 54848.91095433597, 'count': 101}}
    try:
        if not (db_util.DB_INSTANCE and db_util.DB_INSTANCE.is_valid()):
            logger.warning("save data failed. DB_INSTANCE is not valid.")
            log_config.output2ui("save data failed. DB_INSTANCE is not valid.", 2)
            return False

        if not isinstance(data, dict):
            data = dict(data)

        collection_name = data.get("ch").split(".")[1]
        db = db_util.DB_INSTANCE.db
        logger.info("save data, collection_name: {}, data: {}".format(collection_name, data))
        log_config.output2ui("save data, collection_name: {}, data: {}".format(collection_name, data))
        db.get_collection(collection_name).insert_one(data)
    except Exception as e:
        logger.exception("save data catch exception: {}".format(e))
        log_config.output2ui("save data catch exception: {}".format(e), 4)



#根据给定的数据绘制k线图，type取值0-"show",1-"pic", 2-"both"】
def plot_candle_chart(df, type=0, pic_name='candle_chart'):
    # 对数据进行整理
    # df.set_index(df['tick_id'], drop=True, inplace=True)
    # df = df[['open', 'high', 'low', 'close']]

    # 作图
    ll = np.arange(0, len(df), 1)
    x_times = []
    for row in ll:
        tick_id = df.loc[row, 'tick_id']
        x_times.append(timestamp2time(tick_id, precision="minute"))
    # xticks = df.index[ll]
    print(x_times)
    xticks = x_times

    fig, ax = plt.subplots()
    candlestick2_ohlc(ax, df['open'].values, df['high'].values, df['low'].values, df['close'].values,
                      width=0.6, colorup='r', colordown='g', alpha=1)

    #eg:xticks(np.arange(12), calendar.month_name[1:13], rotation=20)
    plt.xticks(ll, xticks, rotation=60)
    plt.title(pic_name)
    plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)

    # 保存数据
    if type == 0:
        plt.show()
    elif type == 1:
        plt.savefig("picture//" + pic_name + ".png")
    else:
        plt.savefig("picture//" + pic_name + ".png")
        plt.show()



if __name__ == '__main__':
    pass