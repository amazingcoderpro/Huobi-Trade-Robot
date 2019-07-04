#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/30
# Function: 
import os
from tkinter import Label, Button, Entry, StringVar, LEFT, RIGHT, Checkbutton, Frame, \
    messagebox, OptionMenu, IntVar, filedialog, N, S, E, W, ACTIVE, DoubleVar
import config
from popup_login import MyDialog


class PopupSystem(MyDialog):
    def __init__(self, parent, title=u"系统设置"):
        MyDialog.__init__(self, parent, title, modal=True)

    def setup_ui(self):
        frame = Frame(self)
        self.trade_min = DoubleVar()
        self.trade_min.set(config.TRADE_MIN_LIMIT_VALUE)
        self.trade_max = DoubleVar()
        self.trade_max.set(config.TRADE_MAX_LIMIT_VALUE)

        self.trade_history_report_interval = IntVar()
        self.trade_history_report_interval.set(config.TRADE_HISTORY_REPORT_INTERVAL)

        Label(frame, text=u"单次最小交易额限制(USDT): ", width=25).grid(row=0, column=0)
        Entry(frame, textvariable=self.trade_min, width=15).grid(row=0, column=1)

        Label(frame, text=u"单次最大交易额限制(USDT): ", width=25).grid(row=1, column=0)
        Entry(frame, textvariable=self.trade_max, width=15).grid(row=1, column=1)
        Label(frame, text=u'最小交易额限制代表每次买入时的最低买入额, 当设置的预算金额过小导致在应该建仓或补仓时计算出的买入额小于最小交易额限制时, 系统自动调整买入额为您设置的最小交易额, 最大交易额限制类似. 当设置最小/最大交易客限制为0时, 系统则不做任何调整, 以真实计算出的买入额进行交易.',
              width=70, wraplength=500, justify='left', fg="gray", font=("", 8)).grid(row=2, column=0, columnspan=3, sticky=N + S + W)


        Label(frame, text=u"账户及盈利情况播报周期(小时): ", width=25).grid(row=3, column=0)
        Entry(frame, textvariable=self.trade_history_report_interval, width=10).grid(row=3, column=1)
        Button(frame, text=u"立即发送", command=lambda: self.on_send_history(), width=10).grid(row=3, column=2)
        Label(frame, text=u'在微信通知开启的情况下, 每间隔您设置的小时数, 系统会将当前的账户持仓及盈利情况通过微信向您进行播报, 以便您实时了解账户及系统运行情况.',
              width=70, wraplength=500, justify='left', fg="gray", font=("", 8)).grid(row=4, column=0, columnspan=3, sticky=N + S + W)

        frame.pack(padx=5, pady=5)

        f = Frame(self)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(f, text=u"确定", width=10, command=self.on_ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(f, text=u"取消", width=10, command=self.on_cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_ok)
        f.pack()

    # 该方法可对用户输入的数据进行校验
    def validate(self):
        try:
            trade_min = float(self.trade_min.get())
            trade_max = float(self.trade_max.get())
            # trade_min = 1 if trade_min < 1 else trade_min
            # trade_max = trade_min+100 if trade_max <= trade_min else trade_max
            if trade_max != 0 and trade_max <= trade_min:
                trade_max = trade_min+100
            self.result["trade_min"] = trade_min
            self.result["trade_max"] = trade_max
        except:
            messagebox.showerror(u"提示", u"请输入有效数字！")
            return False
        return True

    # 该方法可处理用户输入的数据
    def process_input(self):
        return True

    def on_send_history(self):
        pass

if __name__ == '__main__':
    pass