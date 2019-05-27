#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/16
# Function: 
import pandas as pd
import numpy as np
# import talib
# import tushare as ts
# from matplotlib import rc
# import matplotlib.pyplot as plt
# rc('mathtext', default='regular')
# import seaborn as sns
# sns.set_style('white')
#
# dw = ts.get_k_data("600600")
# close = dw.close.values
# print(close)
# dw['macd'], dw['macdsignal'], dw['macdhist'] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
# dw[['close','macd','macdsignal','macdhist']].plot()
#
# fg = plt.figure(figsize=[8,12])
# # plt.plot(dw.index, dw["close"], label="close")
# # plt.plot(dw.index, dw["macd"], label="macd")
# plt.show()
# fig, ax = plt.subplots()
# plt.savefig("macd.png")
# # if __name__ == '__main__':
# # #     pass
# # macd = 12 天 EMA - 26 天 EMA,  ==== DIF
# # signal = 9 天 MACD的EMA   ===== DEA
# # hist = MACD - MACD signal  =====  hist