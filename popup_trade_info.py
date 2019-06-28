#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/30
# Function: 

from tkinter import ttk, Button, LEFT, Frame, ACTIVE
from popup_login import MyDialog



def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


class PopupTradeInfo(MyDialog):
    def __init__(self, parent, trade_group, title=u"交易详情"):
        self.trade_group = trade_group
        self.trades = trade_group.get('trades', [])
        MyDialog.__init__(self, parent, title, modal=True)

    def setup_ui(self):
        frame = Frame(self)
        columns = (
            u"序号", u"交易对", u"状　态", u"持币数量", u"持仓费用", u"买入价格", u"卖出价格", u"盈利额", u"盈利比%", u"买入时间", u"卖出时间")
        self.tree = ttk.Treeview(frame, show="headings", columns=columns, height=11)  # 表格
        for name in columns:
            if name == u"序号":
                self.tree.column(name, width=30, anchor="center")
            if name in [u"状态"]:
                self.tree.column(name, width=50, anchor="center")
            elif name in [u"买入时间", u"卖出时间"]:
                self.tree.column(name, width=100, anchor="center")
            else:
                self.tree.column(name, width=80, anchor="center")
            self.tree.heading(name, text=name, command=lambda _col=name:treeview_sort_column(self.tree, _col, False))

        index = 0
        for trade in self.trades:
            trade_pair = "{}/{}".format(trade["coin"], trade['money'])
            str_status = u"监控中"
            if trade.get("is_sell", 0) == 1:
                str_status = u"已完成"
                if trade.get("sell_type", "") == "failed":
                    str_status = u"失败"

            self.tree.insert("", index, values=(index+1,
            trade_pair,
            str_status,
            round(trade["amount"], 6),
            round(trade["cost"], 6),
            round(trade["buy_price"], 6),
            round(trade.get("sell_price", 0), 6),
            round(trade.get("profit", 0), 6),
            round(trade.get("profit_percent", 0)*100, 3),
            trade["buy_time"].strftime("%m%d %H:%M:%S") if trade.get("buy_time", None) else "",
            trade["sell_time"].strftime("%m%d %H:%M:%S") if trade.get("sell_time", None) else ""))
            index += 1

        self.tree.grid(row=0, column=0)
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
        return True

    # 该方法可处理用户输入的数据
    def process_input(self):
        return True




if __name__ == '__main__':
    pass