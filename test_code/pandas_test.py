# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # Created by Charles on 2018/6/14
# # Function:
#
# import pandas as pd
# from mpl_finance import candlestick2_ohlc
# import matplotlib.pyplot as plt
# import numpy as np
#
# s = pd.Series([1,2,3,4], index=["open", "high", "low", "close"])
# s2 = pd.Series([2,3,4,5])
# s.append(s2)
# print(s)
# d = pd.DataFrame([[1,2,3], [4,5,6]], columns=["a", "b", "c"])
# d = d.append([3,4,5])
# d.plot()
# print(d.describe())
#
# def plot_candle_chart(df, pic_name='candle_chart'):
#
#     # 对数据进行整理
#     # df.set_index(df['交易日期'], drop=True, inplace=True)
#
#     df = df[['open', 'high', 'low', 'close']]
#
#     # 作图
#     ll = np.arange(0, len(df), 1)
#     # my_xticks = df.index[ll].date
#
#     fig, ax = plt.subplots()
#
#     candlestick2_ohlc(ax, df['open'].values, df['high'].values, df['low'].values, df['close'].values,
#                       width=0.6, colorup='r', colordown='g', alpha=1)
#
#     # plt.xticks(ll, my_xticks)
#     plt.xticks(rotation=60)
#
#     plt.title(pic_name)
#
#     plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
#
#     # 保存数据
#     plt.savefig(pic_name+'.png')
#
# def test_drop():
#     dw = pd.DataFrame([[1, 0, 3], [1, 5, 6], [4, 2, 5],[5, 2, 5],[6, 2, 5],[7, 2, 5]], columns=["a", "b", "c"])
#     lt = len(dw)
#     dw.drop([1,2,3], inplace=True)
#     # dw.reset_index(drop=True, inplace=True)
#     print(dw)
#     dw.loc[len(dw)]=[99,4,9]
#     print(dw)
#     print(float(dw.tail(1)["a"]))
#
#     tpdf = dw.loc[dw["b"]>1]
#     print(tpdf)
#     tpdf2=tpdf[tpdf["b"]<4]
#     print(tpdf2)
#     print(tpdf[tpdf["b"]<10].c.max())
#     # print(dw.loc[dw["b"]>20].c.max())
#
# def test_duplicate():
#     dw = pd.DataFrame([[1, 2, 3], [1, 5, 6], [4, 2, 5]], columns=["a", "b", "c"])
#
#     current_price = dw.loc[len(dw)-1, "a"]
#     print(current_price)
#     current_price = dw.tail(1)["a"]
#     print(current_price)
#
#     print(dw)
#     dd = dw[['a', 'c']][dw.a > 1]
#     print(dd)
#     exit(1)
#
#     print(dw.head(len(dw)))
#     print("-------------")
#     result = dw.duplicated()
#     print(result)
#
#     di = dw.duplicated('a')
#     print(di)
#     di = dw.duplicated(['a', 'b'])
#     print(di)
#     print(dw[di])
#     a = dw.loc[len(dw) - 1]["a"]
#     new_dw = dw.drop_duplicates('a').reset_index(drop=True)
#
#     print(new_dw)
#     a = dw.loc[len(dw) - 1]["a"]
#     a = new_dw.loc[len(dw) -2, "a"]
#     # df = new_dw.reset_index(drop=True)
#     # a = df.loc[len(df)-2]["a"]
#     # print(df)
#     print(dw)
#
# if __name__ == '__main__':
#     # df = pd.read_csv("sh600000.csv")
#     # plot_candle_chart(df)
#
#     test_drop()