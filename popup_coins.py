#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/30
# Function:
import os
from tkinter import Label, Button, StringVar, LEFT, Checkbutton, Frame, \
    messagebox, OptionMenu, IntVar, N, S, W, ACTIVE
import config
from popup_login import MyDialog

class PopupCoins(MyDialog):
    def __init__(self, parent, history_pairs=[], title=u"币种设置"):
        self.ckb_values = {}
        self.selected_symbols = {}
        self.history_pairs = history_pairs
        # for pair in self.history_pairs:
        #     coin = pair.get("coin", "")
        #     money = pair.get("money", "")
        #     if money in self.selected_symbols.keys():
        #         self.selected_symbols[money].append(coin)
        #     else:
        #         self.selected_symbols[money] = []
        #         self.selected_symbols[money].append(coin)

        MyDialog.__init__(self, parent, title, modal=True)

    def setup_ui(self):
        frame = Frame(self)
        self.platform = StringVar()
        Label(frame, text=u"计价货币: ", width=15).grid(row=0, column=0)
        lst_moneys = list(config.PLATFORMS.get(config.CURRENT_PLATFORM, {}).get("trade_pairs", {}).keys())
        self.money = StringVar()
        self.money.set(lst_moneys[0])
        opt_money = OptionMenu(frame, self.money, *lst_moneys, command=self.cmd_money_change)
        opt_money.grid(row=0, column=1, sticky=N+S+W)
        frame.pack(padx=5, pady=5)

        #把所有计价货币下的币种对应的checkbutton保存下来
        for money in lst_moneys:
            self.ckb_values[money] = []
            self.selected_symbols[money] = []

        self.coins_frame = Frame(self)
        self.coins_frame.pack()
        row = 0
        col = 0
        coins = config.PLATFORMS.get(config.CURRENT_PLATFORM, {}).get("trade_pairs", {}).get(lst_moneys[0], [])
        coins = list(set(coins))
        coins.sort()
        for coin in coins:
            ckb_value = IntVar()
            ckb_value.set(0)
            self.ckb_values[lst_moneys[0]].append({"coin": coin, "value": ckb_value})
            ckb = Checkbutton(self.coins_frame, text=coin, variable=ckb_value, onvalue=1, offvalue=0, command=self.cmd_ckb)
            ckb.grid(row=row, column=col)
            col += 1
            if col > 4:
                row += 1
                col = 0

        self.frame_btn = Frame(self)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(self.frame_btn, text="确定", width=10, command=self.on_ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(self.frame_btn, text="取消", width=10, command=self.on_cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_ok)
        self.frame_btn.pack()

        print(config.CURRENT_SYMBOLS)
        for k, v in config.CURRENT_SYMBOLS.items():
            coins = v.get("coins")
            for coin in coins:
                coin_name = coin.get("coin")
                self.selected_symbols[k].append(coin_name)

        self.cmd_money_change(None)

    def cmd_money_change(self, event):
        current_money = self.money.get()
        coins = config.PLATFORMS.get(config.CURRENT_PLATFORM, {}).get("trade_pairs", {}).get(current_money, [])
        coins = list(set(coins))
        coins.sort()

        # 先销掉所有非当前计价货币的checkbtn
        self.coins_frame.destroy()

        # 重绘当前计价货币下的所有checkbuttion
        self.coins_frame = Frame(self)
        self.coins_frame.pack(padx=5, pady=5)

        row = 0
        col = 0
        self.ckb_values[current_money].clear()

        # 再次进入对话框，如果之前设置过，将其恢复
        last_selected_coins = config.CURRENT_SYMBOLS.get(current_money, {}).get("coins", [])
        last_selected_coin_names = []
        for coin in last_selected_coins:
            last_selected_coin_names.append(coin.get("coin", ""))

        for coin in coins:
            ckb_value = IntVar()
            ckb_value.set(0)

            # 之前选中过，还原为１
            if coin in self.selected_symbols[current_money]:
                ckb_value.set(1)

            coin_name = coin.get("coin", "") if isinstance(coin, dict) else coin
            if coin_name in last_selected_coin_names:
                ckb_value.set(1)

            self.ckb_values[current_money].append({"coin": coin_name, "value": ckb_value})

            ckb = Checkbutton(self.coins_frame, text=coin_name, variable=ckb_value, onvalue=1, offvalue=0, command=self.cmd_ckb)
            ckb.grid(row=row, column=col)
            col += 1
            if col > 5:
                row += 1
                col = 0

        self.frame_btn.destroy()
        self.frame_btn = Frame(self)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(self.frame_btn, text="确定", width=10, command=self.on_ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(self.frame_btn, text="取消", width=10, command=self.on_cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_ok)
        self.frame_btn.pack()

    def cmd_ckb(self):
        # 任何一次点击，就把当前界面上所有checkbutton过一遍
        current_money = self.money.get()
        self.selected_symbols[current_money].clear()
        for dt in self.ckb_values.get(current_money, []):
            if int(dt["value"].get()) == 1:
                self.selected_symbols[current_money].append(dt["coin"])
        # print(self.selected_symbols)

    # 该方法可对用户输入的数据进行校验
    def validate(self):
        self.result["symbols"] = {}
        coin_count = 0
        print(self.selected_symbols)
        for money, coins in self.selected_symbols.items():
            if money not in self.result["symbols"].keys():
                self.result["symbols"][money] = {"trade": 0, "frozen": 0, "coins": []}
            for coin in coins:
                self.result["symbols"][money]["coins"].append({"coin": coin, "trade": 0, "frozen": 0})
                coin_count += 1

        # print(self.result["symbols"])
        if coin_count == 0:
            messagebox.showinfo(u"提示", u"请至少选择一种交易对！")
            return False

        return True

    # 该方法可处理用户输入的数据
    def process_input(self):
        pass





if __name__ == '__main__':
    pass