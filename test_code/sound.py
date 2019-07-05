#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/7/23
# Function: 


# import win32com.client
# import winsound
# speak = win32com.client.Dispatch('SAPI.SPVOICE')
# winsound.Beep(2015, 3000)
# winsound.MessageBeep(winsound.MB_OK)
# speak.Speak('程序运行完毕!')

# if __name__ == '__main__':
#     pass
# import queue
# aq = queue.Queue(maxsize=2)
# aq.put(1)
# print(11)
# aq.put(2, block=False)
# print(22)
# print(aq.get(block=False))
import json
import requests
import sqlite3
import datetime

def encode_str(source="123456"):
    import hashlib
    sha = hashlib.sha256()
    sha.update(str(source).encode("utf-8"))
    encode_source = sha.hexdigest()
    print(encode_source)
    return encode_source

# data = {"account": "17502964994", "password": encode_str("123456")}
# json_data = json.dumps(data)
# headers = {'Content-Type': 'application/json'}
# url = "http://127.0.0.1:5000/huobi/login/"
# ret = requests.post(url=url, headers=headers, data=json_data)
# print(ret.status_code)
#
# print(json.loads(ret.text))

# if __name__ == '__main__':
#     encode_str()
def test_sqlite():

    conn = sqlite3.connect("ddu.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute(
        "create table if not exists trade(id integer primary key autoincrement, buy_type varchar(128), "
        "sell_type varchar(128), limit_profit real, back_profit real, track integer, buy_time timestamp, "
        "sell_time timestamp, coin varchar(10), money varchar(10), amount real, buy_price real, cost real, "
        "is_sell integer, sell_price real, profit_percent real, profit real)")
    cursor.execute('insert into trade values(?, ?, ?, ?, ?)', (None, 'auto', 'profit', -0.051, datetime.datetime.now()))
    conn.commit()

    cursor.execute('select * from trade')
    print(cursor.fetchall())


def format_float(num, pos=2):
    if pos <= 0:
        return int(num)

    num_split = str(num).split('.')
    if len(num_split) == 1:
        return num

    num = float(num_split[0] + '.' + num_split[1][0:pos])
    return num

print(format_float(23, 7))

retry = 3
num = 23.2346
while retry>=0:
    if retry == 0:
        print("aaa")
        break
    else:
        print(format_float(num, retry-1))
        retry -=1

def sort_list():
    import datetime
    tt_list = [{"is_sell": 1, "end_time": None, "last_update": datetime.datetime.now()+datetime.timedelta(seconds=10)}, {"is_sell": 0, "last_update": datetime.datetime.now()}, {"is_sell": 1, "last_update": datetime.datetime.now()+datetime.timedelta(seconds=20)}]
    tt_list_not_selled = list(filter(lambda x: x["is_sell"] == 0, tt_list))
    tt_list_not_selled.sort(key=lambda x: x["last_update"], reverse=False)

    tt_list_selled = list(filter(lambda x:x["is_sell"]==1, tt_list))
    tt_list_selled.sort(key=lambda x: x["last_update"], reverse=False)

    new_list = []
    # new_list.append(tt_list_not_selled)
    # new_list.append(tt_list_selled)
    # print(new_list)
    tt_list_not_selled += tt_list_selled[0:1]
    print(tt_list)


# 单次交易信息，这样的一次交易记录，将被包含在一组执行单元中, 除非是手动买入的
TRADE = {
    "buy_type": "auto",         # 买入模式：auto 自动买入(机器策略买入)，man手动买入,
    "sell_type": "profit",      # 要求的卖出模式，机器买入的一般都为止盈卖出。可选：profit 止盈卖出（默认）， no-不要卖出，针对手动买入的单，smart-使用高抛，kdj等策略卖出
    "limit_profit": -1,              # 大于零代表使用当前的盈利比例，否则使用所属交易组的盈利比例
    "back_profit": -1,               # 追踪回撤系数, 同上
    "track": -1,                     # 是否追踪止盈，同上
    "buy_time": None,
    "sell_time": None,
    "coin": "EOS",
    "money": "USDT",
    "amount": 0,              # 买入或卖出的币量
    "buy_price": 0,            # 实际买入成交的价格
    "cost": 0,               # 实际花费的计价货币量
    "is_sell": 0,           # 是否已经卖出
    "sell_price": 0,        # 实际卖出的价格
    "profit_percent": 0,    # 盈利比，卖出价格相对于买入价格
    "profit": 0,            # 盈利额，只有卖出后才有
    "failed_times": 0,
    "uri": ""
}


# 一组执行单元，买和卖都在里面
TRADE_GROUP = {
    "build": "smart",           # 建仓触发模式smart－－智能建仓，　auto－－自动建仓
    "mode": "",                  #robust,keep..按何种交易风格执行，　若未设置，则默认使用全局的交易参数，
    "smart_profit": -1,  # 是否启用智能止盈
    "smart_patch": -1,  # 是否启用智能补仓
    "patch_mode": "",  # 补仓的模式，默认为倍投

    "coin": "",             #EOS等　
    "money": "",        #USDT等　
    "trades": [TRADE],            # 每一次交易记录，
    "grid": -1,              # 是否开启网格交易, 小于零代表使用全局配置
    "track": -1,             # 是否开启追踪止盈, 小于零代表使用全局配置
    "amount": 0,         # 持仓数量（币）
    "cost": 0,           # 当前持仓费用（计价货币）
    "avg_price": 0,      # 持仓均价
    "max_cost": 0,      # 这组交易中最多时持仓花费，用于计算收益比
    "profit": 0,        # 这组策略的总收益， 每次卖出后都进行累加
    "profit_percent": 0,    # 整体盈利比（整体盈利比，当前总盈利数除以最大花费,　total_profit_amount/max_cost）
    "last_profit_percent": 0,   # 尾单盈利比（最后一单的盈利比）
    "limit_profit": -1,      # 止盈比例，　可单独设置，如果未设置（-1），则使用当前所选择的交易策略的止盈比例
    "back_profit": -1,       # 追踪比例，　可单独设置，如果未设置（-1），则使用当前所选择的交易策略的追踪比例
    "buy_counts": 0,             # 已建单数，买入次数
    "sell_counts": 0,            # 卖出单数，卖出的次数，其实就是尾单收割次数
    "patch_index": 0,           # 当前补单序号，每买入一单后，path_index加上，　每卖出一单后，pathc_index减1
    "patch_ref": -1,             # 补仓参考，0--整体均价，１－－参考上一单买入价格，　小于零代表使用全局
    "patch_interval": -1,     # 补仓间隔，　小于零代表使用全局
    "last_buy_price": 0,    # 最后一次买入价格，补仓时有可能会选择参考上次买入价，如果上一单已经卖出，那么参考上上一单，以此类推
    "start_time": None,     # 建仓时间
    "end_time": None,       # 如果为none代表还未结束
    "last_update": None,
    "uri": "",  # 唯一标识，建仓时间加随机数，如20190608123012336
    "principal": -1, #当前这组交易的预算,未单独设置的话(小于零)，则默认为全局本金预算除以监控的币对数，
    "last_sell_failed": None,
    "sell_out": 0,
    "is_sell": 0,
    "stop_patch": 0
}

def update_trade_info_to_db():
    try:
        conn = sqlite3.connect("ddu.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        # trade
        cursor.execute(
            """create table if not exists trade(id integer primary key autoincrement, buy_type varchar(128), sell_type varchar(128), limit_profit real, back_profit real, track integer, buy_time timestamp, sell_time timestamp, coin varchar(10), money varchar(10), amount real, buy_price real, cost real, is_sell integer, sell_price real, profit_percent real, profit real, failed_times integer, uri varchar(100), group_uri varchar(100))""")

        # trade_group
        cursor.execute(
            "create table if not exists trade_group(id integer primary key autoincrement, build varchar(20), mode varchar(20), smart_profit integer,"
            "smart_patch integer, patch_mode varchar(20), coin varchar(20), money varchar(20), grid integer, track integer, amount real, cost real,"
            "avg_price real, max_cost real, profit real, profit_percent real, last_profit_percent real, limit_profit real, back_profit real, "
            "buy_counts integer, sell_counts integer, patch_index integer, patch_ref integer, patch_interval real, last_buy_price real, "
            "start_time timestamp, end_time timestamp, last_update, uri varchar(100), principal real, last_sell_failed timestamp, sell_out integer,"
            "is_sell integer, stop_patch integer, user_name varchar(128))")

        # user
        cursor.execute(
            "create table if not exists user(id integer primary key autoincrement, name varchar(128), password varchar(128), api_key varchar(128),"
            "secret_key varchar(128))")

        # api key
        cursor.execute(
            "create table if not exists api_key(id integer primary key autoincrement, user_name varchar(128), platform varchar(20), api_key varchar(128),"
            "track integer, grid integer, smart_first integer, smart_profit integer, smart_patch integer, patch_mode varchar(20), patch_interval real,"
            "patch_ref integer)")

        # trade_mode
        cursor.execute(
            "create table if not exists trade_mode(id integer primary key autoincrement, mode varchar(20), limit_profit real, back_profit real,"
            "secret_key varchar(128), user_name varchar(128))")

        cursor.execute('select uri from trade_group where id>=0')
        group_uris = []
        results = cursor.fetchall()
        if results:
            for res in results:
                group_uris.append(res[0])

        cursor.execute('select uri from trade where id>=0')
        trade_uris = []
        results = cursor.fetchall()
        if results:
            for res in results:
                trade_uris.append(res[0])

        for group in [TRADE_GROUP]:
            if group.get("uri", "") not in group_uris:
                cursor.execute('insert into `trade_group` values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           (None, group.get("build", ""), group.get("mode", ""),  group.get("smart_profit", -1), group.get("smart_patch", -1),
                            group.get("patch_mode", ""), group.get("coin", ""), group.get("money", ""), group.get("grid", -1),
                            group.get("track", -1), group.get("amount", 0), group.get("cost", 0), group.get("avg_price", 0),
                            group.get("max_cost", 0), group.get("profit", 0), group.get("profit_percent", 0),
                            group.get("last_profit_percent", 0),group.get("limit_profit", -1),group.get("back_profit", -1),
                            group.get("buy_counts", 0), group.get("sell_counts", 0), group.get("patch_index", 0),
                            group.get("patch_ref", -1), group.get("patch_interval", -1), group.get("last_buy_price", 0), group.get("start_time", None),
                            group.get("end_time", None), group.get("last_update", None),group.get("uri", ''), group.get("principal", -1),
                            group.get("last_sell_failed", None), group.get("sell_out", 0), group.get("is_sell", 0), group.get("stop_patch", 0),
                            "aaaaaaaaaaaaa"))
            else:
                cursor.execute('update `trade_group` set build=?, mode=?, smart_profit=?, smart_patch=?, patch_mode=?, grid=?, '
                               'track=?, amount=?, cost=?, avg_price=?, max_cost=?, profit=?, profit_percent=?, '
                               'last_profit_percent=?, limit_profit=?, back_profit=?, buy_counts=?, sell_counts=?, patch_index=?, '
                               'patch_ref=?, patch_interval=?, last_buy_price=?, start_time=?, end_time=?, last_update=?, '
                               'principal=?, last_sell_failed=?, sell_out=?, stop_patch=? where uri=?',
                           (group.get("build", ""), group.get("mode", ""),  group.get("smart_profit", -1), group.get("smart_patch", -1),
                            group.get("patch_mode", ""), group.get("grid", -1),
                            group.get("track", -1), group.get("amount", 0), group.get("cost", 0), group.get("avg_price", 0),
                            group.get("max_cost", 0), group.get("profit", 0), group.get("profit_percent", 0),
                            group.get("last_profit_percent", 0),group.get("limit_profit", -1),group.get("back_profit", -1),
                            group.get("buy_counts", 0), group.get("sell_counts", 0), group.get("patch_index", 0),
                            group.get("patch_ref", -1), group.get("patch_interval", -1), group.get("last_buy_price", 0), group.get("start_time", None),
                            group.get("end_time", None), group.get("last_update", None), group.get("principal", -1),
                            group.get("last_sell_failed", None), group.get("sell_out", 0), group.get("stop_patch", 0), group.get("uri", '')))

            trades = group.get("trades", [])
            for trade in trades:
                if trade.get("uri", "") not in trade_uris:
                    cursor.execute("insert into `trade` values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, trade.get("buy_type", ""), trade.get("sell_type", ""),
                                                                           trade.get("limit_profit", -1), trade.get("back_profit", -1),
                                                                           trade.get("track", -1), trade.get("buy_time", None),
                                                                           trade.get("sell_time", None), trade.get("coin", ""),
                                                                           trade.get("money", ""), trade.get("amount", 0),
                                                                           trade.get("buy_price", 0), trade.get("cost", 0),
                                                                           trade.get("is_sell", 0), trade.get("sell_price", 0),
                                                                           trade.get("profit_percent", 0), trade.get("profit", 0),
                                                                           trade.get("failed_times", 0), trade.get("uri", ""),
                                                                           group.get("uri", "")))
                else:
                    cursor.execute("update `trade` set buy_type=?, sell_type=?, limit_profit=?, back_profit=?, track=?,"
                                   "buy_time=?, sell_time=?, amount=?, buy_price=?, cost=?, is_sell=?, sell_price=?, "
                                   "profit_percent=?, profit=?, failed_times=? where uri=?", (trade.get("buy_type", ""), trade.get("sell_type", ""),
                                                                           trade.get("limit_profit", -1), trade.get("back_profit", -1),
                                                                           trade.get("track", -1), trade.get("buy_time", None),
                                                                           trade.get("sell_time", None), trade.get("amount", 0),
                                                                           trade.get("buy_price", 0), trade.get("cost", 0),
                                                                           trade.get("is_sell", 0), trade.get("sell_price", 0),
                                                                           trade.get("profit_percent", 0), trade.get("profit", 0),
                                                                           trade.get("failed_times", 0), trade.get("uri", "")))
        conn.commit()

    except Exception as e:
        pass
    finally:
        conn.close()

    # cursor.execute('select * from trade_group')
    # result = cursor.fetchall()
    # if result:
    #     for res in result:
    #         print(res)

if __name__ == '__main__':
    # test_sqlite()
    sort_list()
    update_trade_info_to_db()