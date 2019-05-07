#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/7/1
# Function:

from tkinter import Toplevel, Label, Button, Entry, StringVar, IntVar, Checkbutton, LEFT, RIGHT, Frame, messagebox, OptionMenu, DoubleVar
import log_config


class PopupStrategy(Toplevel):
    def __init__(self, move_stop_profit_params,
                 stop_loss_params,
                 kdj_buy_params,
                 kdj_sell_params,
                 vol_price_fly_params,
                 boll_params,
                 title="Strategy Configuration"):
        Toplevel.__init__(self)
        self.is_ok = False
        self.vol_price_fly_params = vol_price_fly_params
        self.kdj_sell_params = kdj_sell_params
        self.kdj_buy_params = kdj_buy_params
        self.stop_loss_params = stop_loss_params
        self.move_stop_profit_params = move_stop_profit_params
        self.boll_params = boll_params

        self.msf_min = DoubleVar()
        self.msf_min.set(self.move_stop_profit_params["msf_min"])
        self.msf_back = DoubleVar()
        self.msf_back.set(self.move_stop_profit_params["msf_back"])
        self.stop_loss = DoubleVar()
        self.stop_loss.set(self.stop_loss_params["percent"])
        self.k_buy = DoubleVar()
        self.k_buy.set(self.kdj_buy_params["k"])
        self.d_buy = DoubleVar()
        self.d_buy.set(self.kdj_buy_params["d"])
        self.kdj_buy_percent = DoubleVar()
        self.kdj_buy_percent.set(self.kdj_buy_params["buy_percent"])
        self.kdj_up_percent = DoubleVar()
        self.kdj_up_percent.set(self.kdj_buy_params["up_percent"])

        self.k_sell = DoubleVar()
        self.k_sell.set(self.kdj_sell_params["k"])
        self.d_sell = DoubleVar()
        self.d_sell.set(self.kdj_sell_params["d"])
        self.kdj_sell_percent = DoubleVar()
        self.kdj_sell_percent.set(self.kdj_sell_params["sell_percent"])
        self.kdj_down_percent = DoubleVar()
        self.kdj_down_percent.set(self.kdj_sell_params["down_percent"])

        self.vol_percent = DoubleVar()
        self.vol_percent.set(self.vol_price_fly_params["vol_percent"])
        self.vol_buy_sell = DoubleVar()
        self.vol_buy_sell.set(self.vol_price_fly_params["high_than_last"])
        self.price_up_limit = DoubleVar()
        self.price_up_limit.set(self.vol_price_fly_params["price_up_limit"])
        self.vol_buy_percent = DoubleVar()
        self.vol_buy_percent.set(self.vol_price_fly_params["buy_percent"])

        # move_stop_profit = {"msf_min": 0.02, "msf_back": 0.03}
        # stop_loss = {"percent": 0.03}
        # kdj_buy = {"k": 18, "d": 20, "buy_percent": 0.1}
        # kdj_sell = {"k": 85, "d": 80, "sell_percent": 0.1}
        # vol_price_fly = {"vol_percent": 1.1, "vol_buy_sell": 1.1, "price_up_limit": 0.03, "buy_percent": 0.2}
        self.setup_ui()
        self.title(title)

    def setup_ui(self):
        row1 = Frame(self)
        row1.pack(fill="x")

        self.ckb_stop_profit_val = IntVar(value=self.move_stop_profit_params.get("check", 1))
        self.ckb_stop_profit = Checkbutton(row1, text='', variable=self.ckb_stop_profit_val, onvalue=1, offvalue=0).pack(side=LEFT)
        Label(row1, text="移动止盈:").pack(side=LEFT)

        row1 = Frame(self)
        row1.pack(fill="x")
        Label(row1, text="最小赢利: ", width=15).pack(side=LEFT)
        Entry(row1, textvariable=self.msf_min, width=15).pack(side=LEFT)
        Label(row1, text="回撤幅度: ", width=15).pack(side=LEFT)
        Entry(row1, textvariable=self.msf_back, width=15).pack(side=LEFT)

        row2 = Frame(self)
        row2.pack(fill="x", ipadx=1, ipady=1)
        self.ckb_stop_loss_val = IntVar(value=self.stop_loss_params.get("check", 1))
        self.ckb_stop_loss = Checkbutton(row2, text='', variable=self.ckb_stop_loss_val, onvalue=1, offvalue=0).pack(side=LEFT)
        Label(row2, text="亏损风险控制: ").pack(side=LEFT)
        Entry(row2, textvariable=self.stop_loss, width=45).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x", ipadx=1, ipady=1)
        self.ckb_kdj_buy_val = IntVar(value=self.kdj_buy_params.get("check", 1))
        self.ckb_kdj_buy = Checkbutton(row3, text='', variable=self.ckb_kdj_buy_val, onvalue=1, offvalue=0).pack(side=LEFT)
        Label(row3, text="KDJ买入参考: ").pack(side=LEFT)

        row4 = Frame(self)
        row4.pack(fill="x", ipadx=1, ipady=1)
        Label(row4, text="K小于等于: ", width=10).pack(side=LEFT)
        Entry(row4, textvariable=self.k_buy, width=5).pack(side=LEFT)
        Label(row4, text="D小于等于: ", width=10).pack(side=LEFT)
        Entry(row4, textvariable=self.d_buy, width=5).pack(side=LEFT)
        Label(row4, text="买入比例: ", width=10).pack(side=LEFT)
        Entry(row4, textvariable=self.kdj_buy_percent, width=5).pack(side=LEFT)
        Label(row4, text="回暖幅度: ", width=10).pack(side=LEFT)
        Entry(row4, textvariable=self.kdj_up_percent, width=5).pack(side=LEFT)
        Label(row4, text="周期: ").pack(side=LEFT)
        lst_trade = ['5min', '15min', '30min', '1day']
        # self.trade.set(lst_trade[0])
        self.kdj_buy_peroid = StringVar()
        self.kdj_buy_peroid.set(self.kdj_buy_params.get("peroid", "15min"))
        OptionMenu(row4, self.kdj_buy_peroid, *lst_trade).pack(side=LEFT)

        row5 = Frame(self)
        row5.pack(fill="x", ipadx=1, ipady=1)
        self.ckb_kdj_sell_val = IntVar(value=self.kdj_sell_params.get("check", 1))
        self.ckb_kdj_sell = Checkbutton(row5, text='', variable=self.ckb_kdj_sell_val, onvalue=1, offvalue=0).pack(side=LEFT)
        Label(row5, text="KDJ卖出参考: ").pack(side=LEFT)

        row6 = Frame(self)
        row6.pack(fill="x", ipadx=1, ipady=1)
        Label(row6, text="K大于等于: ", width=10).pack(side=LEFT)
        Entry(row6, textvariable=self.k_sell, width=5).pack(side=LEFT)
        Label(row6, text="D大于等于: ", width=10).pack(side=LEFT)
        Entry(row6, textvariable=self.d_sell, width=5).pack(side=LEFT)
        Label(row6, text="卖出比例: ", width=10).pack(side=LEFT)
        Entry(row6, textvariable=self.kdj_sell_percent, width=5).pack(side=LEFT)
        Label(row6, text="回撤幅度: ", width=10).pack(side=LEFT)
        Entry(row6, textvariable=self.kdj_down_percent, width=5).pack(side=LEFT)
        Label(row6, text="周期: ").pack(side=LEFT)
        lst_trade = ['5min', '15min', '30min', '1day']
        # self.trade.set(lst_trade[0])
        self.kdj_sell_peroid = StringVar()
        self.kdj_sell_peroid.set(self.kdj_sell_params.get("peroid", "15min"))
        OptionMenu(row6, self.kdj_sell_peroid, *lst_trade).pack(side=LEFT)

        row5 = Frame(self)
        row5.pack(fill="x", ipadx=1, ipady=1)
        self.ckb_vol_price_val = IntVar(value=self.vol_price_fly_params.get("check", 1))
        self.ckb_vol_price_buy = Checkbutton(row5, text='', variable=self.ckb_vol_price_val, onvalue=1, offvalue=0).pack(side=LEFT)

        Label(row5, text="量价齐升: ").pack(side=LEFT)
        row6 = Frame(self)
        row6.pack(fill="x", ipadx=1, ipady=1)
        Label(row6, text="总量0-3比3-7: ", width=12).pack(side=LEFT)
        Entry(row6, textvariable=self.vol_percent, width=5).pack(side=LEFT)
        Label(row6, text="周期量比: ", width=15).pack(side=LEFT)
        Entry(row6, textvariable=self.vol_buy_sell, width=5).pack(side=LEFT)
        Label(row6, text="风险控制: ", width=10).pack(side=LEFT)
        Entry(row6, textvariable=self.price_up_limit, width=5).pack(side=LEFT)
        Label(row6, text="买入比例: ", width=10).pack(side=LEFT)
        Entry(row6, textvariable=self.vol_buy_percent, width=5).pack(side=LEFT)

        row5 = Frame(self)
        row5.pack(fill="x", ipadx=1, ipady=1)
        self.ckb_boll_buy_val = IntVar(value=self.boll_params.get("check", 1))
        self.ckb_boll_buy = Checkbutton(row5, text='', variable=self.ckb_boll_buy_val, onvalue=1, offvalue=0).pack(side=LEFT)

        Label(row5, text="BOLL买入参考: ").pack(side=LEFT)
        self.open_diff1_percent = DoubleVar()
        self.open_diff1_percent.set(self.boll_params["open_diff1_percent"])
        self.open_diff2_percent = DoubleVar()
        self.open_diff2_percent.set(self.boll_params["open_diff2_percent"])

        self.close_diff1_percent = DoubleVar()
        self.close_diff1_percent.set(self.boll_params["close_diff1_percent"])
        self.close_diff2_percent = DoubleVar()
        self.close_diff2_percent.set(self.boll_params["close_diff2_percent"])

        self.open_down_percent = DoubleVar()
        self.open_down_percent.set(self.boll_params["open_down_percent"])

        self.open_up_percent = DoubleVar()
        self.open_up_percent.set(self.boll_params["open_up_percent"])

        self.open_buy_percent = DoubleVar()
        self.open_buy_percent.set(self.boll_params["open_buy_percent"])

        row6 = Frame(self)
        row6.pack(fill="x", ipadx=1, ipady=1)
        Label(row6, text="开上中轨差比例: ", width=15).pack(side=LEFT)
        Entry(row6, textvariable=self.open_diff1_percent, width=10).pack(side=LEFT)
        Label(row6, text="开中下轨差比例: ", width=15).pack(side=LEFT)
        Entry(row6, textvariable=self.open_diff2_percent, width=10).pack(side=LEFT)

        row6 = Frame(self)
        row6.pack(fill="x", ipadx=1, ipady=1)
        Label(row6, text="闭上中轨差比例: ", width=15).pack(side=LEFT)
        Entry(row6, textvariable=self.close_diff1_percent, width=10).pack(side=LEFT)
        Label(row6, text="闭中下轨差比例: ", width=15).pack(side=LEFT)
        Entry(row6, textvariable=self.close_diff2_percent, width=10).pack(side=LEFT)

        row6 = Frame(self)
        row6.pack(fill="x", ipadx=1, ipady=1)
        Label(row6, text="开口跌幅小于: ", width=15).pack(side=LEFT)
        Entry(row6, textvariable=self.open_down_percent, width=5).pack(side=LEFT)

        Label(row6, text="超跌回暖幅度大于: ", width=15).pack(side=LEFT)
        Entry(row6, textvariable=self.open_up_percent, width=5).pack(side=LEFT)

        Label(row6, text="买入比例: ", width=10).pack(side=LEFT)
        Entry(row6, textvariable=self.open_buy_percent, width=5).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x")
        # Button(row3, text="Reset", command=lambda: self.on_reset(), width=10).pack(side=RIGHT)
        Button(row3, text="Cancel", command=lambda: self.on_cancel(), width=10).pack(side=RIGHT)
        Button(row3, text="OK", command=lambda: self.on_ok(), width=10).pack(side=RIGHT)

    def on_ok(self):
        try:
            msf_min = float(self.msf_min.get())
            msf_back = float(self.msf_back.get())
            stop_loss = float(self.stop_loss.get())
            k_buy = float(self.k_buy.get())
            d_buy = float(self.d_buy.get())
            kdj_buy_percent = float(self.kdj_buy_percent.get())
            k_sell = float(self.k_sell.get())
            d_sell = float(self.d_sell.get())
            kdj_sell_percent = float(self.kdj_sell_percent.get())
            vol_percent = float(self.vol_percent.get())
            vol_buy_sell = float(self.vol_buy_sell.get())
            price_up_limit = float(self.price_up_limit.get())
            vol_buy_percent = float(self.vol_buy_percent.get())

            open_diff1_percent = float(self.open_diff1_percent.get())
            open_diff2_percent = float(self.open_diff2_percent.get())

            close_diff1_percent = float(self.close_diff1_percent.get())
            close_diff2_percent = float(self.close_diff2_percent.get())

            open_down_percent = float(self.open_down_percent.get())
            open_up_percent = float(self.open_up_percent.get())

            open_buy_percent = float(self.open_buy_percent.get())

        except Exception as e:
            messagebox.showwarning("Warning", "All parameters must be numeric and cannot be null!")  # 提出警告对话窗
            return

        self.move_stop_profit_params["check"] = int(self.ckb_stop_profit_val.get())
        self.move_stop_profit_params["msf_min"] = msf_min
        self.move_stop_profit_params["msf_back"] = msf_back

        self.stop_loss_params["percent"] = stop_loss
        self.stop_loss_params["check"] = int(self.ckb_stop_loss_val.get())

        self.kdj_buy_params["check"] = int(self.ckb_kdj_buy_val.get())
        self.kdj_buy_params["k"] = k_buy
        self.kdj_buy_params["d"] = d_buy
        self.kdj_buy_params["buy_percent"] = kdj_buy_percent
        self.kdj_buy_params["up_percent"] = float(self.kdj_up_percent.get())
        self.kdj_buy_params["peroid"] = str(self.kdj_buy_peroid.get())

        self.kdj_sell_params["check"] = int(self.ckb_kdj_sell_val.get())
        self.kdj_sell_params["k"] = k_sell
        self.kdj_sell_params["d"] = d_sell
        self.kdj_sell_params["sell_percent"] = kdj_sell_percent
        self.kdj_sell_params["down_percent"] = float(self.kdj_down_percent.get())
        self.kdj_sell_params["peroid"] = str(self.kdj_sell_peroid.get())

        self.vol_price_fly_params["check"] = int(self.ckb_vol_price_val.get())
        self.vol_price_fly_params["vol_percent"] = vol_percent
        self.vol_price_fly_params["high_than_last"] = vol_buy_sell
        self.vol_price_fly_params["price_up_limit"] = price_up_limit
        self.vol_price_fly_params["buy_percent"] = vol_buy_percent

        self.boll_params["check"] = int(self.ckb_boll_buy_val.get())
        self.boll_params["open_diff1_percent"] = open_diff1_percent
        self.boll_params["open_diff2_percent"] = open_diff2_percent
        self.boll_params["close_diff1_percent"] = close_diff1_percent
        self.boll_params["close_diff2_percent"] = close_diff2_percent
        self.boll_params["open_down_percent"] = open_down_percent
        self.boll_params["open_up_percent"] = open_up_percent
        self.boll_params["open_buy_percent"] = open_buy_percent
        # self.value_dict["access_key"] = access_key.strip().replace("\n", "")
        # self.value_dict["secret_key"] = secret_key.strip().replace("\n", "")
        messagebox.showinfo("Info", "Strategy change have taken effect！")
        log_config.output2ui("Setup strategy successfully!", 8)
        self.destroy()

    def on_cancel(self):
        self.destroy()

    def on_reset(self):
        self.msf_back.set(0.02)


if __name__ == '__main__':
    value_dict = {}
    PopupStrategy(value_dict, "策略配置")
