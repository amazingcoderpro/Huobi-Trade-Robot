#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/18
# Function: 

KLINE_MAP = {}  #用于保存所有关心的交易对的k线数据，该数据在程序启动时主动请求回来，然后按照不同的周期进行更新，所有指标的计算都可以从这里取数据
"""eg:
    {"market.btcusdt.kline.15min": Dataframe}
"""
REAL_TIME_MAP = {} #保存实时数据，可以认为是秒级更新，程序启动时发起订阅，该数据来服务器推送
"""eg:
    {"btcusdt":DataFrame["open", "close", "high"][6521, 6518, 6522....]}"""
if __name__ == '__main__':
    pass