#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/30
# Function: 

from tkinter import Label, Button, Entry, StringVar, LEFT, RIGHT, Checkbutton, Frame, \
    messagebox, OptionMenu, IntVar, N, S, E, W, ACTIVE, DoubleVar,IntVar
import config
from popup_login import MyDialog


class PopupMode(MyDialog):
    def __init__(self, parent, title=u"策略设置"):
        self.result = {}
        MyDialog.__init__(self, parent, title, modal=True, delta_x=400, delta_y=50)

    def setup_ui(self):
        frame = Frame(self)
        current_mode = config.TRADE_MODE_CONFIG.get(config.TRADE_MODE, {})
        display_name = current_mode.get("display", u"稳健")

        Label(frame, text=u"整体策略选择: ", fg="green", font=("", 11, "bold")).grid(row=0, column=0)
        lst_mode = [value["display"] for key, value in config.TRADE_MODE_CONFIG.items()]
        self.mode = StringVar()
        self.mode.set(display_name)
        self.opt_mode = OptionMenu(frame, self.mode, *lst_mode, command=self.cmd_mode_change)
        self.opt_mode.grid(row=0, column=1, sticky=N + S + W)
        Label(frame, text=u'在行情稳定或上升时建议策略设置偏向激进, 以博得更多的利润; 在行情较坏时, 建议策略设置偏向稳健或保守, 以降低交易风险.',
              width=70, wraplength=500, justify='left', fg="gray", font=("", 8)).grid(row=1, column=0, columnspan=4, padx=5, ipadx=5, sticky=N + S + W)


        Label(frame, text=u"补仓参数设置:", fg="green", font=("", 11, "bold")).grid(row=2, column=0, pady=15)

        Label(frame, text=u"补仓数列: ", width=12).grid(row=3, column=0)

        self.patch = StringVar()
        current_mode_patch_mode = current_mode.get("patch_mode", "multiple")
        lst_patch = [value["display"] for key, value in config.PATCH_CONFIG.items()]
        self.patch.set(config.PATCH_CONFIG.get(current_mode_patch_mode, {}).get("display", u"倍投"))
        self.opt_patch = OptionMenu(frame, self.patch, *lst_patch, command=self.cmd_patch_change)
        self.opt_patch.grid(row=3, column=1, sticky=N + S + W)

        self.patch_ref = StringVar()
        current_mode_patch_ref = current_mode.get("patch_ref", 0)
        Label(frame, text=u"补仓参考: ", width=12).grid(row=3, column=2)
        lst_patch_ref = [u"持仓均价", u"上单买价"]
        self.patch_ref.set(lst_patch_ref[current_mode_patch_ref])
        self.opt_patch_ref = OptionMenu(frame, self.patch_ref, *lst_patch_ref)
        self.opt_patch_ref.grid(row=3, column=3, sticky=N + S + W)

        Label(frame, text=u'补仓间隔(%):', width=12).grid(row=4, column=0)
        # 创建并添加Entry,用于接受用户输入的用户名
        self.patch_interval = DoubleVar()
        self.patch_interval.set(round(current_mode.get("patch_interval", 0.05)*100, 4))
        self.ety_interval = Entry(frame, textvariable=self.patch_interval, width=6)
        self.ety_interval.grid(row=4, column=1)
        # Label(frame, text=u'%', width=2).grid(row=4, column=2, sticky=N + S + W)

        Label(frame, text=u'最大补仓次数:', width=14).grid(row=4, column=2)
        # 创建并添加Entry,用于接受用户输入的用户名
        self.patch_times = IntVar()
        self.patch_times.set(round(current_mode.get("limit_patch_times", 6), 4))
        self.ety_times = Entry(frame, textvariable=self.patch_times, width=6)
        self.ety_times.grid(row=4, column=3)

        Label(frame, text=u'系统将根据您设置的补仓方式和补仓间隔在必要的时候进行补仓, 以达到降低持仓成本的目的, 使用不同的补仓数列将影响补仓的比例和次数, 默认推荐为倍投数列.',
              width=70, wraplength=500, justify='left', fg="gray", font=("", 8)).grid(row=5, column=0, columnspan=4, padx=5, ipadx=5, sticky=N + S + W)

        Label(frame, text=u"止盈参数设置:", fg="green", font=("", 11, "bold")).grid(row=6, column=0, pady=15)
        Label(frame, text=u'止盈比例(%):', width=12).grid(row=7, column=0)
        # 创建并添加Entry,用于接受用户输入的用户名
        self.limit_profit = DoubleVar()
        self.limit_profit.set(round(current_mode.get("limit_profit", 0.03)*100, 4))
        self.ety_profit = Entry(frame, textvariable=self.limit_profit, width=8)
        self.ety_profit.grid(row=7, column=1)
        # Label(frame, text=u'%', width=2).grid(row=7, column=2, sticky=N + S + W)

        self.track_profit = IntVar()
        self.track_profit.set(current_mode.get("track", 1))
        Checkbutton(frame, text=u'是否开启追踪止盈', variable=self.track_profit, onvalue=1, offvalue=0, width=20, command=self.cmd_track).grid(row=8, column=0)

        Label(frame, text=u'回撤比例(%):', width=12).grid(row=8, column=1)
        # 创建并添加Entry,用于接受用户输入的用户名
        self.back_profit = DoubleVar()
        self.back_profit.set(round(current_mode.get("back_profit", 0.005)*100, 4))
        self.ety_back = Entry(frame, textvariable=self.back_profit, width=8)
        self.ety_back.grid(row=8, column=2)
        # Label(frame, text=u'%', width=2).grid(row=8, column=3, sticky=N + S + W)
        Label(frame, text=u'开启追踪止盈后, 在达到要求的止盈比例后并不会立即卖出, 系统会开启追踪, 直到盈利不再增涨并且回撤到预设的回撤比例时才会卖出, 以达到盈利更大化的目的, 建议开启.',
              width=70, wraplength=500, justify='left', fg="gray", font=("", 8)).grid(row=9, column=0, columnspan=4, padx=5, ipadx=5, sticky=N + S + W)


        Label(frame, text=u"智能交易设置:", fg="green", font=("", 11, "bold")).grid(row=10, column=0, pady=15)
        self.grid_profit = IntVar()
        self.grid_profit.set(current_mode.get("grid", 1))
        Checkbutton(frame, text=u'是否开启网格止盈', variable=self.grid_profit, onvalue=1, offvalue=0, width=20).grid(row=11, column=0, sticky=N + S + W)
        Label(frame, text=u'只要整个交易组中任何一单达到止盈条件即卖出盈利, 而不必等到整体达到盈利条件, 如此可达到反复收割尾单盈利的效果, 使盈利更加灵活, 建议开启.',
              width=70, wraplength=500, justify='left', fg="gray", font=("", 8)).grid(row=12, column=0, columnspan=4, sticky=N + S + W)


        self.smart_first = IntVar()
        self.smart_first.set(current_mode.get("smart_first", 1))
        Checkbutton(frame, text=u'是否开启智能建仓', variable=self.smart_first, onvalue=1, offvalue=0, width=20).grid(row=13, column=0, sticky=N + S + W)
        Label(frame, text=u'开启智能建仓后, 系统将根据综合数据分析得出建仓推荐指数, 并根据该指数决是否建仓以及建仓的比例. 关闭该功能时, 系统会在行情稳定时立即建仓, 而不会等待最佳入场时机. 当您认为行情较好或者急于入场建仓时, 可暂时关闭该功能, 以达到快速建仓的目的, 其他时间建议开启!',
              width=75, wraplength=500, justify='left', fg="gray", font=("", 8)).grid(row=14, column=0, columnspan=4, sticky=N + S + W)

        self.smart_profit = IntVar()
        self.smart_profit.set(current_mode.get("smart_profit", 1))
        Checkbutton(frame, text=u'是否开启智能止盈', variable=self.smart_profit, onvalue=1, offvalue=0, width=20).grid(row=15, column=0, sticky=N + S + W)
        Label(frame, text=u'开启智能止盈后, 在达到您设置追踪止盈条件后, 如果系统分析出该币价格仍在上涨, 则会延迟卖出, 以达到扩大盈利的目的, 推荐开启.',
              width=70, wraplength=500, justify='left', fg="gray", font=("", 8)).grid(row=16, column=0, columnspan=4, sticky=N + S + W)

        self.smart_patch = IntVar()
        self.smart_patch.set(current_mode.get("smart_patch", 1))
        Checkbutton(frame, text=u'是否开启智能补仓', variable=self.smart_patch, onvalue=1, offvalue=0, width=20).grid(row=17, column=0, sticky=N + S + W)
        Label(frame, text=u'开启智能补仓后, 在达到您设置补仓间隔条件后, 如果系统分析出该币价格仍在下跌, 则会延迟补仓, 以达到降低持仓成本和交易风险的目的, 推荐开启.',
              width=70, wraplength=500, justify='left', fg="gray", font=("", 8)).grid(row=18, column=0, columnspan=4, sticky=N + S + W)

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
            smart_profit = int(self.smart_profit.get())
            smart_patch = int(self.smart_patch.get())
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
            self.result["smart_first"] = smart_first
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

            self.smart_first.set(mode.get("smart_first", 1))
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

    def cmd_patch_change(self, event):
        self.patch.get()