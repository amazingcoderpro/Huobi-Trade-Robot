#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2019/5/7
# Function:

from tkinter import Toplevel, Label, Button, Entry, StringVar, IntVar, Checkbutton, LEFT, RIGHT, Frame, messagebox, OptionMenu, DoubleVar
import log_config
import logging
logger = logging.getLogger(__name__)

class PopupSystem(Toplevel):
    def __init__(self, value_dict, title="System Configuration"):
        Toplevel.__init__(self)
        self.is_ok = False
        self.value_dict = value_dict
        is_email, is_wechat, is_alarm, trade_min, trade_max, wait_buy_price, \
        wait_buy_account, wait_sell_price, wait_sell_amount, alarm_time, alarm_trade = value_dict.get("is_email", True), value_dict.get("is_wechat", True), value_dict.get("is_alarm", False), \
                                                   value_dict.get("trade_min", 10), value_dict.get("trade_max", 1000), value_dict.get("wait_buy_price"), \
                                                              value_dict.get("wait_buy_account"), value_dict.get("wait_sell_price"), value_dict.get("wait_sell_account"), value_dict.get("alarm_time", 30), value_dict.get("is_alarm_trade", True)

        self.trade_min = DoubleVar()
        self.trade_min.set(trade_min)
        self.trade_max = DoubleVar()
        self.trade_max.set(trade_max)

        self.is_email = StringVar()
        self.is_email.set('YES' if is_email else 'NO')

        self.is_wechat = StringVar()
        self.is_wechat.set('YES' if is_email else 'NO')

        self.is_alarm = StringVar()
        self.is_alarm.set('YES' if is_alarm else 'NO')

        self.alarm_time = DoubleVar()
        self.alarm_time.set(alarm_time)

        self.alarm_trade = StringVar()
        self.alarm_trade.set('YES' if alarm_trade else 'NO')



        self.wait_buy_price1 = DoubleVar()
        self.wait_buy_price1.set(wait_buy_price[0])
        self.wait_buy_account1 = DoubleVar()
        self.wait_buy_account1.set(wait_buy_account[0])

        self.wait_buy_price2 = DoubleVar()
        self.wait_buy_price2.set(wait_buy_price[1])
        self.wait_buy_account2 = DoubleVar()
        self.wait_buy_account2.set(wait_buy_account[1])

        self.wait_buy_price3 = DoubleVar()
        self.wait_buy_price3.set(wait_buy_price[2])
        self.wait_buy_account3 = DoubleVar()
        self.wait_buy_account3.set(wait_buy_account[2])

        self.wait_sell_price1 = DoubleVar()
        self.wait_sell_price1.set(wait_sell_price[0])
        self.wait_sell_account1 = DoubleVar()
        self.wait_sell_account1.set(wait_sell_amount[0])

        self.wait_sell_price2 = DoubleVar()
        self.wait_sell_price2.set(wait_sell_price[1])
        self.wait_sell_account2 = DoubleVar()
        self.wait_sell_account2.set(wait_sell_amount[1])

        self.wait_sell_price3 = DoubleVar()
        self.wait_sell_price3.set(wait_sell_price[2])
        self.wait_sell_account3 = DoubleVar()
        self.wait_sell_account3.set(wait_sell_amount[2])

        self.setup_ui()
        self.title(title)

    def setup_ui(self):
        row1 = Frame(self)
        row1.pack(fill="x")
        lst_yes_no = ['YES', 'NO']
        Label(row1, text=u"是否邮件通知: ", width=12).pack(side=LEFT)
        OptionMenu(row1, self.is_email, *lst_yes_no).pack(side=LEFT)

        Label(row1, text=u"是否微信通知: ", width=12).pack(side=LEFT)
        OptionMenu(row1, self.is_email, *lst_yes_no).pack(side=LEFT)


        Label(row1, text=u"交易时是否弹窗提醒: ", width=18).pack(side=LEFT)
        OptionMenu(row1, self.is_alarm, *lst_yes_no).pack(side=LEFT)

        row2 = Frame(self)
        row2.pack(fill="x")
        Label(row2, text=u"弹窗提醒时长(秒): ", width=15).pack(side=LEFT)
        Entry(row2, textvariable=self.alarm_time, width=8).pack(side=LEFT)

        Label(row2, text=u"弹窗提醒超时未处理后是否自动交易: ", width=28).pack(side=LEFT)
        OptionMenu(row2, self.alarm_trade, *lst_yes_no).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"单次最小交易额(美金)>: ", width=18).pack(side=LEFT)
        Entry(row3, textvariable=self.trade_min, width=15).pack(side=LEFT)

        Label(row3, text=u"单次最大交易额(美金)<: ", width=18).pack(side=LEFT)
        Entry(row3, textvariable=self.trade_max, width=15).pack(side=LEFT)

        row4 = Frame(self)
        row4.pack(fill="x")
        Label(row4, text=u"挂单买入: ", width=15).pack(side=LEFT)

        row4 = Frame(self)
        row4.pack(fill="x")
        Label(row4, text=u"买入价格1: ", width=15).pack(side=LEFT)
        Entry(row4, textvariable=self.wait_buy_price1, width=15).pack(side=LEFT)
        Label(row4, text=u"买入金额1(美金): ", width=20).pack(side=LEFT)
        Entry(row4, textvariable=self.wait_buy_account1, width=15).pack(side=LEFT)

        row4 = Frame(self)
        row4.pack(fill="x")
        Label(row4, text=u"买入价格2: ", width=15).pack(side=LEFT)
        Entry(row4, textvariable=self.wait_buy_price2, width=15).pack(side=LEFT)
        Label(row4, text=u"买入金额2(美金): ", width=20).pack(side=LEFT)
        Entry(row4, textvariable=self.wait_buy_account2, width=15).pack(side=LEFT)

        row4 = Frame(self)
        row4.pack(fill="x")
        Label(row4, text=u"买入价格3: ", width=15).pack(side=LEFT)
        Entry(row4, textvariable=self.wait_buy_price3, width=15).pack(side=LEFT)
        Label(row4, text=u"买入金额3(美金): ", width=20).pack(side=LEFT)
        Entry(row4, textvariable=self.wait_buy_account3, width=15).pack(side=LEFT)

        row5 = Frame(self)
        row5.pack(fill="x")
        Label(row5, text=u"挂单卖出: ", width=15).pack(side=LEFT)

        row5 = Frame(self)
        row5.pack(fill="x")
        Label(row5, text=u"卖出价格1: ", width=15).pack(side=LEFT)
        Entry(row5, textvariable=self.wait_sell_price1, width=15).pack(side=LEFT)
        Label(row5, text=u"卖出数量1(币数): ", width=20).pack(side=LEFT)
        Entry(row5, textvariable=self.wait_sell_account1, width=15).pack(side=LEFT)

        row5 = Frame(self)
        row5.pack(fill="x")
        Label(row5, text=u"卖出价格2: ", width=15).pack(side=LEFT)
        Entry(row5, textvariable=self.wait_sell_price2, width=15).pack(side=LEFT)
        Label(row5, text=u"卖出数量2(币数): ", width=20).pack(side=LEFT)
        Entry(row5, textvariable=self.wait_sell_account2, width=15).pack(side=LEFT)

        row5 = Frame(self)
        row5.pack(fill="x")
        Label(row5, text=u"卖出价格3: ", width=15).pack(side=LEFT)
        Entry(row5, textvariable=self.wait_sell_price3, width=15).pack(side=LEFT)
        Label(row5, text=u"卖出数量3(币数): ", width=20).pack(side=LEFT)
        Entry(row5, textvariable=self.wait_sell_account3, width=15).pack(side=LEFT)


        row3 = Frame(self)
        row3.pack(fill="x")
        # Button(row3, text="Reset", command=lambda: self.on_reset(), width=10).pack(side=RIGHT)
        Button(row3, text="Cancel", command=lambda: self.on_cancel(), width=10).pack(side=RIGHT)
        Button(row3, text="OK", command=lambda: self.on_ok(), width=10).pack(side=RIGHT)

    def on_ok(self):
        try:
            is_email = True if str(self.is_email.get()) == "YES" else False
            is_alarm = True if str(self.is_alarm.get()) == "YES" else False
            is_wechat = True if str(self.is_wechat.get()) == "YES" else False
            is_alarm_trade = True if str(self.alarm_trade.get()) == "YES" else False

            alarm_time = float(self.alarm_time.get())
            alarm_time = alarm_time if alarm_time <= 120 else 120

            trade_min = float(self.trade_min.get())
            trade_min = trade_min if trade_min > 1 else 1
            trade_max = float(self.trade_max.get())
            trade_max = trade_max if trade_max < 1000000 else 1000000
            trade_max = trade_max if trade_max > 10 else 10

            wait_buy_price1 = float(self.wait_buy_price1.get())
            wait_buy_account1 = float(self.wait_buy_account1.get())
            wait_buy_price2 = float(self.wait_buy_price2.get())
            wait_buy_account2 = float(self.wait_buy_account2.get())
            wait_buy_price3 = float(self.wait_buy_price3.get())
            wait_buy_account3 = float(self.wait_buy_account3.get())

            wait_sell_price1 = float(self.wait_sell_price1.get())
            wait_sell_account1 = float(self.wait_sell_account1.get())
            wait_sell_price2 = float(self.wait_sell_price2.get())
            wait_sell_account2 = float(self.wait_sell_account2.get())
            wait_sell_price3 = float(self.wait_sell_price3.get())
            wait_sell_account3 = float(self.wait_sell_account3.get())

        except Exception as e:
            messagebox.showwarning("Warning", "All parameters must be numeric and cannot be null!")  # 提出警告对话窗
            return

        self.value_dict["is_email"] = is_email
        self.value_dict["is_wechat"] = is_wechat
        self.value_dict["is_alarm"] = is_alarm
        self.value_dict["is_alarm_trade"] = is_alarm_trade
        self.value_dict["alarm_time"] = alarm_time

        self.value_dict["trade_min"] = trade_min
        self.value_dict["trade_max"] = trade_max
        self.value_dict["wait_buy_price"] = [wait_buy_price1, wait_buy_price2, wait_buy_price3]
        self.value_dict["wait_buy_account"] = [wait_buy_account1, wait_buy_account2, wait_buy_account3]
        self.value_dict["wait_sell_price"] = [wait_sell_price1, wait_sell_price2, wait_sell_price3]
        self.value_dict["wait_sell_account"] = [wait_sell_account1, wait_sell_account2, wait_sell_account3]

        self.is_ok = True
        # messagebox.showinfo("Info", "System settings change have taken effect！")
        log_config.output2ui("Setup System successfully!", 8)
        logger.info("system setup: {}".format(self.value_dict))
        # print(self.value_dict)
        self.destroy()

    def on_cancel(self):
        self.is_ok = False
        self.destroy()


if __name__ == '__main__':
    value_dict = {}
    ps = PopupSystem(value_dict, "System Configuration")
    ps.setup_ui()
