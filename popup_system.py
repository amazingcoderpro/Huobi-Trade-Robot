#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2019/5/7
# Function:

from tkinter import Toplevel, Label, Button, Entry, StringVar, IntVar, Checkbutton, LEFT, RIGHT, \
    Frame, messagebox, OptionMenu, DoubleVar,Text, END, Scale, HORIZONTAL
import log_config
import logging
import config
logger = logging.getLogger(__name__)


class PopupSystem(Toplevel):
    def __init__(self, value_dict, title="System Configuration"):
        Toplevel.__init__(self)
        self.is_ok = False
        self.value_dict = value_dict
        postion_low, force_position_low, postion_high, force_position_high, risk_factor, is_email, is_wechat, is_alarm, trade_min, trade_max, wait_buy_price, \
        wait_buy_account, wait_sell_price, wait_sell_amount, alarm_time, alarm_trade, trade_history_report_interval, account_report_interval, nick_name = value_dict.get("position_low", 0), value_dict.get("force_position_low", 0),value_dict.get("position_high", 100), value_dict.get("force_position_high", 0), value_dict.get("risk", 1.0), value_dict.get("is_email", True), value_dict.get("is_wechat", True), value_dict.get("is_alarm", False), \
                                                   value_dict.get("trade_min", 10), value_dict.get("trade_max", 1000), value_dict.get("wait_buy_price"), \
                                                              value_dict.get("wait_buy_account"), value_dict.get("wait_sell_price"), value_dict.get("wait_sell_account"), value_dict.get("alarm_time", 30), value_dict.get("is_alarm_trade", True), value_dict.get("trade_history_report_interval", 86400), value_dict.get("account_report_interval", 7200),value_dict.get("nick_name", "")

        self.trade_min = DoubleVar()
        self.trade_min.set(trade_min)
        self.trade_max = DoubleVar()
        self.trade_max.set(trade_max)

        self.nick_name = StringVar()
        self.nick_name.set(nick_name)

        self.is_email = StringVar()
        self.is_email.set('YES' if is_email else 'NO')

        self.is_wechat = StringVar()
        self.is_wechat.set('YES' if is_wechat else 'NO')

        self.is_alarm = StringVar()
        self.is_alarm.set('YES' if is_alarm else 'NO')

        self.alarm_time = DoubleVar()
        self.alarm_time.set(alarm_time)

        self.alarm_trade = StringVar()
        self.alarm_trade.set('YES' if alarm_trade else 'NO')

        self.txt_emails = None
        self.emails = "\n".join(value_dict.get("emails", []))

        self.txt_wechats = None
        self.wechats = "\n".join(value_dict.get("wechats", []))

        self.ckb_login_wechat_now = IntVar()
        self.ckb_lwn = None

        self.position_low = DoubleVar()
        self.position_low.set(postion_low * 100)
        self.position_high = DoubleVar()
        self.position_high.set(postion_high * 100)

        self.ckb_force_position_low = IntVar()
        self.ckb_force_position_low.set(force_position_low)
        self.ckb_fp_low = None

        self.ckb_force_position_high = IntVar()
        self.ckb_force_position_high.set(force_position_high)
        self.ckb_fp_high = None


        # self.risk_factor = DoubleVar()
        # self.risk_factor.set(risk_factor)
        self.risk_factor = risk_factor
        self.risk_scale = None

        # 历史交易记录播报周期
        self.trade_history_report_interval = IntVar()
        self.trade_history_report_interval.set(trade_history_report_interval)

        # 账户情况播报周期
        self.account_report_interval = IntVar()
        self.account_report_interval.set(account_report_interval)

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

        self.txt_emails_vip = None
        self.txt_emails = None
        # print(value_dict.get("emails", []))
        self.emails_vip = "\n".join(value_dict.get("emails_vip", []))
        self.emails = "\n".join(value_dict.get("emails", []))
        # print(self.emails)

        self.txt_wechats_vip = None
        self.txt_wechats = None
        self.wechats_vip = "\n".join(value_dict.get("wechats_vip", []))
        self.wechats = "\n".join(value_dict.get("wechats", []))

        self.setup_ui()
        self.title(title)

    def setup_ui(self):
        row0 = Frame(self)
        row0.pack(fill="x")
        Label(row0, text=u"请输入当前用户昵称: ", width=15).pack(side=LEFT)
        Entry(row0, textvariable=self.nick_name, width=15).pack(side=LEFT)

        row1 = Frame(self)
        row1.pack(fill="x")
        lst_yes_no = ['YES', 'NO']
        Label(row1, text=u"是否邮件通知: ", width=12).pack(side=LEFT)
        OptionMenu(row1, self.is_email, *lst_yes_no).pack(side=LEFT)

        Label(row1, text=u"是否微信通知: ", width=12).pack(side=LEFT)
        OptionMenu(row1, self.is_wechat, *lst_yes_no).pack(side=LEFT)

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

        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"风险系数(取值范围0.5-1.5, 越小越稳健, 越大越激进): ", width=40).pack(side=LEFT)
        row3 = Frame(self)
        row3.pack(fill="x")
        self.risk_scale = Scale(row3, from_=0.5, to=1.5, resolution=0.01, orient=HORIZONTAL, length=200)
        self.risk_scale.set(self.risk_factor)
        self.risk_scale.pack()

        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"限制最低持仓比(取值0-100): ", width=25).pack(side=LEFT)
        Entry(row3, textvariable=self.position_low, width=5).pack(side=LEFT)
        Label(row3, text=u"%", width=5).pack(side=LEFT)
        self.ckb_fp_low = Checkbutton(row3, text='低于该仓位后是否强制锁仓（不再卖出）', variable=self.ckb_force_position_low, onvalue=1, offvalue=0).pack()

        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"限制最高持仓比(取值0-100): ", width=25).pack(side=LEFT)
        Entry(row3, textvariable=self.position_high, width=5).pack(side=LEFT)
        Label(row3, text=u"%", width=5).pack(side=LEFT)
        self.ckb_fp_high = Checkbutton(row3, text='高于该仓位后是否强制锁仓（不再买入）', variable=self.ckb_force_position_high, onvalue=1, offvalue=0).pack()


        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"历史交易记录播报周期(小时): ", width=25).pack(side=LEFT)
        Entry(row3, textvariable=self.trade_history_report_interval, width=15).pack(side=LEFT)
        Button(row3, text="立即发送", command=lambda: self.on_send_history(), width=10).pack(side=RIGHT)


        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"账户信息播报周期(小时): ", width=25).pack(side=LEFT)
        Entry(row3, textvariable=self.account_report_interval, width=15).pack(side=LEFT)
        Button(row3, text="立即发送", command=lambda: self.on_send_account_info(), width=10).pack(side=RIGHT)

        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"收件箱地址(多个邮箱地址请换行输入): ", width=30).pack(side=LEFT)
        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"VIP: ", width=30).pack(side=LEFT)
        Label(row3, text=u"普通: ", width=30).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x")
        self.txt_emails_vip = Text(row3, height=4, width=30)
        self.txt_emails_vip.insert(END, self.emails_vip)
        self.txt_emails_vip.pack(ipadx=5, side=LEFT)

        self.txt_emails = Text(row3, height=4, width=30)
        self.txt_emails.insert(END, self.emails)
        self.txt_emails.pack(ipadx=5, side=LEFT)


        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"微信昵称(多个微信昵称请换行输入): ", width=30).pack(side=LEFT)
        self.ckb_lwn = Checkbutton(row3, text='立即登录', variable=self.ckb_login_wechat_now, onvalue=1, offvalue=0).pack()
        row3 = Frame(self)
        row3.pack(fill="x")
        Label(row3, text=u"VIP: ", width=30).pack(side=LEFT)
        Label(row3, text=u"普通: ", width=30).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x")
        self.txt_wechats_vip = Text(row3, height=4, width=30)
        self.txt_wechats_vip.insert(END, self.wechats_vip)
        self.txt_wechats_vip.pack(ipadx=5, side=LEFT)

        self.txt_wechats = Text(row3, height=4, width=30)
        self.txt_wechats.insert(END, self.wechats)
        self.txt_wechats.pack(ipadx=5, side=LEFT)


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
            login_wechat_now = self.ckb_login_wechat_now.get()
            force_position_low = self.ckb_force_position_low.get()
            force_position_high = self.ckb_force_position_high.get()

            trade_history_interval = self.trade_history_report_interval.get()
            account_report_interval = self.account_report_interval.get()

            risk = float(self.risk_scale.get())
            nick_name = self.nick_name.get()

            # risk = float(self.risk_factor.get())
            # if risk < 0.5:
            #     risk = 0.5
            #
            # if risk > 1.5:
            #     risk = 1.5

            position_low = float(self.position_low.get())
            if position_low > 100:
                position_low = 1
            elif position_low < 0:
                position_low = 0
            else:
                position_low /= 100

            position_high = float(self.position_high.get())
            if position_high > 100:
                position_high = 1
            elif position_high < 0:
                position_high = 0
            else:
                position_high /= 100
            #
            # if position_high-position_low < 0.05:
            #     position_high += 0.05

            if position_high < position_low:
                position_high = 1

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

        self.value_dict["risk"] = risk
        self.value_dict["position_low"] = position_low
        self.value_dict["position_high"] = position_high
        self.value_dict["force_position_low"] = force_position_low
        self.value_dict["force_position_high"] = force_position_high
        self.value_dict["emails"] = self.txt_emails.get(1.0, END)
        self.value_dict["wechats"] = self.txt_wechats.get(1.0, END)
        self.value_dict["emails_vip"] = self.txt_emails_vip.get(1.0, END)
        self.value_dict["wechats_vip"] = self.txt_wechats_vip.get(1.0, END)

        self.value_dict["login_wechat_now"] = login_wechat_now
        self.value_dict["trade_history_report_interval"] = trade_history_interval
        self.value_dict["account_report_interval"] = account_report_interval
        self.value_dict["nick_name"] = nick_name

        self.is_ok = True
        # messagebox.showinfo("Info", "System settings change have taken effect！")
        log_config.output2ui("Setup System successfully!", 8)
        logger.info("system setup: {}".format(self.value_dict))
        # print(self.value_dict)
        self.destroy()

    def on_cancel(self):
        self.is_ok = False
        self.destroy()

    def on_send_history(self):
        try:
            trade_history_interval = int(self.trade_history_report_interval.get())
        except:
            trade_history_interval = 24

        config.SEND_HISTORY_NOW = trade_history_interval

    def on_send_account_info(self):
        config.SEND_ACCOUNT_NOW = 1

if __name__ == '__main__':
    value_dict = {}
    ps = PopupSystem(value_dict, "System Configuration")
    ps.setup_ui()
