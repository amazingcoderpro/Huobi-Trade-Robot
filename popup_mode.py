#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/30
# Function: 
import os
from tkinter import Label, Button, Entry, StringVar, LEFT, RIGHT, Checkbutton, Frame, \
    messagebox, OptionMenu, IntVar, N, S, E, W, ACTIVE, DoubleVar
import config
from popup_login import MyDialog


class PopupMode(MyDialog):
    def __init__(self, parent, title=u"策略设置"):
        self.result = {}
        MyDialog.__init__(self, parent, title, modal=True)

    def setup_ui(self):
        frame = Frame(self)

        current_mode = config.TRADE_MODE_CONFIG.get(config.TRADE_MODE, {})

        Label(frame, text=u"策略选择: ", width=12).grid(row=0, column=0)

        lst_mode = [value["display"] for key, value in config.TRADE_MODE_CONFIG.items()]
        self.mode = StringVar()
        self.mode.set(current_mode.get("display", u"稳健"))
        self.opt_mode = OptionMenu(frame, self.mode, *lst_mode, command=self.cmd_mode_change)
        self.opt_mode.grid(row=0, column=1, sticky=N + S + W)


        Label(frame, text=u"-----------------------补仓参数设置-----------------------", width=40).grid(row=1, column=0, columnspan=3, pady=15)

        Label(frame, text=u"补仓数列: ", width=12).grid(row=2, column=0)

        self.patch = StringVar()
        current_mode_patch_mode = current_mode.get("patch_mode", "multiple")
        lst_patch = [value["display"] for key, value in config.PATCH_CONFIG.items()]
        self.patch.set(config.PATCH_CONFIG.get(current_mode_patch_mode, {}).get("display", u"倍投"))
        self.opt_patch = OptionMenu(frame, self.patch, *lst_patch, command=self.cmd_patch_change)
        self.opt_patch.grid(row=2, column=1, sticky=N + S + W)

        self.patch_ref = StringVar()
        current_mode_patch_ref = current_mode.get("patch_ref", 0)
        Label(frame, text=u"补仓参考: ", width=12).grid(row=3, column=0)
        lst_patch_ref = [u"持仓均价", u"上单买价"]
        self.patch_ref.set(lst_patch_ref[current_mode_patch_ref])
        self.opt_patch_ref = OptionMenu(frame, self.patch_ref, *lst_patch_ref)
        self.opt_patch_ref.grid(row=3, column=1, sticky=N + S + W)

        Label(frame, text=u'补仓间隔:', width=12).grid(row=4, column=0)
        # 创建并添加Entry,用于接受用户输入的用户名
        self.patch_interval = DoubleVar()
        self.patch_interval.set(round(current_mode.get("patch_interval", 0.05)*100, 4))
        self.ety_interval = Entry(frame, textvariable=self.patch_interval, width=8)
        self.ety_interval.grid(row=4, column=1)
        Label(frame, text=u'%', width=2).grid(row=4, column=2, sticky=N + S + W)

        Label(frame, text=u"-----------------------止盈参数设置-----------------------", width=40).grid(row=5, column=0, columnspan=3, pady=15)
        Label(frame, text=u'止盈比例:', width=12).grid(row=6, column=0)
        # 创建并添加Entry,用于接受用户输入的用户名
        self.limit_profit = DoubleVar()
        self.limit_profit.set(round(current_mode.get("limit_profit", 0.03)*100, 4))
        self.ety_profit = Entry(frame, textvariable=self.limit_profit, width=8)
        self.ety_profit.grid(row=6, column=1)
        Label(frame, text=u'%', width=2).grid(row=6, column=2, sticky=N + S + W)

        self.track_profit = IntVar()
        self.track_profit.set(current_mode.get("track", 1))
        Checkbutton(frame, text=u'是否开启追踪止盈', variable=self.track_profit, onvalue=1, offvalue=0, width=20, command=self.cmd_track).grid(row=7, column=0)

        Label(frame, text=u'回撤比例:', width=12).grid(row=7, column=1)
        # 创建并添加Entry,用于接受用户输入的用户名
        self.back_profit = DoubleVar()
        self.back_profit.set(round(current_mode.get("back_profit", 0.005)*100, 4))
        self.ety_back = Entry(frame, textvariable=self.back_profit, width=8)
        self.ety_back.grid(row=7, column=2)
        Label(frame, text=u'%', width=2).grid(row=7, column=3, sticky=N + S + W)

        self.grid_profit = IntVar()
        self.grid_profit.set(current_mode.get("grid", 1))
        Checkbutton(frame, text=u'是否开启网格止盈', variable=self.grid_profit, onvalue=1, offvalue=0, width=20).grid(row=8, column=0, sticky=N + S + W)
        Label(frame, text=u'针对尾单进行止盈追踪, 达到反复收割尾单的效果.',
              width=50, wraplength=400, justify='left', fg="gray").grid(row=9, column=0, columnspan=4, sticky=N + S + W)


        self.smart_first = IntVar()
        self.smart_first.set(current_mode.get("smart_first", 1))
        Checkbutton(frame, text=u'是否开启智能建仓', variable=self.smart_first, onvalue=1, offvalue=0, width=20).grid(row=10, column=0, sticky=N + S + W)
        Label(frame, text=u'开启智能建仓后, 系统将根据综合数据分析得出建仓推荐指数, 并根据该指数决是否建仓以及建仓量的多少. 若未开启, 则会在行情稳定时立即建仓.',
              width=50, wraplength=400, justify='left', fg="gray").grid(row=11, column=0, columnspan=4, sticky=N + S + W)

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
            mode_name = self.mode.get()
            patch_name = self.patch.get()
            limit_profit = float(self.limit_profit.get())
            back_profit = float(self.back_profit.get())
            track = int(self.track_profit.get())
            grid = int(self.grid_profit.get())
            smart_first = int(self.smart_first.get())
            patch_interval = float(self.patch_interval.get())
            patch_ref_name = self.patch_ref.get()

            mode_key = "robust"
            for k, v in config.TRADE_MODE_CONFIG.items():
                if v["display"] == mode_name:
                    mode_key = k
                    break
            patch_key = "multiple"
            for k, v in config.PATCH_CONFIG.items():
                if v["display"] == patch_name:
                    patch_key = k
                    break

            self.result["mode"] = mode_key
            self.result["patch_mode"] = patch_key
            self.result["limit_profit"] = round(limit_profit/100, 6)
            self.result["back_profit"] = round(back_profit/100, 6)
            if grid and limit_profit < back_profit:
                messagebox.showerror(u"提示", u"开启追踪止盈时, 回撤比例必须小于止盈比例！")
                return False

            self.result["track"] = track
            self.result["grid"] = grid
            self.result["smart_first"] = smart_first
            self.result["patch_interval"] = round(patch_interval/100, 6)
            self.result["patch_ref"] = 1 if patch_ref_name == u"上单买价" else 0

            #下面这两个用记界面打印提示
            self.result["mode_name"] = mode_name
            self.result["patch_name"] = patch_name
            self.result["patch_ref_name"] = patch_ref_name
        except Exception as e:
            messagebox.showerror(u"提示", u"请输入有效数字！")
            return False

        return True

    # 该方法可处理用户输入的数据
    def process_input(self):
        return True

    def cmd_mode_change(self, event):
        mode_name = self.mode.get()
        mode = None
        for k, v in config.TRADE_MODE_CONFIG.items():
            if v["display"] == mode_name:
                mode = v
                break

        if mode:
            self.limit_profit.set(round(mode.get("limit_profit", 0.03)*100, 4))
            self.back_profit.set(round(mode.get("back_profit", 0.005)*100, 4))
            patch_name = mode.get("patch_mode", "multiple")
            self.patch.set(config.PATCH_CONFIG.get(patch_name, {}).get("display", u"倍投"))

            self.grid_profit.set(mode.get("grid", 1))
            self.track_profit.set(mode.get("track", 1))
            self.smart_first.set(mode.get("smart_first", 1))

            lst_patch_ref = [u"持仓均价", u"上单买价"]
            self.patch_ref.set(lst_patch_ref[mode.get("patch_ref", 0)])
            self.patch_interval.set(round(mode.get("patch_interval", 0.05)*100, 4))

    def cmd_track(self):
        val = self.track_profit.get()
        if val:
            self.ety_back.config(state="normal")
        else:
            self.ety_back.config(state="disabled")

    def cmd_patch_change(self, event):
        self.patch.get()