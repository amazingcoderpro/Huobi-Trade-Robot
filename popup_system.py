#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2019/5/7
# Function:

from tkinter import Toplevel, Label, Button, Entry, StringVar, IntVar, Checkbutton, LEFT, RIGHT, Frame, messagebox, OptionMenu, DoubleVar
import log_config


class PopupSystem(Toplevel):
    def __init__(self, value_dict, title="System Configuration"):
        Toplevel.__init__(self)
        self.is_ok = False
        self.value_dict = value_dict
        is_email, is_alarm, trade_min, trade_max, wait_buy_price, \
        wait_buy_account, wait_sell_price, wait_sell_amount = value_dict.get("is_email", True), value_dict.get("is_alarm", False), \
                                                   value_dict.get("trade_min", 10), value_dict.get("trade_max", 1000), value_dict.get("wait_buy_price"), \
                                                              value_dict.get("wait_buy_account"), value_dict.get("wait_sell_price"), value_dict.get("wait_sell_account")

        self.trade_min = DoubleVar()
        self.trade_min.set(trade_min)
        self.trade_max = DoubleVar()
        self.trade_max.set(trade_max)

        self.is_email = StringVar()
        self.is_email.set('YES' if is_email else 'NO')

        self.is_alarm = StringVar()
        self.is_alarm.set('YES' if is_alarm else 'NO')

        self.wait_buy_price = DoubleVar()
        self.wait_buy_price.set(wait_buy_price)
        self.wait_buy_account = DoubleVar()
        self.wait_buy_account.set(wait_buy_account)
        self.wait_sell_price = DoubleVar()
        self.wait_sell_price.set(wait_sell_price)
        self.wait_sell_account = DoubleVar()
        self.wait_sell_account.set(wait_sell_amount)

        self.setup_ui()
        self.title(title)

    def setup_ui(self):
        row1 = Frame(self)
        row1.pack(fill="x")
        lst_email = ['YES', 'NO']
        Label(row1, text="Send email: ", width=15).pack(side=LEFT)
        OptionMenu(row1, self.is_email, *lst_email).pack(side=LEFT)

        row2 = Frame(self)
        row2.pack(fill="x")
        lst_alarm = ['YES', 'NO']
        Label(row2, text="Alarm: ", width=15).pack(side=LEFT)
        OptionMenu(row2, self.is_alarm, *lst_alarm).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text="单次最小交易额: ", width=15).pack(side=LEFT)
        Entry(row3, textvariable=self.trade_min, width=15).pack(side=LEFT)

        Label(row3, text="单次最大交易额: ", width=15).pack(side=LEFT)
        Entry(row3, textvariable=self.trade_max, width=15).pack(side=LEFT)

        row4 = Frame(self)
        row4.pack(fill="x")
        Label(row4, text="挂单买入价格: ", width=15).pack(side=LEFT)
        Entry(row4, textvariable=self.wait_buy_price, width=15).pack(side=LEFT)
        Label(row4, text="挂单买入金额(美金): ", width=20).pack(side=LEFT)
        Entry(row4, textvariable=self.wait_buy_account, width=15).pack(side=LEFT)

        row5 = Frame(self)
        row5.pack(fill="x")
        Label(row5, text="挂单卖出价格: ", width=15).pack(side=LEFT)
        Entry(row5, textvariable=self.wait_sell_price, width=15).pack(side=LEFT)
        Label(row5, text="挂单卖出数量(币数): ", width=20).pack(side=LEFT)
        Entry(row5, textvariable=self.wait_sell_account, width=15).pack(side=LEFT)


        row3 = Frame(self)
        row3.pack(fill="x")
        # Button(row3, text="Reset", command=lambda: self.on_reset(), width=10).pack(side=RIGHT)
        Button(row3, text="Cancel", command=lambda: self.on_cancel(), width=10).pack(side=RIGHT)
        Button(row3, text="OK", command=lambda: self.on_ok(), width=10).pack(side=RIGHT)

    def on_ok(self):
        try:
            is_email = True if str(self.is_email.get())=="YES" else False
            is_alarm = True if str(self.is_alarm.get())=="YES" else False
            trade_min = float(self.trade_min.get())
            trade_max = float(self.trade_max.get())
            wait_buy_price = float(self.wait_buy_price.get())
            wait_buy_account = float(self.wait_buy_account.get())
            wait_sell_price = float(self.wait_sell_price.get())
            wait_sell_account = float(self.wait_sell_account.get())

        except Exception as e:
            messagebox.showwarning("Warning", "All parameters must be numeric and cannot be null!")  # 提出警告对话窗
            return

        self.value_dict["is_email"] = is_email
        self.value_dict["is_alarm"] = is_alarm
        self.value_dict["trade_min"] = trade_min
        self.value_dict["trade_max"] = trade_max
        self.value_dict["wait_buy_price"] = wait_buy_price
        self.value_dict["wait_buy_account"] = wait_buy_account
        self.value_dict["wait_sell_price"] = wait_sell_price
        self.value_dict["wait_sell_account"] = wait_sell_account
        self.is_ok = True
        messagebox.showinfo("Info", "System settings change have taken effect！")
        log_config.output2ui("Setup System successfully!", 8)
        # print(self.value_dict)
        self.destroy()

    def on_cancel(self):
        self.is_ok = False
        self.destroy()



if __name__ == '__main__':
    value_dict = {}
    ps = PopupSystem(value_dict, "System Configuration")
    ps.setup_ui()
