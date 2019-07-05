#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/18
# Function:
import os
import time
from datetime import datetime, timedelta
from tkinter import Tk, Label, Menu, Button, IntVar, DoubleVar, StringVar, VERTICAL, Entry, END, messagebox, OptionMenu, ttk, N, S, E, W  #上对齐/下对齐/左对齐/右对齐
from tkinter.scrolledtext import ScrolledText
from queue import Queue
import logging
import json
from threading import Thread
import requests
from greesbar import GressBar
from huobi import Huobi
import process
from strategy_pool import StrategyPool
import strategies
from tkinter.messagebox import askyesno
import log_config
import huobi
import config
import wechat_helper
import webbrowser
logger = logging.getLogger(__name__)
CURRENT_PRICE = 1
from popup_login import PopupLogin
from popup_api import PopupAPI
from popup_coins import PopupCoins
from popup_trade_info import PopupTradeInfo
from popup_mode import PopupMode
from popup_trade_results import PopupTradeResults
from popup_system import PopupSystem
from popup_group_mode import PopupGroupMode
import hashlib
import yaml
import base64
import pickle
import sqlite3


def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


class MainUI:
    def __init__(self, root):
        self.account = ""
        self.working = False
        self.is_login = False
        self.run_time_value = 0
        self.verify = True
        self.coin_trade = 0
        self.dollar_trade = 0
        self.notify_queue = Queue()
        self.gressbar_init_history = GressBar()
        self.gressbar_verify_api = GressBar()
        self.root = root
        self.top = None
        self.is_api_ok = False
        self._user_info = {}
        self._strategy_dict = {}
        root.title(config.TITLE)
        log_config.init_log_config(use_mail=False)
        self.first_login = True

        self.history_pairs = [] # 历史未完成的交易对

        self.pop_menu = Menu(root, tearoff=0)
        self.pop_menu.add_command(label="交易参数设置", command=self.cmd_group_setting)
        self.pop_menu.add_command(label="停止补仓", command=self.cmd_stop_patch)
        self.pop_menu.add_command(label="开启补仓", command=self.cmd_start_patch)
        self.pop_menu.add_command(label="平仓(卖出当前币种)", command=self.cmd_sell_out)
        self.pop_menu.add_command(label="清仓(卖出所有币种)", command=self.cmd_sell_all)
        self.pop_menu.add_separator()
        self.pop_menu.add_command(label="取消")

        self._hb = None
        self._strategy_pool = StrategyPool()

        self.btn_login_str = StringVar()
        self.btn_login_str.set(u"登   录")
        self.btn_login = Button(root, textvariable=self.btn_login_str, command=self.cmd_login, width=8, font=("", 14, 'bold'))

        # self.label_arrow10 = Label(root, text=u"↓", width=8)
        # self.label_arrow11 = Label(root, text=u"↓", width=8)

        # self.label_platform = Label(root, text=u"选择平台: ", width=8, font=("", 14, 'bold'))
        # lst_platform = [u"火币", u"币安", u"OKEx"]
        # self.platform = StringVar()
        # self.platform.set(lst_platform[0])
        # self.opt_platform = OptionMenu(root, self.platform, *lst_platform)

        self.btn_api = Button(root, text=u"API设置", command=self.cmd_api, width=8, font=("", 14, 'bold'))
        self.btn_coin = Button(root, text=u"币种设置", command=self.cmd_coin, width=8, font=("", 14, 'bold'))

        # self.label_money = Label(root, text=u"计价货币: ", width=8, font=("", 11, 'bold'))
        # lst_money = ["USDT", "BTC"]
        # self.money = StringVar()
        # self.money.set(lst_money[0])
        # self.opt_money = OptionMenu(root, self.money, *lst_money)

        # self.label_mode = Label(root, text=u"选择策略:", width=8, font=("", 11, 'bold'))
        # lst_mode = ["保守", "激进+"]
        # self.mode = StringVar()
        # self.mode.set(lst_mode[0])
        # self.opt_mode = OptionMenu(root, self.mode, *lst_mode)

        # self.btn_coin = Button(root, text=u"交易币种", command=self.cmd_coin, width=15, font=("", 14, 'bold'))
        self.btn_mode_setting = Button(root, text=u"策略设置", command=self.cmd_mode_setting, width=8, font=("", 14, 'bold'))
        self.btn_system_setting = Button(root, text=u"系统设置", command=self.cmd_system_setting, width=8, font=("", 14, 'bold'))
        self.btn_pending_setting = Button(root, text=u"挂单买卖", command=self.cmd_pending_setting, width=8, font=("", 14, 'bold'))
        self.btn_start_str = StringVar()
        self.btn_start_str.set(u"立即启动")
        self.btn_start = Button(root, textvariable=self.btn_start_str, command=self.cmd_start, width=8, font=("", 14, 'bold'))
        self.btn_pause = Button(root, text=u"全部停止", command=self.cmd_stop, width=8, font=("", 14, 'bold'))
        self.btn_wechat_str = StringVar()
        self.btn_wechat_str.set(u"微信通知")
        self.btn_wechat = Button(root, textvariable=self.btn_wechat_str, command=self.cmd_wechat, width=8, font=("", 14, 'bold'))

        self.label_money = Label(root, text=u"计价货币:", width=8, font=("", 12, 'bold'))
        # self.label_money_ = Label(root, text="USDT", width=3, font=("", 12, 'bold'))

        self.lst_money = ["USDT", "BTC", "ETH"]
        for k,v in config.PLATFORMS.items():
            for money in v["trade_pairs"].keys():
                self.lst_money.append(money)

        self.lst_money = list(set(self.lst_money))
        self.money = StringVar()
        self.money.set("USDT")
        self.opt_money = OptionMenu(root, self.money, *self.lst_money, command=self.cmd_money_change)
        # self.opt_money.config(width=4)

        self.label_mode = Label(root, text=u"策略选择:", width=8, font=("", 12, 'bold'))
        self.lst_mode = []
        default_mode = u"稳健"
        for k, v in config.TRADE_MODE_CONFIG.items():
            self.lst_mode.append(v["display"])
            if k == config.TRADE_MODE:
                default_mode = v["display"]

        self.mode = StringVar()
        self.mode.set(default_mode)
        self.opt_mode = OptionMenu(root, self.mode, *self.lst_mode, command=self.cmd_mode_change)
        # self.opt_mode.config(width=4)

        self.balance = DoubleVar()
        self.balance.set(0)
        self.label_balance = Label(root, text=u"可用余额:", width=8, font=("", 12, 'bold'))
        self.label_balance_ = Label(root, textvariable=self.balance, width=10, font=("", 12, 'bold'))

        self.principal = DoubleVar()
        self.principal.set(0)
        self.label_principal = Label(root, text=u"本金预算:", width=8, font=("", 12, 'bold'))
        self.ety_principal = Entry(root, textvariable=self.principal, font=("", 11, 'bold'), width=14)
        self.btn_principal = Button(root, text="确认", command=self.cmd_principal, width=6)

        # self.position = DoubleVar()
        # self.position.set(0)
        # self.label_account_position = Label(root, text=u"仓位:", width=4, font=("", 12, 'bold'))
        # self.label_account_position_ = Label(root, textvariable=self.position, width=6, font=("", 12, 'bold'))

        self.coin_counts = IntVar()
        self.coin_counts.set(0)
        self.label_coin_num = Label(root, text=u"监控币种数:", width=10, font=("", 12, 'bold'))
        self.label_coin_num_ = Label(root, textvariable=self.coin_counts, width=8, font=("", 12, 'bold'))

        self.total_profit = DoubleVar()
        self.total_profit.set(0)
        self.label_total_profit = Label(root, text=u"累计盈利:", width=8, font=("", 12, 'bold'))
        self.label_total_profit_ = Label(root, textvariable=self.total_profit, width=8, font=("", 12, 'bold'))

        self.run_time = StringVar()
        self.run_time.set("0时0分")
        self.label_total_run = Label(root, text=u"在线时长:", width=8, font=("", 12, 'bold'))
        self.label_total_run_ = Label(root, textvariable=self.run_time, width=10, font=("", 12, 'bold'))

        self.btn_results = Button(root, text="收益统计", command=self.cmd_trade_result, width=7, font=("", 12, 'bold'))

        # columns = (u"启动时间", u"状态", u"交易对", u"当前价格", u"持仓均价", u"货币数量", u"持仓费用", u"收益比%", u"已做单数", u"止盈比例%", u"止盈追踪%", u"间隔参考", u"网格止盈", u"尾单收益比%", u"累计收益", u"最近更新", u"结束时间")
        # columns = (
        # u"序号", u"交易对", u"状态", u"当前价格", u"持仓均价", u"持币数量", u"持仓费用", u"已做单数", u"已盈利单数", u"尾单收益比%", u"累计收益", u"收益比%", u"建仓时间",  u"最近更新", u"结束时间")

        columns = (
            u"序号", u"交易对", u"状态", u"持仓均价", u"持币数量", u"持仓费用", u"已做单数", u"已盈利单数", u"尾单收益比%", u"累计收益", u"收益比%",
            u"建仓时间", u"最近更新", u"结束时间")

        self.tree = ttk.Treeview(root, show="headings", columns=columns, height=16)  # 表格
        for name in columns:
            if name == u"序号":
                self.tree.column(name, width=30, anchor="center")
            if name in [u"状态"]:
                self.tree.column(name, width=50, anchor="center")
            elif name in [u"收益比", u"已做单数"]:
                self.tree.column(name, width=70, anchor="center")
            elif name in [u"建仓时间", u"最近更新", u"结束时间"]:
                self.tree.column(name, width=110, anchor="center")
            else:
                self.tree.column(name, width=80, anchor="center")
            # self.tree.heading(name, text=name)  # 显示表头

            self.tree.heading(name, text=name, command=lambda _col=name:treeview_sort_column(self.tree, _col, False))

            # i = columns.index(name)
            # self.mat_list.heading(name, text=columns[i], command=lambda _col=name: treeview_sort_column(self.mat_list, _col, False))


        import random
        # for i in range(10):
        # self.tree.insert("", 0, values=("0618 15:23:33", u"进行中", "EOSETH", "6.5631", 6.13, 103.4, 621.22, 4.23, 4, 2.31 , 145.32, "0613 08:25:36"))  # 插入数据，
        # self.tree.insert("", 1, values=(
        # 2, u"进行中", "ONTUSDT", 1.4153, 1.236, 6345, 1.236*6345, 15.2, 5, 2.15, 89.31,
        # "20190613 05:35:16"))  # 插入数据，
        # self.tree.insert("", 2, values=(
        # 3, u"进行中", "IOSTBTC",  0.011454, 0.01005, 94534, 0.01005*94534, 8.12, 2, 2.61, 106.32,
        # "20190613 04:44:10"))  # 插入数据，

        self.tree.bind("<Double-1>", self.cmd_tree_double_click)
        self.tree.bind("<Button-3>", self.cmd_right_menu)
        self.tree.bind("<ButtonRelease-1>", self.cmd_left_menu)

        vbar = ttk.Scrollbar(root, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vbar.set)

        self.txt_ui_log = ScrolledText(root, width=180, height=13)
        # 创建一个TAG，其前景色为红色
        self.txt_ui_log.tag_config('INFO', foreground='black', background="white", font=("", 11, 'normal'))
        self.txt_ui_log.tag_config('WARNING', foreground='orange', background="white", font=("", 11, 'normal'))
        self.txt_ui_log.tag_config('ERROR', foreground='red', background="white", font=("", 11, 'normal'))
        self.txt_ui_log.tag_config('SHOW', foreground='green', background="white", font=("", 11, 'bold'))
        self.txt_ui_log.tag_config('BUY', foreground='green', background="white", font=("", 10, 'bold'))
        self.txt_ui_log.tag_config('SELL', foreground='red', background="white", font=("", 10, 'bold'))
        self.txt_ui_log.tag_config('LINK', foreground='blue', underline=True, background="white", font=("", 11, 'normal'))

        self.txt_ui_log.see(END)

        self.btn_login.grid(row=0, column=0, padx=8, pady=10)
        self.btn_api.grid(row=1, column=0, padx=8, pady=10)
        self.btn_coin.grid(row=2, column=0, padx=8, pady=10)
        self.btn_mode_setting.grid(row=3, column=0, padx=8, pady=10)
        self.btn_system_setting.grid(row=4, column=0, padx=8, pady=10)
        self.btn_pending_setting.grid(row=5, column=0, padx=8, pady=10)
        self.btn_wechat.grid(row=6, column=0, padx=8, pady=10)
        self.btn_start.grid(row=7, column=0, padx=8, pady=10)
        self.btn_pause.grid(row=8, column=0, padx=8, pady=10)

        # root.grid_rowconfigure(0, minsize=5)
        root.grid_columnconfigure(1, pad=1)
        root.grid_columnconfigure(2, pad=1)

        self.label_money.grid(row=0, column=1, padx=8, pady=10, ipadx=0, ipady=0, sticky=S+N+W)
        self.opt_money.grid(row=0, column=2, padx=1, pady=10, ipadx=0, ipady=0, sticky=W)

        self.label_mode.grid(row=0, column=3, padx=1, pady=10, sticky=S+N+W)
        self.opt_mode.grid(row=0, column=4, padx=1, pady=10, sticky=S+N+W)

        self.label_balance.grid(row=0, column=5, padx=1, pady=10, sticky=S+N+W)
        self.label_balance_.grid(row=0, column=6, padx=1, pady=10, sticky=S+N+W)

        self.label_principal.grid(row=0, column=7, padx=1, pady=10, sticky=S+N+W)
        self.ety_principal.grid(row=0, column=8, padx=1, pady=10, sticky=S+N+W)
        self.btn_principal.grid(row=0, column=9, padx=1, pady=10, sticky=S+N+W)

        self.label_coin_num.grid(row=1, column=1, padx=1, pady=10, sticky=S+N+W)
        self.label_coin_num_.grid(row=1, column=2, padx=1, pady=10, sticky=S+N+W)

        self.label_total_profit.grid(row=1, column=3, padx=1, pady=10, sticky=S+N+W)
        self.label_total_profit_.grid(row=1, column=4, padx=1, pady=10, sticky=S+N+W)

        self.label_total_run.grid(row=1, column=5, padx=1, pady=10, sticky=S+N+W)
        self.label_total_run_.grid(row=1, column=6, padx=1, pady=10, sticky=S+N+W)
        self.btn_results.grid(row=1, column=7, padx=1, pady=10, sticky=S+N+W)

        self.tree.grid(row=2, column=1, rowspan=4, columnspan=10, padx=8, pady=8, sticky=N+S+W+E)
        # tv.grid(row=0, column=0, sticky=NSEW)
        vbar.grid(row=2, column=11, rowspan=4, padx=0, ipadx=0, pady=8, sticky=N+S+W)

        self.txt_ui_log.grid(row=6, column=1, rowspan=3, columnspan=10, padx=8, pady=8, sticky=N+S+W)

        self.btn_api.config(state="disabled")
        self.btn_coin.config(state="disabled")
        self.btn_mode_setting.config(state="disabled")
        self.btn_system_setting.config(state="disabled")
        self.btn_pause.config(state="disabled")
        self.btn_pending_setting.config(state="disabled")
        self.btn_principal.config(state="disabled")
        self.btn_start.config(state="disabled")
        self.btn_wechat.config(state="disabled")
        self.btn_results.config(state="disabled")

    def logout(self):
        if self.is_login:
            data = {"account": self.account}
            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            url = "http://{}:5000/huobi/logout/".format(config.HOST)
            ret = requests.post(url=url, headers=headers, data=json_data)
            self.is_login = False
            # print(ret.text)

    def cmd_stop_patch(self):
        if not self.tree.selection():
            log_config.output2ui(u"请选中特定的交易组后方可进行操作!", 2)
            return

        item = self.tree.selection()[0]
        group_uri = self.tree.item(item, "values")[11]

        for group in config.TRADE_RECORDS_NOW:
            if group.get("uri", "-1") == group_uri:
                if not group.get("end_time", None):
                    group["stop_patch"] = 1
                    pair = "{}{}".format(group["coin"], group["money"]).upper()
                    log_config.output2ui(u"将停止对交易组{}补仓, 但仍会监控其是否达到盈利条件并进行卖出！".format(pair), 3)
                    strategies.should_update_ui_tree = True
                    break
                else:
                    log_config.output2ui("[提示]该组交易已经结束, 无需设置!", 2)

    def cmd_start_patch(self):
        if not self.tree.selection():
            log_config.output2ui(u"请选中特定的交易组后方可进行操作!", 2)
            return

        item = self.tree.selection()[0]
        group_uri = self.tree.item(item, "values")[11]

        for group in config.TRADE_RECORDS_NOW:
            if group.get("uri", "-1") == group_uri:
                if not group.get("end_time", None):
                    group["stop_patch"] = 0
                    pair = "{}{}".format(group["coin"], group["money"]).upper()
                    log_config.output2ui(u"将继续对交易组{}进行补仓！".format(pair), 3)
                    strategies.should_update_ui_tree = True
                    break
                else:
                    log_config.output2ui("[提示]该组交易已经结束, 无需设置!", 2)

    def cmd_sell_out(self):
        if not self.working:
            log_config.output2ui(u"平仓前请先启动工作, 否则无法平仓!", 2)
            return

        if not self.tree.selection():
            log_config.output2ui(u"请选中特定的交易组后方可进行平仓!", 2)
            return

        item = self.tree.selection()[0]
        group_uri = self.tree.item(item, "values")[11]

        for group in config.TRADE_RECORDS_NOW:
            if group.get("uri", "-1") == group_uri:
                if not group.get("end_time", None):
                    group["grid"] = 0
                    group["sell_out"] = 1
                    pair = "{}{}".format(group["coin"], group["money"]).upper()
                    log_config.output2ui(u"正在对交易组{}进行平仓, 平仓后将开启新一轮监控. 如果您不想再买入该币种, 请在币种设置中取消对该币种的勾选！".format(pair), 3)
                    break
                else:
                    log_config.output2ui("[提示]该组交易已经结束, 无须平仓!", 2)

    def cmd_group_setting(self):
        if not self.tree.selection():
            log_config.output2ui("请选择特定的交易组后方可进行参数设置.", 2)
            return

        item = self.tree.selection()[0]
        group_uri = self.tree.item(item, "values")[11]
        selected_group = None
        for group in config.TRADE_RECORDS_NOW:
            if group.get("uri", "-1") == group_uri:
                if group.get("end_time", None):
                    log_config.output2ui(u"[提示]该组交易已经结束, 不支持参数设置!", 2)
                    return

                selected_group = group
                break

        if not selected_group:
            log_config.output2ui(u"未找到该组交易信息, 无法设置, 将按照全局交易参数进行交易处理!", 2)
            return

        pop = PopupGroupMode(self.root, selected_group)
        if pop.result["is_ok"]:
            for k, v in pop.result.items():
                if k in selected_group.keys():
                    selected_group[k] = v

            log_config.output2ui(
                u"[{}]本组交易策略设置成功! 本组交易将按照您设置的参数进行交易, 其他未设置的交易组仍会按照全局的交易参数进行处理！\n以下是您为当前交易组选择的策略参数: [{}], 补仓数列为: [{}], 补仓参考: [{}], 补仓间隔: {}%, 止盈比例为: {}%, 追踪止盈: {}, "
                u"追踪回撤比例: {}%, 网格止盈: {}, 智能止盈: {}, 智能补仓: {}".format(self.tree.item(item, "values")[1], pop.result["mode_name"],
                                                                              pop.result["patch_name"],
                                                                              pop.result["patch_ref_name"],
                                                                              round(pop.result["patch_interval"] * 100,
                                                                                    4),
                                                                              round(pop.result["limit_profit"] * 100,
                                                                                    4),
                                                                              u"开启" if pop.result["track"] else u"关闭",
                                                                              round(pop.result["back_profit"] * 100, 4),
                                                                              u"开启" if pop.result["grid"] else u"关闭",
                                                                              u"开启" if pop.result[
                                                                                  "smart_profit"] else u"关闭",
                                                                              u"开启" if pop.result[
                                                                                  "smart_patch"] else u"关闭"), 0)
            self.update_trade_info_to_db()

    def cmd_sell_all(self):
        if not self.working:
            log_config.output2ui(u"清仓前请先启动工作, 否则无法清仓!", 2)
            return

        resp = messagebox.askyesno(u"清仓提示", u"将按当前市价卖出当前计价货币({})下的所有处于监控状态的币种, 确认是否继续?".format(self.money.get()))
        if resp:
            for group in config.TRADE_RECORDS_NOW:
                # 将当前计价货币下的所有币种进行清仓
                if not group.get("end_time", None) and group.get("money", "") == self.money.get():
                    group["grid"] = 0
                    group["sell_out"] = 1
                    pair = "{}{}".format(group["coin"], group["money"]).upper()
                    log_config.output2ui(u"正在对交易组{}进行平仓...".format(pair), 3)

    def cmd_left_menu(self, event):
        self.pop_menu.grab_release()

    def cmd_right_menu(self, event):
        # self.tree.selection_set(iid)
        # self.pop_menu.post(event.x_root, event.y_root)
        # return
        # if not self.working:
        #     return

        try:
            iid = self.tree.identify_row(event.y)
            if iid:
                # mouse pointer over item
                self.tree.selection_set(iid)
                self.pop_menu.post(event.x_root, event.y_root)

            else:
                pass
                # mouse pointer not over item
                # occurs when items do not fill frame
                # no action required
        finally:
            self.pop_menu.grab_release()

    def cmd_tree_double_click(self, event):
        if not self.tree.selection():
            return

        item = self.tree.selection()[0]
        group_uri = self.tree.item(item, "values")[11]

        select_record = None
        for record in config.TRADE_RECORDS_NOW:
            uri = record["uri"]
            if group_uri == uri:
                select_record = record
                break

        #输出每一次交易详情
        if select_record:
            # log_config.output2ui(u"本组交易详细交易记录如下：", 0)
            # for trade in select_record["trades"]:
            #     log_config.output2ui("{}".format(trade), 0)
            pop = PopupTradeInfo(parent=root, trade_group=select_record)

    def cmd_mode_change(self, event):
        value = self.mode.get()
        old_mode = config.TRADE_MODE
        for k, v in config.TRADE_MODE_CONFIG.items():
            if v["display"] == value:
                config.TRADE_MODE = k
                break
        if old_mode != config.TRADE_MODE:
            log_config.output2ui(u"交易策略修改为: [{}], 之后所有的交易都会遵循该策略参数运行, 包括已经建仓的交易对．".format(value), 3)
        # print(config.TRADE_MODE)

    def cmd_money_change(self, event):
        if not config.CURRENT_SYMBOLS:
            log_config.output2ui(u"请先去 [币种设置] 窗口中选择您要交易的交易对!")
            return

        if isinstance(event, str):
            money = event
            self.lst_money = list(config.CURRENT_SYMBOLS.keys())
            self.money.set(event)
        else:
            money = self.money.get()

        value = config.CURRENT_SYMBOLS.get(money, None)
        if not value:
            coins_count = 0
            balance = 0
            principal = 0
        else:
            coins_count = len(value.get("coins", []))
            balance = round(value.get("trade", 0), 4)
            principal = value.get("principal", 0)
            if principal == 0:
                principal = round(2*balance, 4)
                value["principal"] = principal

        self.coin_counts.set(coins_count)
        self.balance.set(balance)
        self.principal.set(principal)

        #　将交易列表切换至当前币种下
        self.update_ui_trade_info()
        log_config.output2ui(
            "当前计价货币为: {}, 监控交易对: {} 个, 可用余额: {}, 本金预算: {}".format(money, coins_count, balance, principal))

    def cmd_principal(self):
        try:
            principal = round(float(self.ety_principal.get()), 6)
            money = self.money.get()
            value = config.CURRENT_SYMBOLS.get(money, None)
            if not value or not value.get("coins", []):
                log_config.output2ui(u"当前计价货币不在监控中, 本金预算设置无效．", 2)
                return
            else:
                value["principal"] = principal
                log_config.output2ui(u"系统会按您当前设置的本金预算额: {} {}, 进行智能投资金额分配, 本金预算代表您在当前计价货币下计划投入的本金量, 本金预算可以大于或小于当前可用余额, 默认为当前可用余额的2倍, 越大的本金预算代表单次交易的金额也越多．".format(principal, money), 1)
                if principal > 0 and principal >= 5*value["trade"]:
                    log_config.output2ui(u"注意：您设置的本金预算远远大于当前可用余额, 有可能导致系统运行时资金调用不足, 无法及时补仓, 请您关注.", 2)
        except:
            log_config.output2ui(u"请输入输入有效数字.", 2)
            self.principal.set(config.CURRENT_SYMBOLS.get(self.money.get(), {}).get("principal", 0))

    def save_config(self):
        """
        登录成功后保存用户信息到配置文件
        :return:
        """
        pass

    def save_account_info_to_db(self):
        try:
            conn = sqlite3.connect(config.DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            # user
            cursor.execute(
                "create table if not exists user(id integer primary key autoincrement, name varchar(256), password varchar(256))")

            cursor.execute("select password from `user` where name=?", (config.CURRENT_ACCOUNT, ))
            user = cursor.fetchone()
            if not user:
                cursor.execute("insert into `user` values(?, ?, ?)", (None, config.CURRENT_ACCOUNT, base64.b64encode(bytes(config.CURRENT_PASSWORD, encoding="utf-8"))))
                conn.commit()
        except Exception as e:
            logger.exception("save account info to db. e=%s".format(e))
            return False
        finally:
            conn.close()
        return True

    def save_api_info_to_db(self):
        try:
            conn = sqlite3.connect(config.DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            cursor.execute("select api_key from `api_key` where user=? and platform=?", (config.CURRENT_ACCOUNT, config.CURRENT_PLATFORM))
            api_key = cursor.fetchone()
            if not api_key:
                cursor.execute("insert into `api_key` values(?, ?, ?, ?, ?)", (None, config.CURRENT_ACCOUNT, config.CURRENT_PLATFORM, config.ACCESS_KEY, config.SECRET_KEY))
            else:
                cursor.execute("update `api_key` set api_key=?, secret_key=? where user=? and platform=?", (config.ACCESS_KEY, config.SECRET_KEY, config.CURRENT_ACCOUNT, config.CURRENT_PLATFORM))
            conn.commit()
        except Exception as e:
            logger.exception("save_api_info_to_db. e=%s".format(e))
            return False
        finally:
            conn.close()
        return True

    # "track integer, grid integer, smart_first integer, smart_profit integer, smart_patch integer, patch_mode varchar(20), patch_interval real,
    def get_access_key_from_db(self):
        try:
            conn = sqlite3.connect(config.DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            # api key
            cursor.execute(
                "create table if not exists api_key(id integer primary key autoincrement, user varchar(256), platform varchar(40), "
                "api_key varchar(256), secret_key varchar(256))")
            conn.commit()
            cursor.execute("select platform, api_key, secret_key from `api_key` where user=?", (config.CURRENT_ACCOUNT, ))
            res = cursor.fetchone()
            if not res:
                return "", "", ""

            return res[0], res[1], res[2]
        except Exception as e:
            return "", "", ""
        finally:
            conn.close()

    def get_account_info_from_db(self):
        try:
            conn = sqlite3.connect(config.DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            cursor.execute(
                "create table if not exists user(id integer primary key autoincrement, name varchar(256), password varchar(256))")
            conn.commit()
            cursor.execute("select name, password from `user` where id>=0")
            res = cursor.fetchone()
            if not res:
                return "", ""

            return res[0], res[1]
        except Exception as e:
            return "", ""
        finally:
            conn.close()

    def cmd_login(self):
        def login(account, password):
            sha = hashlib.sha256()
            sha.update(str(password).encode("utf-8"))
            encode_password = sha.hexdigest()
            if account == "15691820861007":
                config.RUN_MODE = 'debug'

            result = {"code": -1, "data": "", "msg": u"网络连接超时！"}
            try:
                retry = 3
                while retry >= 0:
                    # host = "127.0.0.1"
                    data = {"account": account, "password": encode_password}
                    json_data = json.dumps(data)
                    headers = {'Content-Type': 'application/json'}
                    url = "http://{}:5000/huobi/login/".format(config.HOST)
                    ret = requests.post(url=url, headers=headers, data=json_data)
                    if ret.status_code == 200:
                        result = json.loads(ret.text)
                        break
                    else:
                        retry -= 1
                        time.sleep(1)
            except Exception as e:
                pass

            return result

        # 读出账号信息
        try:
            account, password = self.get_account_info_from_db()

            if not account:
                with open(r'ddu.yml', 'r') as f:
                    yaml_dict = yaml.load(f, Loader=yaml.FullLoader)

                config.CURRENT_ACCOUNT = str(base64.b64decode(yaml_dict.get("account", b"")), encoding="utf-8")
                config.CURRENT_PASSWORD = str(base64.b64decode(yaml_dict.get("password", b"")), encoding="utf-8")
                config.ACCESS_KEY = str(base64.b64decode(yaml_dict.get("access_key", b"")), encoding="utf-8")
                config.SECRET_KEY = str(base64.b64decode(yaml_dict.get("secret_key", b"")), encoding="utf-8")
                config.CURRENT_PLATFORM = str(base64.b64decode(yaml_dict.get("platform", b"")), encoding="utf-8")
            else:
                config.CURRENT_ACCOUNT = account
                config.CURRENT_PASSWORD = str(base64.b64decode(password), encoding="utf-8")
        except:
            pass

        pop = PopupLogin(parent=root)
        if pop.result["is_ok"]:
            account = pop.result["account"]
            password = pop.result["password"]
            remember = pop.result["remember"]

            ret = login(account, password)
            code = ret.get("code", 0)
            if code != 1:
                self.is_login = False
                messagebox.showwarning(u"错误", ret.get("msg", u"登录失败!"))
                return
            else:
                config.CURRENT_ACCOUNT = account
                config.CURRENT_PASSWORD = password
                if remember:
                    self.save_account_info_to_db()
                    # yaml_dict = {"account": base64.b64encode(bytes(account, encoding="utf-8")),
                    #              "password": base64.b64encode(bytes(password, encoding="utf-8"))}
                    # try:
                    #     with open("ddu.yml", 'w') as f:
                    #         yaml.dump(yaml_dict, f)
                    # except:
                    #     pass

                self.account = account
                self.is_login = True
                self.btn_api.config(state="normal")
                self.btn_login.config(state="disabled")
                self.btn_results.config(state="normal")
                self.btn_login_str.set(u"登录成功")
                root.title(config.TITLE+"--{}, 到期时间:{}".format(self.account, ret.get("data", "")))
                log_config.output2ui(u"登录成功，余额到期时间：{}.".format(ret.get("data", "")), 0)
                log_config.output2ui(u"第二步, 请点击 [API设置], 在弹出窗口中选择你要交易的平台, 并输入该平台的API授权码进行授权．", 1)

    def cmd_api(self):
        def show_information():
            self.txt_ui_log.insert(END, u"[温馨提示] 目前本系统仅对接火币平台, 其他主流平台正在紧急接入中. 如果您还没有火币平台账号，请参考[火币平台用户指导书]，简单几步带您完成从注册到交易．注册时使用我们的 [邀请注册链接] (邀请码 8jbg4)可免费获得本系统100天的试用时长.\n")

            urls = ['https://www.huobi.de.com/topic/invited/?invite_code=8jbg4&from=groupmessage',
                   'https://www.huobi.co/zh-cn/',
                   'https://www.huobi.co/zh-cn/apikey/',
                   'http://github.com/PythonAwesome/HuobiUserGuide/blob/master/README.md',
                   'https://www.jianshu.com/p/c4c4e3325a28',
                   'https://www.jianshu.com/p/de6b120cf8d7'
                   ]
            name = [u'邀请注册链接', u'火币全球官方网站(火币APP下载也在这里)', u'火币API Key申请(开通授权和身份验证必需)', u'火币平台用户指导书', u"如何提高被动收入",
                    u"本系统使用手册"]
            m = 0
            for each in name:
                self.txt_ui_log.tag_config(m, foreground='blue', underline=True, font=("", 11, 'normal'))
                self.txt_ui_log.tag_bind(m, '<Enter>', self.show_hand_cursor)
                self.txt_ui_log.tag_bind(m, '<Leave>', self.show_arrow_cursor)
                self.txt_ui_log.insert(END, each + '\n', m)
                self.txt_ui_log.tag_bind(m, '<Button-1>', self.handlerAdaptor(self.click, url=urls[m]))
                m += 1

            self.txt_ui_log.see(END)

        if not self.is_login:
            messagebox.showinfo(u"提示", u"请先进行 [登 录]！")
            return

        show_information()
        platform, api_key, secret_key = self.get_access_key_from_db()
        if api_key:
            config.CURRENT_PLATFORM = platform
            config.ACCESS_KEY = api_key
            config.SECRET_KEY = secret_key

        pop = PopupAPI(parent=root)
        if pop.result["is_ok"]:
            config.CURRENT_PLATFORM = pop.result["platform"]
            config.ACCESS_KEY = pop.result["access_key"]
            config.SECRET_KEY = pop.result["secret_key"]
            if not config.ACCESS_KEY:
                log_config.output2ui(u"请设置授权码！", 2)
                return

            log_config.output2ui(u"你当前选择的平台是: [{}], 授权码为: [{}].".format(pop.result["platform_display"], config.ACCESS_KEY))
            # if pop.result.get("remember", 1):
            #     self.save_api_info_to_db()
                # yaml_dict = {"account": base64.b64encode(bytes(config.CURRENT_ACCOUNT, encoding="utf-8")),
                #              "password": base64.b64encode(bytes(config.CURRENT_PASSWORD, encoding="utf-8")),
                #              "access_key": base64.b64encode(bytes(config.ACCESS_KEY, encoding="utf-8")),
                #              "secret_key": base64.b64encode(bytes(config.SECRET_KEY, encoding="utf-8")),
                #              "platform": base64.b64encode(bytes(config.CURRENT_PLATFORM, encoding="utf-8"))
                #              }
                # f = open(r'ddu.yml', 'w')
                # yaml.dump(yaml_dict, f)

            if pop.result.get("load_history", 1):
                self.load_trades()

            self.api_verify(remember=pop.result.get("remember", 1))

    def cmd_coin(self):
        if not self.is_api_ok:
            messagebox.showinfo(u"提示", u"请先进行 [API设置]!")
            return

        pop = PopupCoins(parent=root, history_pairs=self.history_pairs)
        if pop.result["is_ok"]:
            config.CURRENT_SYMBOLS = pop.result["symbols"]
            logger.info("current symbols: {}".format(config.CURRENT_SYMBOLS))
            msg = ""
            coins_count = 0
            config.NEED_TOBE_SUB_SYMBOL.clear()     # 再次设置时要把上一次的清空
            for money, value in config.CURRENT_SYMBOLS.items():
                coins = value.get("coins", [])
                if coins:
                    for coin in coins:
                        # 保存交易对, 用于加载历史数据
                        config.NEED_TOBE_SUB_SYMBOL.append("{}{}".format(coin["coin"], money).lower())
                        msg += "{}/{}, ".format(coin["coin"], money)
                        coins_count += 1
            log_config.output2ui(u"您总共选择了{}组交易对: {}.".format(coins_count, msg[0:-2]), 0)
            self.init_history()

    def cmd_start(self):
        def start(hb):
            logger.info("start work!!")
            # log_config.output2ui(u"系统启动中...", 1)
            log_config.output2ui(u"系统开始工作, 将为您智能选择最佳交易时机进行自动化交易! 请保证您的电脑网络通畅, 不要随意停止或关闭本系统, 否则可能导致历史数据丢失, 错过最佳交易时机!", 1)
            log_config.output2ui(u"点击 [全部停止] 可停止程序自动交易．", 8)
            hb.run()
            logger.info("work over!!")

        if not self.is_login:
            log_config.output2ui(u"请先进行登录！", 2)
            messagebox.showinfo(u"提示", u"请先进行登录！")
            return

        if not self.is_api_ok:
            log_config.output2ui(u"请先进行API设置！", 2)
            messagebox.showinfo(u"提示", u"请先进行API设置！")
            return

        if not config.NEED_TOBE_SUB_SYMBOL:
            log_config.output2ui(u"请先选择您想要交易的币种!", 2)
            messagebox.showinfo(u"提示", u"请先选择您想要交易的币种！")
            return

        self.btn_start.config(state="disabled")
        if not self._hb:
            self._hb = Huobi()

        th = Thread(target=start, args=(self._hb,))
        th.setDaemon(True)
        th.start()

        self.btn_start.config(state="disabled")
        self.btn_start_str.set(u"正在运行")
        self.btn_pause.config(state="normal")
        self.btn_coin.config(state="disabled")
        self.btn_api.config(state="disabled")
        self.btn_login.config(state="disabled")
        self.btn_mode_setting.config(state="normal")
        self.btn_system_setting.config(state="normal")
        self.btn_pending_setting.config(state="normal")
        # self.btn_wechat.config(state="normal")
        self.btn_principal.config(state="normal")
        time.sleep(0.5)
        self.register_strategy()
        self.start_check_strategy()
        self.working = True

    def cmd_stop(self):
        if not self.working:
            return

        logger.info("stop_work!")
        if self._hb:
            self._hb.exit()

        self.clean_strategy()
        self.stop_check_strategy()

        log_config.output2ui(u"系统已停止工作!", 2)
        self.working = False

        self.btn_start_str.set(u"立即启动")
        self.btn_pause.config(state="disabled")
        self.btn_start.config(state="normal")
        self.btn_coin.config(state="normal")
        self.btn_api.config(state="normal")
        # self.btn_login.config(state="normal")

    def cmd_mode_setting(self):
        pop = PopupMode(parent=self.root)
        if pop.result["is_ok"]:
            config.TRADE_MODE = pop.result.get("mode", "robust")
            for k, v in pop.result.items():
                if k in config.TRADE_MODE_CONFIG[config.TRADE_MODE].keys():
                    config.TRADE_MODE_CONFIG[config.TRADE_MODE][k] = v

            log_config.output2ui(u"交易策略设置成功! 您当前选择的策略为: [{}], 补仓数列为: [{}], 补仓参考: [{}], 补仓间隔: {}%, 止盈比例为: {}%, 追踪止盈: {}, "
                                 u"追踪回撤比例: {}%, 网格止盈: {}, 智能建仓: {}, 智能止盈: {}, 智能补仓: {}".format(pop.result["mode_name"], pop.result["patch_name"],
                                                                           pop.result["patch_ref_name"], round(pop.result["patch_interval"]*100, 4),
                                                                         round(pop.result["limit_profit"]*100, 4),
                                                                         u"开启" if pop.result["track"] else u"关闭",
                                                                         round(pop.result["back_profit"]*100, 4),
                                                                         u"开启" if pop.result["grid"] else u"关闭",
                                                                         u"开启" if pop.result["smart_first"] else u"关闭",
                                                                         u"开启" if pop.result["smart_profit"] else u"关闭",
                                                                            u"开启" if pop.result["smart_patch"] else u"关闭"), 0)

            self.mode.set(pop.result["mode_name"])

    def cmd_system_setting(self):
        pop = PopupSystem(parent=self.root)
        if pop.result["is_ok"]:
            config.TRADE_MIN_LIMIT_VALUE = pop.result.get("trade_min", 0)
            config.TRADE_MAX_LIMIT_VALUE = pop.result.get("trade_max", 0)

    def cmd_pending_setting(self):
        pass

    def cmd_wechat(self):
        self.btn_wechat.config(state="disabled")
        if config.WECHAT_NOTIFY:
            config.WECHAT_NOTIFY = False
            log_config.output2ui("正在退出微信登录...")
            th = Thread(target=self.logout_wechat_aycn)
            th.setDaemon(True)
            th.start()
        else:
            config.WECHAT_NOTIFY = True
            log_config.output2ui(u"正在登录微信, 可能需要您使用手机微信扫码登录或者需要您在手机上确认登录！否则您可能无法收到实时交易信息, 不过您也可以在交易平台官方APP中查看历史交易记录．", 0)
            th = Thread(target=self.login_wechat_aycn)
            th.setDaemon(True)
            th.start()

    def show_hand_cursor(self, event):
        self.txt_ui_log.config(cursor='arrow')

    def show_arrow_cursor(self, event):
        self.txt_ui_log.config(cursor='xterm')

    def click(self, event, url):
        webbrowser.open(url)

    def handlerAdaptor(self, fun, **kwds):
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)

    def init_history(self):
        def init_history_thread(hb):
            ret = self._hb.init()  # 这一步是必须的，先同步处理
            if not ret:
                self.btn_start.config(state="disabled")
                self.gressbar_init_history.quit()
                return

            ret2 = hb.init_history()
            self.gressbar_init_history.quit()
            if not (ret and ret2):
                logger.error("init service failed.")
                log_config.output2ui(u"系统初始化失败! 请检查网络状况并重试!", 3)
                messagebox.showwarning("警告", u"系统初始化失败! 请检查网络状况并重试!")
                self.btn_start.config(state="disabled")
                return False

            log_config.output2ui(u"加载历史交易数据成功!", 1)
            log_config.output2ui(u"第四步, 请点击 [立即启动], 程序将开启自动化交易. 如需进行自定义交易策略请点击[策略设置]按钮, 非专业人士不建议您对策略进行修改. 策略修改在程序运行过程当中立即生效, 不需要重新启动. ", 1)
            self.btn_start.config(state="normal")
            self.btn_mode_setting.config(state="normal")
            self.btn_pending_setting.config(state="normal")
            self.btn_system_setting.config(state="normal")
            self.btn_pending_setting.config(state="normal")
            self.btn_principal.config(state="normal")
            self.update_ui_balance()

        def update_balance_thread():
            strategies.update_balance()
            bal_msg = ""
            first_money_name = ""       # 第一个money名字
            for money, value in config.CURRENT_SYMBOLS.items():
                coins = value.get("coins", [])
                if coins:
                    if not first_money_name:
                        first_money_name = money
                    bal_msg += u"[{}: 可用{}, 冻结{}]    ".format(money, round(value["trade"], 6), round(value["frozen"], 6))
                    for coin in coins:
                        bal_msg += u"[{}: 可用{}, 冻结{}]    ".format(coin["coin"], round(coin["trade"], 6), round(coin["frozen"], 6))
            log_config.output2ui(u"您所选择的各交易对的余额及冻结情况如下：{}".format(bal_msg), 0)
            self.cmd_money_change(event=first_money_name)

        huobi.save_history_trade_vol(config.NEED_TOBE_SUB_SYMBOL)
        if not self._hb:
            self._hb = Huobi()

        th = Thread(target=update_balance_thread)
        th.setDaemon(True)
        th.start()

        th = Thread(target=init_history_thread, args=(self._hb,))
        th.setDaemon(True)
        th.start()

        self.gressbar_init_history.start(text=u"正在加载历史交易数据, 请稍等...")
        return True

    def start_work(self):
        def start(hb):
            logger.info("start work!!")
            # log_config.output2ui(u"系统启动中...", 1)
            log_config.output2ui(u"系统开始工作，将为您智能发现最佳交易时机并进行自动交易!", 8)
            log_config.output2ui(u"点击 [停止工作] 可停止程序自动交易．", 8)
            hb.run()
            logger.info("work over!!")

        if not self.verify:
            log_config.output2ui(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!", 5)
            messagebox.showerror(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!")
            self.run_status_text.set(u"待授权")
            return

        strategies.trade_advise_update()

        process.ORG_COIN_TRADE = None
        process.ORG_COIN_FROZEN = None
        process.ORG_DOLLAR_TRADE = None
        process.ORG_DOLLAR_FROZEN = None
        process.ORG_COIN_TOTAL = None
        process.ORG_DOLLAR_TOTAL = None
        process.ORG_PRICE = None
        process.ORG_DOLLAR_TOTAL = None  # 总价值金量, 所有资产换成usdt

        if not self._hb:
            self._hb = Huobi()

        self.register_strategy()
        self.start_check_strategy()

        th = Thread(target=start, args=(self._hb,))
        th.setDaemon(True)
        th.start()
        self.stop_button.config(state="normal")
        self.start_button.config(state="disabled")
        self.start_check_strategy_button.config(state="normal")
        self.verify_identity_button.config(state="disabled")
        self.working = True

    def login_wechat_aycn(self):
        ret = wechat_helper.login_wechat()
        self.btn_wechat.config(state="normal")
        self.btn_wechat_str.set(u"取消微信通知")
        log_config.output2ui(u"微信登录成功, 实时交易信息和账号周期统计信息将通过微信发送给您的[文件传输助手], 请注意查收！", 0)

    def logout_wechat_aycn(self):
        ret = wechat_helper.logout()
        self.btn_wechat.config(state="normal")
        self.btn_wechat_str.set(u"微信通知")
        log_config.output2ui(u"取消微信通知成功!", 0)


    def login_wechat(self):
        log_config.output2ui(u"正在登录微信, 可能需要您使用手机微信扫码登录或者需要您在手机上确认登录！否则您可能无法收到实时交易信息, 不过您也可以在交易平台官方APP中查看历史交易记录．", 0)
        th = Thread(target=self.login_wechat_aycn)
        th.setDaemon(True)
        th.start()

    def start_check_strategy(self):
        if not self.is_api_ok or not self.is_login:
            log_config.output2ui(u"请先进行登录和API设置", 3)
            return

        # 策略检测线程启动
        logger.info("start_check_strategy...")
        log_config.output2ui(u"正在加载策略...", 0)
        self._strategy_pool.start_work()
        log_config.output2ui(u"加载策略成功!", 1)

    def stop_check_strategy(self):
        logger.info("stop_check_strategy...")
        log_config.output2ui(u"正在停止执行策略...", 0)
        self._strategy_pool.stop_work()
        log_config.output2ui(u"停止执行策略成功!", 0)

    def register_strategy(self):
        if not self.is_api_ok or not self.is_login:
            log_config.output2ui(u"请先进行登录和API设置", 3)
            return

        logger.info("register_strategy.")
        log_config.output2ui(u"正在注册策略...", 1)
        self._strategy_pool.clean_all()
        for strategy in strategies.STRATEGY_LIST:
            logger.info("register_strategy, strategy={}".format(strategy.name))
            log_config.output2ui("register_strategy, strategy={}".format(strategy.name), 7)
            self._strategy_pool.register(strategy)
        log_config.output2ui(u"注册策略成功!", 1)

    def clean_strategy(self):
        logger.warning("clean_strategy...")
        log_config.output2ui(u"正在清空所有策略...", 0)
        self._strategy_pool.clean_all()
        log_config.output2ui(u"清空所有策略成功!", 0)

    def center_window(self, width, height):
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(size)

    def wait_buy_sell(self, price):
        if not price or not self.working:
            # logger.info("wait_buy_sell not be trigger!, price={}, working={}".format(price, self.working))
            return False

        buy_prices = config.WAIT_BUY_PRICE
        buy_amounts = config.WAIT_BUY_ACCOUNT
        sell_prices = config.WAIT_SELL_PRICE
        sell_amounts = config.WAIT_SELL_ACCOUNT

        symbol = config.NEED_TOBE_SUB_SYMBOL[0]
        for i, buy_price in enumerate(buy_prices):
            # 循环遍历挂单买
            buy_amount = buy_amounts[i]
            if buy_price > 0 and buy_amount > config.TRADE_MIN_LIMIT_VALUE*1.02 and self.dollar_trade>config.TRADE_MIN_LIMIT_VALUE*1.02:
                if price <= buy_price:
                    if buy_amounts > self.dollar_trade:
                        buy_amount = self.dollar_trade

                    ret = strategies.buy_market(symbol, amount=buy_amount, record=True, current_price=price)
                    if ret[0]:
                        msg = u"挂单买入{}成功: 挂单价格={}$, 挂单金额={}$, 实际价格={}$, 实际买入金额={}$.".format(symbol, buy_price, buy_amount, price, ret[1])
                        success = False
                        if ret[0] == 1:
                            msg += u"-交易成功！"
                            config.WAIT_BUY_ACCOUNT[i] = buy_amount - ret[1]
                            success = True
                        elif ret[0] == 2:
                            msg += u"-交易被取消, 取消原因: {}!".format(ret[2])
                        elif ret[0] == 3:
                            msg += u"-交易失败, 失败原因: {}！".format(ret[2])
                        log_config.output2ui(msg, 6)
                        logger.warning(msg)
                        log_config.notify_user(msg, own=True)
                        log_config.notify_user(log_config.make_msg(0, symbol, price))



            # 循环遍历挂单卖
            sell_price = sell_prices[i]
            sell_amount = sell_amounts[i]
            if sell_price > 0 and sell_amount > 0.0001 and self.coin_trade>0.0001 and sell_amount*price>config.TRADE_MIN_LIMIT_VALUE*1.02 and self.coin_trade*price>config.TRADE_MIN_LIMIT_VALUE*1.02:
                if price >= sell_price:
                    if sell_amount > self.coin_trade:
                        sell_amount = self.coin_trade

                    ret = strategies.sell_market(symbol, amount=sell_amount, record=False, current_price=price)
                    if ret[0]:
                        msg = u"挂单卖出{}: 挂单价格={}, 挂单个数={}个, 实际价格={}, 实际挂单卖出个数={}个.".format(symbol,
                                sell_price, sell_amount, price, ret[1])
                        success = False
                        if ret[0] == 1:
                            msg += u"-交易成功！"
                            config.WAIT_SELL_ACCOUNT[i] = sell_amount - ret[1]
                            success = True
                        elif ret[0] == 2:
                            msg += u"-交易被取消, 取消原因: {}!".format(ret[2])
                        elif ret[0] == 3:
                            msg += u"-交易失败, 失败原因: {}！".format(ret[2])
                        log_config.output2ui(msg, 7)
                        logger.warning(msg)
                        log_config.notify_user(msg, own=True)
                        log_config.notify_user(log_config.make_msg(1, symbol, price))

    def update_coin(self, price=None):
        """
        更新盈利信息
        :param price:
        :return:
        """
        try:
            if not price:
                price_text = self.price_text.get()
                price = 0
                if len(price_text.split(":")) > 1:
                    price = float(price_text.split(":")[1])
                else:
                    price = 0
            else:
                price = float(price)

            bal_text = self.bal_text.get()
            if not bal_text:
                return
            coin_str = bal_text.split(",")[0].split("/")
            dollar_str = bal_text.split(",")[1].split("/")
            if len(coin_str) > 0 and len(dollar_str) > 0:

                coin_trade = float(coin_str[0])
                coin_frozen = float(coin_str[1])
                self.coin_trade = coin_trade

                dollar_trade = float(dollar_str[0])
                self.dollar_trade = dollar_trade
                dollar_frozen = float(dollar_str[1])
                total_coin_value = coin_trade + coin_frozen + (dollar_trade + dollar_frozen) / price

                total_dollar_value = (coin_trade + coin_frozen) * price + dollar_trade + dollar_frozen
                if total_dollar_value>0:
                    position = (coin_trade + coin_frozen)*price / total_dollar_value
                else:
                    position = 0
                self.coin_text.set("{}/{}/{}%".format(round(total_coin_value, 4), round(total_dollar_value, 2), round(position*100, 2)))
                if not process.ORG_COIN_TOTAL:
                    process.START_TIME = datetime.now()
                    if total_dollar_value>0:
                        process.ORG_CHICANG = (coin_trade+coin_frozen)*price/total_dollar_value
                    else:
                        process.ORG_CHICANG = 0
                    process.ORG_COIN_TRADE = coin_trade
                    process.ORG_COIN_FROZEN = coin_frozen
                    process.ORG_DOLLAR_TRADE = dollar_trade
                    process.ORG_DOLLAR_FROZEN = dollar_frozen
                    process.ORG_COIN_TOTAL = total_coin_value
                    process.ORG_DOLLAR_TOTAL = total_dollar_value
                    process.ORG_PRICE = price
                    # 更新总额, 初始化更新一次即可
                    self.origin_text.set("{}/{}/{}/{}".format(price, round(coin_trade + coin_frozen,4), round(dollar_trade + dollar_frozen, 2), round(total_dollar_value, 2)))

                profit_coin = round(total_coin_value - process.ORG_COIN_TOTAL, 3)
                profit_dollar = round(total_dollar_value - process.ORG_DOLLAR_TOTAL, 3)
                self.profit_text.set("{}/{}".format(profit_coin, profit_dollar))

                #更新大盘涨跌幅和当前账户的涨跌幅
                process.CURRENT_TOTAL_DOLLAR_VALUE = total_dollar_value
                process.CURRENT_TOTAL_COIN_VALUE = total_coin_value
                if process.ORG_DOLLAR_TOTAL>0:
                    account_zhang = round((total_dollar_value - process.ORG_DOLLAR_TOTAL)*100 / process.ORG_DOLLAR_TOTAL, 3)
                else:
                    account_zhang = 0

                self.now_text.set("{}% / {}%".format(round((price-process.ORG_PRICE)*100/process.ORG_PRICE, 2), account_zhang))
        except Exception as e:
            logger.exception("update_coin e={}".format(e))

    def update_trade_info_to_db(self):
        try:
            conn = sqlite3.connect(config.DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            # trade
            cursor.execute(
                """create table if not exists trade (id integer primary key autoincrement, buy_type varchar(128), 
                sell_type varchar(128), limit_profit real, back_profit real, track integer, buy_time timestamp, 
                sell_time timestamp, coin varchar(10), money varchar(10), amount real, buy_price real, cost real, 
                is_sell integer, sell_price real, profit_percent real, profit real, failed_times integer, 
                uri varchar(100), group_uri varchar(100), user varchar(128), platform varchar(40))""")

            # trade_group
            cursor.execute(
                "create table if not exists trade_group(id integer primary key autoincrement, build varchar(20), mode varchar(20), smart_profit integer,"
                "smart_patch integer, patch_mode varchar(20), coin varchar(20), money varchar(20), grid integer, track integer, amount real, cost real,"
                "avg_price real, max_cost real, profit real, profit_percent real, last_profit_percent real, limit_profit real, back_profit real, "
                "buy_counts integer, sell_counts integer, patch_index integer, patch_ref integer, patch_interval real, last_buy_price real, "
                "start_time timestamp, end_time timestamp, last_update timestamp, uri varchar(100), principal real, last_sell_failed timestamp, sell_out integer,"
                "is_sell integer, stop_patch integer, first_cost real, user varchar(128), platform varchar(40))")

            # trade_mode
            cursor.execute(
                "create table if not exists trade_mode(id integer primary key autoincrement, mode varchar(20), limit_profit real, back_profit real)")

            conn.commit()
            cursor.execute('select uri from trade_group where id>=0')
            group_uris = []
            results = cursor.fetchall()
            if results:
                for res in results:
                    group_uris.append(res[0])

            cursor.execute('select uri from trade where id>=0')
            trade_uris = []
            results = cursor.fetchall()
            if results:
                for res in results:
                    trade_uris.append(res[0])

            for group in config.TRADE_RECORDS_NOW:
                if group.get("uri", "") not in group_uris:
                    cursor.execute(
                        'insert into `trade_group` values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (None, group.get("build", ""), group.get("mode", ""), group.get("smart_profit", -1),
                         group.get("smart_patch", -1),
                         group.get("patch_mode", ""), group.get("coin", ""), group.get("money", ""),
                         group.get("grid", -1),
                         group.get("track", -1), group.get("amount", 0), group.get("cost", 0),
                         group.get("avg_price", 0),
                         group.get("max_cost", 0), group.get("profit", 0), group.get("profit_percent", 0),
                         group.get("last_profit_percent", 0), group.get("limit_profit", -1),
                         group.get("back_profit", -1),
                         group.get("buy_counts", 0), group.get("sell_counts", 0), group.get("patch_index", 0),
                         group.get("patch_ref", -1), group.get("patch_interval", -1), group.get("last_buy_price", 0),
                         group.get("start_time", None),
                         group.get("end_time", None), group.get("last_update", None), group.get("uri", ''),
                         group.get("principal", -1),
                         group.get("last_sell_failed", None), group.get("sell_out", 0), group.get("is_sell", 0),
                         group.get("stop_patch", 0), group.get("first_cost", 10), group.get("user", config.CURRENT_ACCOUNT),
                         group.get("platform", config.CURRENT_PLATFORM)))
                else:
                    cursor.execute(
                        'update `trade_group` set build=?, mode=?, smart_profit=?, smart_patch=?, patch_mode=?, grid=?, '
                        'track=?, amount=?, cost=?, avg_price=?, max_cost=?, profit=?, profit_percent=?, '
                        'last_profit_percent=?, limit_profit=?, back_profit=?, buy_counts=?, sell_counts=?, patch_index=?, '
                        'patch_ref=?, patch_interval=?, last_buy_price=?, start_time=?, end_time=?, last_update=?, '
                        'principal=?, last_sell_failed=?, sell_out=?, stop_patch=?, is_sell=? where uri=? and user=?',
                        (group.get("build", ""), group.get("mode", ""), group.get("smart_profit", -1),
                         group.get("smart_patch", -1),
                         group.get("patch_mode", ""), group.get("grid", -1),
                         group.get("track", -1), group.get("amount", 0), group.get("cost", 0),
                         group.get("avg_price", 0),
                         group.get("max_cost", 0), group.get("profit", 0), group.get("profit_percent", 0),
                         group.get("last_profit_percent", 0), group.get("limit_profit", -1),
                         group.get("back_profit", -1),
                         group.get("buy_counts", 0), group.get("sell_counts", 0), group.get("patch_index", 0),
                         group.get("patch_ref", -1), group.get("patch_interval", -1), group.get("last_buy_price", 0),
                         group.get("start_time", None),
                         group.get("end_time", None), group.get("last_update", None), group.get("principal", -1),
                         group.get("last_sell_failed", None), group.get("sell_out", 0), group.get("stop_patch", 0),
                         group.get("is_sell", 0),
                         group.get("uri", ''), group.get("user", config.CURRENT_ACCOUNT)))
                conn.commit()

                trades = group.get("trades", [])
                for trade in trades:
                    if trade.get("uri", "") not in trade_uris:
                        cursor.execute(
                            "insert into `trade` values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (None, trade.get("buy_type", ""), trade.get("sell_type", ""),
                             trade.get("limit_profit", -1), trade.get("back_profit", -1),
                             trade.get("track", -1), trade.get("buy_time", None),
                             trade.get("sell_time", None), trade.get("coin", ""),
                             trade.get("money", ""), trade.get("amount", 0),
                             trade.get("buy_price", 0), trade.get("cost", 0),
                             trade.get("is_sell", 0), trade.get("sell_price", 0),
                             trade.get("profit_percent", 0), trade.get("profit", 0),
                             trade.get("failed_times", 0), trade.get("uri", ""),
                             trade.get("group_uri", ""), trade.get("user", config.CURRENT_ACCOUNT),
                             trade.get("platform", config.CURRENT_PLATFORM)))
                    else:
                        cursor.execute(
                            "update `trade` set buy_type=?, sell_type=?, limit_profit=?, back_profit=?, track=?,"
                            "buy_time=?, sell_time=?, amount=?, buy_price=?, cost=?, is_sell=?, sell_price=?, "
                            "profit_percent=?, profit=?, failed_times=? where uri=?",
                            (trade.get("buy_type", ""), trade.get("sell_type", ""),
                             trade.get("limit_profit", -1), trade.get("back_profit", -1),
                             trade.get("track", -1), trade.get("buy_time", None),
                             trade.get("sell_time", None), trade.get("amount", 0),
                             trade.get("buy_price", 0), trade.get("cost", 0),
                             trade.get("is_sell", 0), trade.get("sell_price", 0),
                             trade.get("profit_percent", 0), trade.get("profit", 0),
                             trade.get("failed_times", 0), trade.get("uri", "")))
                conn.commit()
            conn.commit()
        except Exception as e:
            log_config.output2ui(u"更新数据失败!", 2)
            logger.exception(str(e))
        finally:
            conn.close()

    def update_ui_trade_info(self):
        self.tree.delete(*self.tree.get_children())
        index = 0
        current_price_dict = {}
        all_profit = 0  # 所有当前货币的总盈利
        for money, value in config.CURRENT_SYMBOLS.items():
            coins = value.get("coins", [])
            for coin in coins:
                coin_name = coin.get("coin", "")
                if coin_name:
                    current_price_dict["{}/{}".format(coin_name, money)] = coin.get("price", 0)

        # config.TRADE_RECORDS_NOW.sort(cmp=None, key=lambda x: x["start_time"], reverse=False)
        #去重
        unique_uri = []
        unique_trades = []
        for trade in config.TRADE_RECORDS_NOW:
            if trade["uri"] not in unique_uri:
                unique_uri.append(trade["uri"])
                unique_trades.append(trade)

        config.TRADE_RECORDS_NOW = unique_trades

        #对交易进行排序，未结束的在前，然后再按更新时间倒排序
        tt_list_not_selled = list(filter(lambda x: x.get("is_sell", 0) == 0 and not x.get("end_time"), config.TRADE_RECORDS_NOW))
        tt_list_not_selled.sort(key=lambda x: x["last_update"], reverse=True)

        tt_list_selled = list(filter(lambda x: x.get("is_sell", 0) == 1 or x.get("end_time"), config.TRADE_RECORDS_NOW))
        tt_list_selled.sort(key=lambda x: x["last_update"], reverse=True)

        # 页面最多显示50个
        if len(tt_list_not_selled) < 50:
            tt_list_not_selled += tt_list_selled[0: 50-len(tt_list_not_selled)]

        for trade in tt_list_not_selled:
            if trade["money"] != self.money.get():
                continue

            trade_pair = "{}/{}".format(trade["coin"], trade['money'])
            current_price = current_price_dict.get(trade_pair, 0)
            total_profit = trade["profit"]        # 单组的累计营利
            all_profit += total_profit          # 所有当前货币对的总盈利

            if not trade.get("end_time", None):
                state = u"监控中"
            if trade.get("stop_patch", 0):
                state = u"停止补仓"
            if trade.get("end_time"):
                state = u"已完成"

            self.tree.insert("", index, values=(index+1,
                                                trade_pair,
            state,
            # current_price,
            round(trade["avg_price"], 6),
            round(trade["amount"], 6),
            round(trade["cost"], 6),
            trade["buy_counts"],
            trade["sell_counts"],
            round(trade["last_profit_percent"]*100, 3),
            round(total_profit, 6),
            round(trade["profit_percent"] * 100, 3),
            trade.get("uri", ""),
            trade["last_update"].strftime("%m%d %H:%M:%S") if trade.get("last_update", None) else "",
            trade["end_time"].strftime("%m%d %H:%M:%S") if trade.get("end_time", None) else ""))
            index += 1

        self.total_profit.set(round(all_profit, 4))
        self.coin_counts.set(index)
        self.update_trade_info_to_db()

    def update_ui_balance(self):
        money = self.money.get()
        value = config.CURRENT_SYMBOLS.get(money, None)
        if not value:
            coins_count = 0
            balance = 0
            principal = 0
        else:
            coins_count = len(value.get("coins", []))
            balance = round(value.get("trade", 0), 4)
            principal = value.get("principal", 0)
            if principal == 0:
                principal = round(2*balance, 4)
                value["principal"] = principal

        self.coin_counts.set(coins_count)
        self.balance.set(balance)
        self.principal.set(principal)

    def update_ui(self):
        # # 每1000毫秒触发自己，形成递归，相当于死循环
        # self.root.after(1000, self.process_msg)
        logger.info("Welcome to Huobi Trade System")
        log_config.output2ui(u"    欢迎使用DDU智能量化交易系统！　本系统由资深量化交易专家和算法团队倾力打造,支持多个主流交易平台.系统经过大量的模拟测试与实盘操作测试, 具有收益稳定, 风险可控的优点."
                             u"本地化运行，更加安全可控，策略可定制，使用更方便!　系统结合历史与实时数据进行分析，加上内置的多套专业策略组合算法，包括智能建仓, 智能补仓, 止盈追踪, 网格量化止盈追踪等．"
                             u"系统将根据您选择的交易策略，智能发现属于您的最佳交易时机进行自动化交易，系统还提供交易实时微信通知, 收益情况按天统计等贴心功能, "
                             u"真正帮您实现24小时实时盯盘，专业可靠，稳定盈利看得见！\n", 1)
        log_config.output2ui(
            u"免责声明:\n  1. 使用本系统时，系统将会根据程序判断自动帮您进行交易，因此产生的盈利或亏损均由您个人负责，与系统开发团队无关\n  2. 本系统需要您提供您在交易平台官网（如火币, OKEx等）申请的API密钥，获取平台授权后方能正常运行,请您妥善保管好自己的密钥,发生丢失造成的财产损失与本系统无关.\n  3. 因操作失误,断网,断电,程序异常等因素造成的经济损失与系统开发团队无关\n  4. 如需商业合作，充值或使用过程中如有任何问题可加QQ群：761222621 进行交流,或与售后团队联系,联系方式: 15691820861\n",
            1)
        log_config.output2ui(u"使用步骤如下:", 1)
        log_config.output2ui(u"第一步, 请点击 [登　录] 按钮, 输入您在{}官网注册的账号和密码进行身份和有效期验证!".format(config.SYSTEM_NAME), 1)
        self.txt_ui_log.see(END)

        def update_price(price_text):
            while 1:
                try:
                    time.sleep(0.5)
                    if not self.verify:
                        continue
                    msg = process.REALTIME_PRICE    #.get(block=True)
                    if msg:
                        # print("update_price {}".format(msg))
                        (key, value), = msg.items()
                        global CURRENT_PRICE
                        CURRENT_PRICE = float(value)
                        price_text.set("{}:{}".format(key.upper(), value))

                        self.wait_buy_sell(price=CURRENT_PRICE)
                        self.update_coin(price=value)
                except Exception as e:
                    logger.exception("update_price exception....")
                    log_config.output2ui("update_price exception....", 3)
                    continue

        def update_balance(bal_text):
            while 1:
                try:
                    time.sleep(5)
                    if not self.verify:
                        continue
                    msg = process.REALTIME_BALANCE #.get(block=True)
                    bal_text.set(str(msg))
                except Exception as e:
                    logger.exception("update_ui_balance exception....")
                    log_config.output2ui("update_ui_balance exception....", 3)
                    continue

        def update_ui_log(log_text):
            while 1:
                try:
                    if not log_config.REALTIME_LOG.empty():
                        try:
                            msg_dict = log_config.REALTIME_LOG.get(block=False)
                        except:
                            time.sleep(0.5)
                        if msg_dict:
                            log_text.configure(state='normal')
                            log_text.insert(END, msg_dict["msg"], msg_dict["level"])
                            log_text.see(END)
                    else:
                        time.sleep(1)
                except Exception as e:
                    logger.exception("update_ui_log exception....")
                    log_config.output2ui("update_ui_log exception....", 3)
                    continue

        def update_run_time():
            while 1:
                try:
                    time.sleep(60)
                    if self.working:
                        self.run_time_value += 1
                    hours = int(self.run_time_value/60)
                    minutes = int(self.run_time_value%60)
                    self.run_time.set(u"{}时{}分".format(hours, minutes))
                except Exception as e:
                    logger.exception("update_kdj exception....")
                    log_config.output2ui("update_kdj exception....", 3)

        def update_advise():
            while 1:
                try:
                    time.sleep(15)
                    if not self.verify:
                        continue
                    if process.REALTIME_ADVISE:
                        # self.notify_text.set(u"[操盘建议]:\n"+process.REALTIME_ADVISE[0]+"\n"+process.REALTIME_ADVISE[1])
                        # self.notify_text.
                        msg = u"[操盘建议]:\n" + process.REALTIME_ADVISE[0] + "\n" + process.REALTIME_ADVISE[1] + u"\n程序将为您持续选择最佳交易时机！"
                        self.notify_text.delete(1.0, END)
                        self.notify_text.insert(END, msg, "MSG")
                        # self.notify_text.insert(END, u"[操盘建议]:\n" + process.REALTIME_ADVISE[0] + "\n" + process.REALTIME_ADVISE[1], "MSG")

                        # log_config.output2ui(u"[操盘建议]:", 8)
                        # log_config.output2ui(process.REALTIME_ADVISE[0], 8)
                        # log_config.output2ui(process.REALTIME_ADVISE[1], 8)

                    if process.REALTIME_SYSTEM_NOTIFY:
                        msg = u"------------[管理员通知]----------\n{}".format(process.REALTIME_SYSTEM_NOTIFY)
                        log_config.output2ui(msg, 6)
                        log_config.notify_user(msg, own=True)
                except Exception as e:
                    logger.exception("update_advise exception....")

        def update_heart():
            while 1:

                time.sleep(180)
                if not self.working:
                    continue

                data = {"account": self.account}
                json_data = json.dumps(data)
                headers = {'Content-Type': 'application/json'}
                url = "http://{}:5000/huobi/heart/".format(config.HOST)
                ret = requests.post(url=url, headers=headers, data=json_data)
                result = json.loads(ret.text)
                code = result.get("code", -1)
                if code == 0:
                    log_config.output2ui(u"您的账号信息异常, 无法继续使用, 如有疑问请与客服联系!", 3)
                    self.cmd_stop()
                elif code == 1:
                    data = result.get("data", "")
                    dt = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
                    if dt < datetime.now():
                        log_config.output2ui(u"抱歉! 您的账号已经过期, 无法继续使用本系统! 感谢您对本系统的支持, 如需继续使用请联系客服人员进行续费！", 3)
                        self.cmd_stop()
                    elif dt < datetime.now()+timedelta(hours=24):
                        log_config.output2ui(u"您的账号将在24小时内过期, 为保障您的稳定收益, 请及时联系客服人员续费, 否则系统将在24小内停止工作！", 3)


        def notify_profit_info():
            hour_report_start_time = None
            daily_report_start_time = None
            while 1:
                time.sleep(60)
                if self.working:
                    try:
                        if not self.verify:
                            continue
                        now_time = datetime.now()
                        if not daily_report_start_time:
                            daily_report_start_time = now_time
                        else:
                            run_total_seconds = (now_time-daily_report_start_time).total_seconds()
                            logger.info("system run total seconds={}, trade_notify_interval={}".format(run_total_seconds, config.TRADE_HISTORY_REPORT_INTERVAL))
                            if (run_total_seconds > config.TRADE_HISTORY_REPORT_INTERVAL*3600) or config.SEND_HISTORY_NOW > 0:
                                logger.info("send history now...")
                                if config.SEND_HISTORY_NOW > 0:
                                    # 立即发送，　不影响周期发送逻辑
                                    beg = now_time-timedelta(hours=config.SEND_HISTORY_NOW)
                                    interval = int(config.SEND_HISTORY_NOW)
                                else:
                                    beg = daily_report_start_time
                                    interval = int(config.TRADE_HISTORY_REPORT_INTERVAL)

                                # 只要发送过，就把起始时间重新置成当前时间　
                                config.SEND_HISTORY_NOW = 0
                                daily_report_start_time = now_time
                                recent_trade_logs = [y for x, y in config.TRADE_ALL_LOG.items() if x > beg]
                                if recent_trade_logs:
                                    recent_trade_logs.sort()
                                    daily_msg = u"火币量化交易系统运行中:\n用户昵称:{}\n币种:{}\n最近{}小时共交易{}次, 记录如下:\n".format(config.NICK_NAME, config.NEED_TOBE_SUB_SYMBOL[0].upper(), interval, len(recent_trade_logs))+"\n\n".join(recent_trade_logs)
                                else:
                                    daily_msg = u"火币量化交易系统运行中:\n用户昵称:{}\n币种:{}\n最近{}小时无交易记录！\n".format(config.NICK_NAME, config.NEED_TOBE_SUB_SYMBOL[0].upper(), interval)

                                log_config.output2ui(daily_msg, 8)
                                logger.warning(daily_msg)
                                log_config.notify_user(daily_msg, own=True)
                        if not hour_report_start_time:
                            hour_report_start_time = now_time
                        else:
                            if (now_time-hour_report_start_time).total_seconds() > config.ACCOUNT_REPORT_INTERVAL*3600 or config.SEND_ACCOUNT_NOW:
                                logger.info("send account info now...")
                                hour_report_start_time = now_time
                                config.SEND_ACCOUNT_NOW = 0

                                global CURRENT_PRICE
                                bal0, bal0_f, bal1, bal1_f = strategies.update_balance()
                                total = (bal0+bal0_f)*CURRENT_PRICE+bal1+bal1_f
                                chicang = ((bal0 + bal0_f) * CURRENT_PRICE) / total
                                dapan_profit = round((CURRENT_PRICE - process.ORG_PRICE) * 100 / process.ORG_PRICE, 3)
                                account_profit = round((total - process.ORG_DOLLAR_TOTAL) * 100 / process.ORG_DOLLAR_TOTAL, 3)
                                is_win = u"是" if account_profit >= dapan_profit else u"否"
                                msg_own = u"""火币量化交易系统运行中:\n用户昵称:{}\n币种:{}\n用户风险承受力:{}\n启动时间:{}\n当前时间:{}\n初始价格:{}\n当前价格:{}\n初始持币量:可用{},冻结{},仓位{}%\n当前持币量:可用{},冻结{},仓位{}%\n初始时持金量:可用{},冻结{}\n初始持金量:可用{},冻结{}\n初始账户总价值:${}\n当前账户总价值:${}\n大盘涨跌幅:{}%\n当前账户涨跌幅:{}%\n当前盈利：{}$\n是否跑羸大盘:{}""".format(
                                    config.NICK_NAME, config.NEED_TOBE_SUB_SYMBOL[0].upper(), config.RISK,
                                    process.START_TIME.strftime("%Y/%m/%d, %H:%M:%S"),
                                    now_time.strftime("%Y/%m/%d, %H:%M:%S"), round(process.ORG_PRICE, 6),
                                    round(CURRENT_PRICE, 6),
                                    round(process.ORG_COIN_TRADE, 4), round(process.ORG_COIN_FROZEN, 4),
                                    round(process.ORG_CHICANG * 100, 2), round(bal0, 4), round(bal0_f, 4), round(chicang * 100, 2),
                                    round(process.ORG_DOLLAR_TRADE, 2), round(process.ORG_DOLLAR_FROZEN, 2), round(bal1, 2), round(bal1_f, 2),
                                    round(process.ORG_DOLLAR_TOTAL, 2), round(total, 2), dapan_profit, account_profit, round(total - process.ORG_DOLLAR_TOTAL, 2), is_win)

                                msg_other = u"火币量化交易系统运行中:\n用户昵称:{}\n币种:{}\n用户风险承受力:{}\n启动时间:{}\n当前时间:{}\n初始价格:{}\n当前价格:{}\n初始持币量:可用{},冻结{},仓位{}%\n当前持币量:可用{},冻结{},仓位{}%\n初始持金量:可用{},冻结{}\n当前持金量:可用{},冻结{}\n初始账户总资产:{}$\n当前账户总资产:${}\n大盘涨跌幅:{}%\n当前账户涨跌幅:{}%\n当前盈利：{}$\n是否跑羸大盘:{}"\
                                    .format(config.NICK_NAME, config.NEED_TOBE_SUB_SYMBOL[0].upper(), config.RISK,
                                        process.START_TIME.strftime("%Y/%m/%d, %H:%M:%S"),
                                        now_time.strftime("%Y/%m/%d, %H:%M:%S"),
                                        round(process.ORG_PRICE, 6), round(CURRENT_PRICE, 6),
                                        "***", "***", round(process.ORG_CHICANG * 100, 2), "***", "***", round(chicang * 100, 2),
                                        "***", "***", "***", "***",
                                        "***", "***",
                                        dapan_profit,
                                        account_profit,"***",
                                        is_win)
                                log_config.output2ui(msg_own, level=8)
                                logger.warning(msg_own)
                                ret1 = log_config.notify_user(msg_own, own=True)
                                ret2 = log_config.notify_user(msg_other)
                    except Exception as e:
                        logger.warning("notify_profit_info exception.e={}".format(e))

        def update_ui_trade_info_thread():
            while 1:
                time.sleep(1)
                if self.working and strategies.should_update_ui_tree:
                    self.update_ui_trade_info()
                    self.update_ui_balance()
                    strategies.should_update_ui_tree = False

            # self.tree.after(5000, update_trade_record)


        # th = Thread(target=update_price, args=(self.price_text,))
        # th.setDaemon(True)
        # th.start()
        th = Thread(target=update_ui_log, args=(self.txt_ui_log, ))
        th.setDaemon(True)
        th.start()
        # th = Thread(target=update_ui_balance, args=(self.bal_text,))
        # th.setDaemon(True)
        # th.start()
        #
        th = Thread(target=update_heart)
        th.setDaemon(True)
        th.start()
        #
        th = Thread(target=update_run_time)
        th.setDaemon(True)
        th.start()
        #
        # th = Thread(target=update_advise)
        # th.setDaemon(True)
        # th.start()
        #
        # th = Thread(target=notify_profit_info)
        # th.setDaemon(True)
        # th.start()

        th = Thread(target=update_ui_trade_info_thread)
        th.setDaemon(True)
        th.start()

        return True

    def save_trades(self):
        try:
            if self.account:
                history_file = "{}.pkl".format(config.CURRENT_ACCOUNT)
                # 以追加的方式保存
                with open(history_file, 'ab') as f:
                    pickle.dump(config.TRADE_RECORDS_NOW, f)
                    log_config.output2ui(u"保存历史交易信息成功!")
        except:
            log_config.output2ui(u"保存交易信息失败, 请以管理员身份运行本系统！", 2)

    def load_trades(self):
        log_config.output2ui(u"正在加载历史未完成的交易对...", 0)
        num = 0
        try:
            conn = sqlite3.connect(config.DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            cursor.execute(
                "create table if not exists trade_group(id integer primary key autoincrement, build varchar(20), mode varchar(20), smart_profit integer,"
                "smart_patch integer, patch_mode varchar(20), coin varchar(20), money varchar(20), grid integer, track integer, amount real, cost real,"
                "avg_price real, max_cost real, profit real, profit_percent real, last_profit_percent real, limit_profit real, back_profit real, "
                "buy_counts integer, sell_counts integer, patch_index integer, patch_ref integer, patch_interval real, last_buy_price real, "
                "start_time timestamp, end_time timestamp, last_update timestamp, uri varchar(100), principal real, last_sell_failed timestamp, sell_out integer,"
                "is_sell integer, stop_patch integer, first_cost real, user varchar(128), platform varchar(40))")


            cursor.execute("select * from `trade_group` where is_sell=0 and user=? and platform=?", (config.CURRENT_ACCOUNT, config.CURRENT_PLATFORM))
            res = cursor.fetchall()
            config.TRADE_RECORDS_NOW = []
            if res:
                for r in res:
                    # 一组执行单元，买和卖都在里面
                    group = {
                        "build": r[1],  # 建仓触发模式smart－－智能建仓，　auto－－自动建仓
                        "mode": r[2],  # robust,keep..按何种交易风格执行，　若未设置，则默认使用全局的交易参数，
                        "smart_profit": r[3],  # 是否启用智能止盈
                        "smart_patch": r[4],  # 是否启用智能补仓
                        "patch_mode": r[5],  # 补仓的模式，默认为倍投
                        "coin": r[6],  # EOS等　
                        "money": r[7],  # USDT等　
                        "trades": [],  # 每一次交易记录，
                        "grid": r[8],  # 是否开启网格交易, 小于零代表使用全局配置
                        "track": r[9],  # 是否开启追踪止盈, 小于零代表使用全局配置
                        "amount": r[10],  # 持仓数量（币）
                        "cost": r[11],  # 当前持仓费用（计价货币）
                        "avg_price": r[12],  # 持仓均价
                        "max_cost": r[13],  # 这组交易中最多时持仓花费，用于计算收益比
                        "profit": r[14],  # 这组策略的总收益， 每次卖出后都进行累加
                        "profit_percent": r[15],  # 整体盈利比（整体盈利比，当前总盈利数除以最大花费,　total_profit_amount/max_cost）
                        "last_profit_percent": r[16],  # 尾单盈利比（最后一单的盈利比）
                        "limit_profit": r[17],  # 止盈比例，　可单独设置，如果未设置（-1），则使用当前所选择的交易策略的止盈比例
                        "back_profit": r[18],  # 追踪比例，　可单独设置，如果未设置（-1），则使用当前所选择的交易策略的追踪比例
                        "buy_counts": r[19],  # 已建单数，买入次数
                        "sell_counts": r[20],  # 卖出单数，卖出的次数，其实就是尾单收割次数
                        "patch_index": r[21],  # 当前补单序号，每买入一单后，path_index加上，　每卖出一单后，pathc_index减1
                        "patch_ref": r[22],  # 补仓参考，0--整体均价，１－－参考上一单买入价格，　小于零代表使用全局
                        "patch_interval": r[23],  # 补仓间隔，　小于零代表使用全局
                        "last_buy_price": r[24],  # 最后一次买入价格，补仓时有可能会选择参考上次买入价，如果上一单已经卖出，那么参考上上一单，以此类推
                        "start_time": r[25],  # 建仓时间
                        "end_time": None,  # 如果为none代表还未结束
                        "last_update": r[27],  # 最近一次更新的时间　
                        "uri": r[28],  # 唯一标识，建仓时间加随机数，如20190608123012336
                        "principal": r[29],  # 当前这组交易的预算,未单独设置的话(小于零)，则默认为全局本金预算除以监控的币对数，
                        "last_sell_failed": r[30],  # 上次卖出失败的时间，　用于做卖出暂停
                        "sell_out": r[31],  # 是否设置为平仓
                        "is_sell": r[32],  # 是否已经卖出
                        "stop_patch": r[33],  # 是否停止补仓
                        "first_cost": r[34],  # 第一单买入花费，以后补仓就参考这个
                        "user": r[35],
                        "platform": r[36]
                    }
                    cursor.execute("select * from `trade` where group_uri=? and user=? and platform=?", (r[28], r[35], r[36]))

                    t_res = cursor.fetchall()
                    if t_res:
                        for tr in t_res:
                            trade = {
                                "buy_type": tr[1],  # 买入模式：auto 自动买入(机器策略买入)，man手动买入,
                                "sell_type": tr[2],
                                # 要求的卖出模式，机器买入的一般都为止盈卖出。可选：profit 止盈卖出（默认）， no-不要卖出，针对手动买入的单，smart-使用高抛，kdj等策略卖出
                                "limit_profit": tr[3],  # 大于零代表使用当前的盈利比例，否则使用所属交易组的盈利比例
                                "back_profit": tr[4],  # 追踪回撤系数, 同上
                                "track": tr[5],  # 是否追踪止盈，同上
                                "buy_time": tr[6],
                                "sell_time": tr[7],
                                "coin": tr[8],
                                "money": tr[9],
                                "amount": tr[10],  # 买入或卖出的币量
                                "buy_price": tr[11],  # 实际买入成交的价格
                                "cost": tr[12],  # 实际花费的计价货币量
                                "is_sell": tr[13],  # 是否已经卖出
                                "sell_price": tr[14],  # 实际卖出的价格
                                "profit_percent": tr[15],  # 盈利比，卖出价格相对于买入价格
                                "profit": tr[16],  # 盈利额，只有卖出后才有
                                "failed_times": tr[17],  # 卖出失败次数，连续三次卖出失败则认为该单已经被手动卖出．
                                "uri": tr[18],  # 唯一标识，　时间戳加随机数
                                "group_uri": tr[19],  # 所属的group的uri
                                "user": tr[20],
                                "platform": tr[21]
                            }
                            group["trades"].append(trade)
                    config.TRADE_RECORDS_NOW.append(group)
                    num += 1
        except Exception as e:
            log_config.output2ui(u"加载历史交易数据失败！", 2)

        # try:
        #     num = 0
        #     history_file = "{}.pkl".format(config.CURRENT_ACCOUNT)
        #     finished_trades = []
        #     with open(history_file, 'rb') as f:
        #         while True:
        #             try:
        #                 trades_records = pickle.load(f)
        #                 for trade_group in trades_records:
        #                     if not trade_group.get("end_time", None):
        #                         num += 1
        #                         config.TRADE_RECORDS_NOW.append(trade_group)
        #                     else:
        #                         finished_trades.append(trade_group)
        #             except:
        #                 break
        # except:
        #     log_config.output2ui(u"未发现历史数据！", 2)
        #     return


        if num > 0:
            # # 从历史文件中删除未完成的交易组
            # with open(history_file, 'wb') as f:
            #     pickle.dump(finished_trades, f)

            pair_names = []
            for group in config.TRADE_RECORDS_NOW:
                coin = group.get("coin", "").upper()
                money = group.get("money", "").upper()

                pair_names.append("{}{}".format(coin, money).upper())
                self.history_pairs.append({"coin": group.get("coin", "").upper(), "money": group.get("money", "").upper()})

                # {'USDT': {'trade': 0, 'frozen': 0, 'coins': [{'coin': 'HT', 'trade': 0, 'frozen': 0}], 'principal': 0}
                if money in config.CURRENT_SYMBOLS.keys():
                    config.CURRENT_SYMBOLS[money]["coins"].append({"coin": coin, 'trade': 0, 'frozen': 0})
                else:
                    config.CURRENT_SYMBOLS[money] = {"coins": [{"coin": coin, 'trade': 0, 'frozen': 0}], 'trade': 0, 'frozen': 0, 'principal': 0}

            log_config.output2ui(u"加载历史未完成的交易对成功, 共{}对! 系统将在币种设置中为您自动勾以下待完成的币种, 继续上次退出时未完成的监控工作：　{}".format(num, pair_names), 3)
        else:
            log_config.output2ui(u"未发现历史待完成的交易对!", 0)

    def cmd_trade_result(self):
        def load_history():
            try:
                trade_records = []
                conn = sqlite3.connect("ddu.db", detect_types=sqlite3.PARSE_DECLTYPES)
                cursor = conn.cursor()
                cursor.execute(
                    "select sell_time, coin, money, cost, profit, profit_percent from `trade` where is_sell=1 and id>=0 and user=? and platform=?",
                    (config.CURRENT_ACCOUNT, config.CURRENT_PLATFORM))
                res = cursor.fetchall()
                if res:
                    for r in res:
                        trade_records.append({"sell_time": r[0], "coin": r[1], "money": r[2], "cost": r[3],
                                                   "profit": r[4], "profit_percent": r[5]})
            except Exception as e:
                messagebox.showerror(u"错误", u"加载历史交易数据失败, 无法查看历史收益记录.")
                return None
            return trade_records

        records = load_history()
        if records is None:
            log_config.output2ui(u"加载历史交易数据失败, 无法查看历史收益记录.", 2)
            return

        PopupTradeResults(parent=self.root, trade_records=records)


    def close_window(self):
        # ans = askyesno("Warning", message="Are you sure to quit？")
        ans = askyesno(u"提示", message=u"确认退出？")
        if ans:
            self.logout()
            self.gressbar_init_history.quit()
            self.gressbar_verify_api.quit()
            self.clean_strategy()
            self.stop_check_strategy()
            self.cmd_stop()
            # 把当次运行运程中的所有交易记录保存到文件中
            # self.save_trades()
            self.root.destroy()
        else:
            return

    def api_verify(self, remember=1):
        def verify_user_by_get_balance():
            from rs_util import HuobiREST
            if config.CURRENT_PLATFORM == "huobi":
                hrs = HuobiREST()
                hrs.get_accounts()
                self.gressbar_verify_api.quit()
                if hrs.account_id and hrs.account_state == config.PLATFORMS["huobi"]["account_state_working"]:
                    self.is_api_ok = True
                    self.btn_coin.config(state="normal")
                    self.btn_mode_setting.config(state="normal")
                    self.btn_system_setting.config(state="normal")
                    self.btn_wechat.config(state="normal")
                    self.btn_principal.config(state="normal")
                    # self.btn_login.config(state="disabled")

                    if remember:
                        self.save_api_info_to_db()

                    log_config.output2ui(u"API授权认证成功! ", 1)
                    log_config.output2ui(u"第三步, 请点击 [币种设置] 选择您想要进行交易的币对.", 1)
                else:
                    self.btn_coin.config(state="disabled")
                    self.btn_mode_setting.config(state="disabled")
                    self.btn_system_setting.config(state="disabled")
                    self.btn_start.config(state="disabled")
                    self.btn_pending_setting.config(state="disabled")
                    messagebox.showwarning("错误", u"API授权认证失败!")
                    log_config.output2ui(u"API授权认证失败, 请检查您的网络状况和授权码是否在有效期, 或者您的授权码是否绑定了特定的IP地址!", 3)

            else:
                time.sleep(1)
                self.gressbar_verify_api.quit()
                messagebox.showwarning("错误", u"API授权认证失败!")
                log_config.output2ui(u"API授权认证失败, 请检查您的网络状况和授权码是否在有效期, 或者您的授权码是否绑定了特定的IP地址!", 3)
                self.btn_coin.config(state="disabled")
                self.btn_mode_setting.config(state="disabled")
                self.btn_system_setting.config(state="disabled")
                self.btn_start.config(state="disabled")
                self.btn_pending_setting.config(state="disabled")

        th = Thread(target=verify_user_by_get_balance)
        th.setDaemon(True)
        th.start()
        self.gressbar_verify_api.start(text=u"正在进行平台授权认证, 请稍等...")


    def verify_huobi(self, access_key):
        retry = 3
        status_code = 0
        error_info = ""
        try:
            while retry >= 0:
                ret = get("http://{}:5000/huobi/{}".format(config.HOST, access_key), timeout=3)
                if ret.status_code == 200:
                    self.verify = True
                    logger.info(u"系统授权认证成功！ 过期时间: {}".format(ret.text))
                    return True, u"系统授权认证成功！ 过期时间: {}".format(ret.text)
                else:
                    #201-invalid, 202-does not exist, 203-expired, 204-exception
                    if ret.status_code == 204:
                        retry -= 1
                        status_code = 204
                        error_info = ret.text
                        logger.error("verify_huobi, server exception 204")
                        continue
                    elif ret.status_code == 203:
                        logger.error("verify_huobi expired. status code={}, text={}".format(ret.status_code, ret.text))
                        msg = u"您的系统授权截止: {} 已过期, 无法继续使用本系统, 如需继续授权使用, 请提供您的AccessKey:\n{}\n给系统管理员进行续费！ \n联系方式:15691820861(可加微信)!".format(ret.text, access_key)
                        self.verify = False
                        return False, msg
                    else:
                        logger.error("verify_huobi failed. status code={}, text={}".format(ret.status_code, ret.text))
                        msg = u"系统授权认证失败, 错误码: {}.\n无法继续使用本系统, 请确认您输入的账户信息正确无误! 如需授权使用, 请提供您的AccessKey:\n{}\n给系统管理员以开通使用权限！ \n联系方式:15691820861(可加微信)!".format(ret.status_code, access_key)
                        self.verify = False
                        return False, msg
                time.sleep(1)
        except Exception as e:
            status_code = -1
            error_info = str(e)
            error_info = error_info.replace(host, "47.77.13.207")
            error_info = error_info.replace("5000", "1009")
            logger.error("verify_huobi e={}".format(error_info))
            error_info = u"网络连接超时！"

        self.verify = False
        return False, u"系统授权认证检查失败, 暂时无法使用本系统, 错误码：{},错误信息:{}\n请检查您的网络情况, 稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!".format(status_code, error_info)

    def set_up_account(self):
        self.txt_ui_log.insert(
            END, u"  温馨提示：在身份验证弹出窗口中输入您的密钥后, 您可以点击[保存密钥]保存自己的密钥至本地文件中，以后进行身份验证时只需点击[导入密钥]即可．", "INFO")

        self.txt_ui_log.insert(END, u"\n\n  如果您还没有火币平台账号，请参考[火币平台用户指导书]，简单几步带您完成从注册到交易．\n\n  注册时使用我们的 [邀请注册链接] (邀请码 8jbg4)可免费获得本系统100天的试用时长.\n\n", "INFO")

        # self.log_text.insert(END, u"\n  https://www.huobi.de.com/topic/invited/?invite_code=8jbg4&from=groupmessage", "link")
        # self.log_text.insert(END, "\n   http://github.com/PythonAwesome/HuobiUserGuide/blob/master/README.md", "link")
        #
        # self.log_text.insert(END, "\n   如果您还没有API密钥，请登录火币官方网站，点击个人头像，进入API管理页面进行申请．官网地址: ", "INFO")
        # self.log_text.insert(END, "\n   https://www.huobi.co/zh-cn/", "link")

        self.txt_ui_log.see(END)

        url = ['https://www.huobi.de.com/topic/invited/?invite_code=8jbg4&from=groupmessage',
               'https://www.huobi.co/zh-cn/',
               'https://www.huobi.co/zh-cn/apikey/',
               'http://github.com/PythonAwesome/HuobiUserGuide/blob/master/README.md',
               'https://www.jianshu.com/p/c4c4e3325a28',
               'https://www.jianshu.com/p/de6b120cf8d7'
            ]
        name = [u'邀请注册链接', u'火币全球官方网站(火币APP下载也在这里)', u'火币API Key申请(开通授权和身份验证必需)', u'火币平台用户指导书', u"如何提高被动收入", u"本系统使用手册"]
        m = 0
        for each in name:
            self.txt_ui_log.tag_config(m, foreground='blue', underline=True)
            self.txt_ui_log.tag_bind(m, '<Enter>', self.show_hand_cursor)
            self.txt_ui_log.tag_bind(m, '<Leave>', self.show_arrow_cursor)
            self.txt_ui_log.insert(END, each + '\n\n', m)
            self.txt_ui_log.tag_bind(m, '<Button-1>', self.handlerAdaptor(self.click, url=url[m]))
            m += 1

        self.txt_ui_log.see(END)
        from popup_api import PopupAPI
        pop = PopupAPI(self._user_info, u"身份验证")
        self.root.wait_window(pop)
        if not self._user_info.get("ok", False):
            return

        logger.info("{}".format(self._user_info))
        # log_config.output2ui("{}".format(self._user_info))

        self.price_text.set("")
        self.bal_text.set("")
        self.coin_text.set("")

        access_key = self._user_info.get("access_key", "")
        # log_config.output2ui(u"正在进行权限验证, 请稍等...", 8)
        ret = self.verify_huobi(access_key)
        if ret[0]:
            logger.info(u"认证成功, key={}".format(access_key))
            log_config.output2ui(ret[1], 8)
        else:
            logger.error(u"授权认证失败, key={}".format(access_key))
            log_config.output2ui(ret[1], 5)
            messagebox.showerror("Error", ret[1])  # 提出警告对话窗
            return

        self.api_verify()
        self.init_history_button.config(state="normal")

        # self.top = Toplevel(self.root)
        # label = Label(self.top, text="ACCESS_KEY")
        # label.pack()
        # entry = Entry(self.top)
        # entry.pack()
        #
        # btn = Button(self.top, text="OK")
        # btn.pack()

    def set_up_strategy(self):
        from popup_strategy import PopupStrategy
        import strategies
        pop = PopupStrategy(strategies.move_stop_profit_params,
                            strategies.stop_loss_params,
                            strategies.kdj_buy_params,
                            strategies.kdj_sell_params,
                            strategies.vol_price_fly_params,
                            strategies.boll_strategy_params,
                            u"策略配置")
        self.root.wait_window(pop)
        # print(strategies.kdj_buy_params)

    def set_up_system(self):
        def login_wechat():
            # log_config.output2ui(u"需要扫码登录微信网页版或在你的手机上确认登录！", 8)
            ret = wechat_helper.login_wechat()
            log_config.output2ui(u"登录微信成功, 实时交易信息和账号周期统计信息将通过微信发送给您的[文件传输助手].", 8)


        from popup_system1 import PopupSystem
        value_dict = {"is_email": config.EMAIL_NOTIFY, "is_wechat": config.WECHAT_NOTIFY, "is_alarm": config.ALARM_NOTIFY, "is_alarm_trade": config.ALARM_TRADE_DEFAULT,
                      "trade_min": config.TRADE_MIN_LIMIT_VALUE, "alarm_time": config.ALARM_TIME,
                      "trade_max": config.TRADE_MAX_LIMIT_VALUE, "wait_buy_price": config.WAIT_BUY_PRICE,
                      "wait_buy_account": config.WAIT_BUY_ACCOUNT, "wait_sell_price":config.WAIT_SELL_PRICE, "wait_sell_account":config.WAIT_SELL_ACCOUNT,
                      "risk": config.RISK, "emails": config.EMAILS, "wechats": config.WECHATS, "position_low": config.LIMIT_MIN_POSITION,
                      "force_position_low": config.FORCE_POSITION_MIN, "position_high": config.LIMIT_MAX_POSITION,
                      "force_position_high": config.FORCE_POSITION_MAX,"trade_history_report_interval": config.TRADE_HISTORY_REPORT_INTERVAL,
                      "account_report_interval": config.ACCOUNT_REPORT_INTERVAL, "emails_vip": config.EMAILS_VIP, "wechats_vip": config.WECHATS_VIP,
                      "nick_name": config.NICK_NAME}

        pop = PopupSystem(value_dict, u"系统配置")
        self.root.wait_window(pop)
        if pop.is_ok:
            config.EMAIL_NOTIFY = value_dict["is_email"]
            config.WECHAT_NOTIFY = value_dict["is_wechat"]
            config.ALARM_NOTIFY = value_dict["is_alarm"]
            config.ALARM_TRADE_DEFAULT = value_dict["is_alarm_trade"]
            config.ALARM_TIME = value_dict["alarm_time"]

            config.TRADE_MIN_LIMIT_VALUE = value_dict["trade_min"]
            config.TRADE_MAX_LIMIT_VALUE = value_dict["trade_max"]
            config.WAIT_BUY_PRICE = value_dict["wait_buy_price"]
            config.WAIT_BUY_ACCOUNT = value_dict["wait_buy_account"]
            config.WAIT_SELL_PRICE = value_dict["wait_sell_price"]
            config.WAIT_SELL_ACCOUNT = value_dict["wait_sell_account"]
            config.RISK = value_dict["risk"]

            config.LIMIT_MIN_POSITION = value_dict["position_low"]
            config.FORCE_POSITION_MIN = value_dict["force_position_low"]

            config.LIMIT_MAX_POSITION = value_dict["position_high"]
            config.FORCE_POSITION_MAX = value_dict["force_position_high"]

            config.TRADE_HISTORY_REPORT_INTERVAL = value_dict["trade_history_report_interval"]
            config.ACCOUNT_REPORT_INTERVAL = value_dict["account_report_interval"]
            config.NICK_NAME = value_dict["nick_name"]
            self.nick_name_text.set(config.NICK_NAME)

            emails = value_dict.get("emails", "").strip().split("\n")
            wechats = value_dict.get("wechats", "").strip().split("\n")

            emails_vip = value_dict.get("emails_vip", "").strip().split("\n")
            wechats_vip = value_dict.get("wechats_vip", "").strip().split("\n")

            log_config.output2ui("system config:\n{}！".format(value_dict))
            login_wechat_now = value_dict.get("login_wechat_now", 0)
            config.EMAILS = []
            for email in emails:
                if email and len(email) > 5 and "@" in email:
                    config.EMAILS.append(email)

            config.WECHATS = []
            for wechat in wechats:
                if wechat and len(wechat) > 2:
                    config.WECHATS.append(wechat)

            config.EMAILS_VIP = []
            for email in emails_vip:
                if email and len(email) > 5 and "@" in email:
                    config.EMAILS_VIP.append(email)

            config.WECHATS_VIP = []
            for wechat in wechats_vip:
                if wechat and len(wechat) > 2:
                    config.WECHATS_VIP.append(wechat)

            # if (config.EMAIL_NOTIFY and (config.WECHATS or config.WECHATS_VIP)) or login_wechat_now:
            if login_wechat_now or config.EMAIL_NOTIFY:
                log_config.output2ui(u"稍后可能需要您使用手机微信扫码登录或者需要您在手机上确认登录！否则您可能无法收到实时交易信息. 当然, 您也可以在火币APP中查看历史交易记录!", 8)
                self.first_login = False
                th = Thread(target=login_wechat)
                th.setDaemon(True)
                th.start()

    def reset_profit(self):
        process.ORG_COIN_TOTAL = None
        self.bal_text.set("")
        strategies.update_balance()
        self.profit_text.set("0/0")
        self.origin_text.set("0/0/0/0")


if __name__ == '__main__':
    root = Tk()
    my_gui = MainUI(root)
    config.ROOT = root
    root.protocol('WM_DELETE_WINDOW', my_gui.close_window)
    my_gui.center_window(1500, 750)
    root.maxsize(1700, 950)

    try:
        root.iconbitmap('favicon.ico')
        # from PIL import ImageTk, Image
        # Tk.call('wm', 'iconphoto', Tk._w, ImageTk.PhotoImage(Image.open('favicon.ico')))
    except:
        pass
    # time.sleep(1)
    my_gui.update_ui()
    root.mainloop()
    logger.info("==========over================")
