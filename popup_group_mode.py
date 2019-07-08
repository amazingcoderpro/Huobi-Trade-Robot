#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/30
# Function: 
import os
from tkinter import Label, Button, Entry, StringVar, LEFT, RIGHT, Checkbutton, Frame, \
    messagebox, OptionMenu, IntVar, N, S, E, W, ACTIVE, DoubleVar
import config
from popup_login import MyDialog


class PopupGroupMode(MyDialog):
    def __init__(self, parent, group, title=u"单个交易组策略设置"):
        self.result = {}
        self.group = group
        MyDialog.__init__(self, parent, title, modal=True, delta_x=400, delta_y=100)

    def setup_ui(self):
        # 如果这组交易没有做特定的设置则默认使用全局的交易参数
        frame = Frame(self)
        group_mode = self.group.get("mode", u"")
        group_mode = config.TRADE_MODE if not group_mode else group_mode
        global_mode = config.TRADE_MODE_CONFIG.get(group_mode, {})
        display_name = global_mode.get("display", u"稳健")

        Label(frame, text=u"本组交易策略选择: ").grid(row=0, column=0)
        lst_mode = [value["display"] for key, value in config.TRADE_MODE_CONFIG.items()]
        self.mode = StringVar()
        self.mode.set(display_name)
        self.opt_mode = OptionMenu(frame, self.mode, *lst_mode, command=self.cmd_mode_change)
        self.opt_mode.grid(row=0, column=1, sticky=N + S + W)

        Label(frame, text=u"补仓数列: ", width=12).grid(row=1, column=0)
        self.patch = StringVar()
        current_mode_patch_mode = self.group.get("patch_mode", "")
        current_mode_patch_mode = global_mode.get("patch_mode", u"multiple") if not current_mode_patch_mode else current_mode_patch_mode
        patch_mode_display = config.PATCH_CONFIG.get(current_mode_patch_mode, {}).get("display", u"倍投")

        lst_patch = [value["display"] for key, value in config.PATCH_CONFIG.items()]
        self.patch.set(patch_mode_display)
        self.opt_patch = OptionMenu(frame, self.patch, *lst_patch)
        self.opt_patch.grid(row=1, column=1, sticky=N + S + W)

        self.patch_ref = StringVar()
        current_mode_patch_ref = self.group.get("patch_ref", -1)
        current_mode_patch_ref = global_mode.get("patch_ref", 0) if current_mode_patch_ref<0 else current_mode_patch_ref
        Label(frame, text=u"补仓参考: ", width=12).grid(row=1, column=2)
        lst_patch_ref = [u"持仓均价", u"上单买价"]
        self.patch_ref.set(lst_patch_ref[current_mode_patch_ref])
        self.opt_patch_ref = OptionMenu(frame, self.patch_ref, *lst_patch_ref)
        self.opt_patch_ref.grid(row=1, column=3, sticky=N + S + W)

        Label(frame, text=u'补仓间隔(%):', width=12).grid(row=2, column=0)
        # 创建并添加Entry,用于接受用户输入的用户名
        patch_interval = self.group.get("patch_interval", -1)
        patch_interval = global_mode.get("patch_interval", 0.05) if patch_interval<0 else patch_interval
        self.patch_interval = DoubleVar()
        self.patch_interval.set(round(patch_interval*100, 4))

        self.ety_interval = Entry(frame, textvariable=self.patch_interval, width=8)
        self.ety_interval.grid(row=2, column=1)
        # Label(frame, text=u'%', width=2).grid(row=2, column=2, sticky=N + S + W)

        Label(frame, text=u'最大补仓次数:', width=14).grid(row=2, column=2)
        # 创建并添加Entry,用于接受用户输入的用户名
        patch_times = self.group.get("limit_patch_times", -1)
        patch_times = global_mode.get("limit_patch_times", 5) if patch_times<0 else patch_times
        self.patch_times = DoubleVar()
        self.patch_times.set(patch_times)
        self.ety_times = Entry(frame, textvariable=self.patch_times, width=6)
        self.ety_times.grid(row=2, column=3)


        Label(frame, text=u'止盈比例(%):', width=12).grid(row=3, column=0)
        # 创建并添加Entry,用于接受用户输入的用户名
        limit_profit = self.group.get("limit_profit", -1)
        limit_profit = global_mode.get("limit_profit", 0.026) if limit_profit<0 else limit_profit

        self.limit_profit = DoubleVar()
        self.limit_profit.set(round(limit_profit*100, 4))
        self.ety_profit = Entry(frame, textvariable=self.limit_profit, width=8)
        self.ety_profit.grid(row=3, column=1)
        # Label(frame, text=u'%', width=2).grid(row=3, column=2, sticky=N + S + W)

        track = self.group.get("track", -1)
        track = global_mode.get("track", 1) if track<0 else track
        self.track_profit = IntVar()
        self.track_profit.set(track)
        Checkbutton(frame, text=u'是否开启追踪止盈', variable=self.track_profit, onvalue=1, offvalue=0, width=20, command=self.cmd_track).grid(row=4, column=0)

        Label(frame, text=u'回撤比例(%):', width=12).grid(row=4, column=1)
        # 创建并添加Entry,用于接受用户输入的用户名
        back_profit = self.group.get("back_profit", -1)
        back_profit = global_mode.get("back_profit", 0.005) if back_profit<0 else back_profit

        self.back_profit = DoubleVar()
        self.back_profit.set(round(back_profit*100, 4))
        self.ety_back = Entry(frame, textvariable=self.back_profit, width=8)
        self.ety_back.grid(row=4, column=2)
        # Label(frame, text=u'%', width=2).grid(row=4, column=3, sticky=N + S + W)

        #设置独立的本金预算

        Label(frame, text=u'本金预算:', width=12).grid(row=5, column=0)
        principal = self.group.get("principal", 0)
        if principal <= 0:
            principal = config.CURRENT_SYMBOLS.get(self.group.get("money", "USDT").upper(), {}).get("principal", 0)
            if principal <= 0:
                principal = config.CURRENT_SYMBOLS.get(self.group.get("money", "USDT").upper(), {}).get("balance", 0) * 2

            coins_num = len(config.CURRENT_SYMBOLS.get(self.group.get("money", "USDT").upper()).get("coins", []))
            coins_num = 1 if coins_num == 0 else coins_num
            principal = principal / coins_num  # 当前货币的本金预算除以需要监控的币对数，就是这个交易对的预算

        self.principal = DoubleVar()
        self.principal.set(round(principal, 4))
        self.ety_profit = Entry(frame, textvariable=self.principal, width=10)
        self.ety_profit.grid(row=5, column=1)
        Label(frame, text=u'您可以为该组交易设置独立的本金预算, 默认为全局本金预算除以监控的币种数', fg="gray", font=("", 8)).grid(row=5, column=2, columnspan=2, sticky=N + S + W)


        grid = self.group.get("grid", -1)
        grid = global_mode.get("grid", 1) if grid < 0 else grid
        self.grid_profit = IntVar()
        self.grid_profit.set(grid)
        Checkbutton(frame, text=u'是否开启网格止盈', variable=self.grid_profit, onvalue=1, offvalue=0, width=20).grid(row=6, column=0, sticky=N + S + W)

        smart_profit = self.group.get("smart_profit", -1)
        smart_profit = global_mode.get("smart_profit", 1) if smart_profit<0 else smart_profit

        self.smart_profit = IntVar()
        self.smart_profit.set(smart_profit)
        Checkbutton(frame, text=u'是否开启智能止盈', variable=self.smart_profit, onvalue=1, offvalue=0, width=20).grid(row=7, column=0, sticky=N + S + W)

        smart_patch = self.group.get("smart_patch", -1)
        smart_patch = global_mode.get("smart_patch", 1) if smart_patch<0 else smart_patch
        self.smart_patch = IntVar()
        self.smart_patch.set(smart_patch)
        Checkbutton(frame, text=u'是否开启智能补仓', variable=self.smart_patch, onvalue=1, offvalue=0, width=20).grid(row=8, column=0, sticky=N + S + W)

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
            patch_interval = float(self.patch_interval.get())
            patch_ref_name = self.patch_ref.get()
            smart_profit = int(self.smart_profit.get())
            smart_patch = int(self.smart_patch.get())
            principal = float(self.principal.get())
            patch_times = int(self.patch_times.get())

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
            self.result["limit_profit"] = 0.01 if self.result["limit_profit"] < 0.01 else self.result["limit_profit"]
            self.result["back_profit"] = round(back_profit/100, 6)
            if grid and limit_profit < back_profit:
                messagebox.showerror(u"提示", u"开启追踪止盈时, 回撤比例必须小于止盈比例！")
                return False

            self.result["track"] = track
            self.result["grid"] = grid
            self.result["smart_profit"] = smart_profit
            self.result["smart_patch"] = smart_patch

            self.result["patch_interval"] = round(patch_interval/100, 6)
            #补仓间隔不能小于千分之五
            self.result["patch_interval"] = 0.005 if self.result["patch_interval"] < 0.005 else self.result["patch_interval"]
            self.result["patch_ref"] = 1 if patch_ref_name == u"上单买价" else 0

            #下面这两个用记界面打印提示
            self.result["mode_name"] = mode_name
            self.result["patch_name"] = patch_name
            self.result["patch_ref_name"] = patch_ref_name
            self.result["principal"] = principal
            self.result["limit_patch_times"] = patch_times
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
            if mode.get("track", 1) == 1:
                self.ety_back.config(state="normal")
            else:
                self.ety_back.config(state="disabled")

            self.smart_profit.set(mode.get("smart_profit", 1))
            self.smart_patch.set(mode.get("smart_patch", 1))

            lst_patch_ref = [u"持仓均价", u"上单买价"]
            self.patch_ref.set(lst_patch_ref[mode.get("patch_ref", 0)])
            self.patch_interval.set(round(mode.get("patch_interval", 0.05)*100, 4))
            self.patch_times.set(mode.get("limit_patch_times", 5))

    def cmd_track(self):
        val = self.track_profit.get()
        if val:
            self.ety_back.config(state="normal")
        else:
            self.ety_back.config(state="disabled")
