#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/30
# Function: 
import os
import requests
from tkinter import Toplevel, Label, Button, Entry, StringVar, LEFT, RIGHT, Checkbutton, Frame, messagebox, OptionMenu, IntVar,Text, END, filedialog
import config

class PopupAccountConfig(Toplevel):
    def __init__(self, value_dict, title="Account Configuration"):
        Toplevel.__init__(self)
        self.value_dict = value_dict
        self.get_key()

        self.ckb_save_val = IntVar()
        self.ckb_save = None

        self.access_key = StringVar()
        self.access_key.set(self.value_dict.get("access_key", ""))

        self.secret_key = StringVar()
        self.secret_key.set(self.value_dict.get("secret_key", ""))

        self.trade_left = StringVar()
        self.trade_left.set(self.value_dict.get("trade_left", "EOS"))

        self.trade_right = StringVar()
        self.trade_right.set(self.value_dict.get("trade_right", "USDT"))

        self.ws_site = StringVar()
        self.ws_site.set(self.value_dict.get("ws_site", "PRO"))

        self.rest_site = StringVar()
        self.rest_site.set(self.value_dict.get("rest_site", "PRO"))

        self.setup_ui()
        self.title(title)


    def setup_ui(self):
        row1 = Frame(self)
        row1.pack(fill="x")
        Label(row1, text="ACCESS　KEY: ", width=15).pack(side=LEFT)
        Entry(row1, textvariable=self.access_key, width=40).pack(side=LEFT)
        Button(row1, text=u"导入密钥", command=lambda: self.on_open_key(), width=10).pack(side=RIGHT)

        row2 = Frame(self)
        row2.pack(fill="x", ipadx=1, ipady=1)
        Label(row2, text="SECRET　KEY: ", width=15).pack(side=LEFT)
        Entry(row2, textvariable=self.secret_key, width=40).pack(side=LEFT)

        # row2 = Frame(self)
        # row2.pack(fill="x", ipadx=1, ipady=1)
        # self.ckb_save = Checkbutton(row2, text='Save', variable=self.ckb_save_val, onvalue=1, offvalue=0).pack()

        Button(row2, text=u"保存密钥", command=lambda: self.on_save_key(), width=10).pack(side=RIGHT)

        row3 = Frame(self)
        row3.pack(fill="x", ipadx=1, ipady=1)
        Label(row3, text=u"选择币种: ", width=10).pack(side=LEFT)
        # lst_trade = ['ethusdt', 'btcusdt', 'eosusdt', 'xrpusdt', 'eoseth', "rsrusdt"]

        lst_trade_left = [x.upper() for x in config.SUPPORT_TRADE_LEFT]
        lst_trade_right = [x.upper() for x in config.SUPPORT_TRADE_RIGHT]

        self.trade_left.set(lst_trade_left[0])
        OptionMenu(row3, self.trade_left, *lst_trade_left).pack(side=LEFT)

        self.trade_right.set(lst_trade_right[0])
        OptionMenu(row3, self.trade_right, *lst_trade_right).pack(side=LEFT)


        # row3 = Frame(self)
        # row3.pack(fill="x", ipadx=1, ipady=1)
        Label(row3, text=u"WS站点: ", width=10).pack(side=LEFT)
        lst_site = ['BR', 'PRO', 'HX']
        OptionMenu(row3, self.ws_site, *lst_site).pack(side=LEFT)

        # row3 = Frame(self)
        # row3.pack(fill="x", ipadx=1, ipady=1)
        Label(row3, text=u"RestAPI站点: ", width=10).pack(side=LEFT)
        OptionMenu(row3, self.rest_site, *lst_site).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x")
        Button(row3, text="Cancel", command=lambda: self.on_cancel(), width=10).pack(side=RIGHT)
        Button(row3, text="OK", command=lambda: self.on_ok(), width=10).pack(side=RIGHT)

    def on_ok(self):
        access_key = self.access_key.get()
        secret_key = self.secret_key.get()
        trade_left = self.trade_left.get().lower()
        trade_right = self.trade_right.get().lower()
        trade = trade_left+trade_right
        ws_site = self.ws_site.get()
        rest_site = self.rest_site.get()

        if not access_key or not secret_key:
            messagebox.showwarning("Warning", "用户密钥不能为空!")  # 提出警告对话窗
            return

        if len(access_key) < 10 or len(secret_key) < 10:
            messagebox.showwarning("Warning", "输入的密钥无效!")  # 提出警告对话窗
            return

        self.value_dict["access_key"] = access_key.strip().replace("\n", "")
        self.value_dict["secret_key"] = secret_key.strip().replace("\n", "")
        self.value_dict["trade"] = trade
        self.value_dict["trade_left"] = trade_left
        self.value_dict["trade_right"] = trade_right
        self.value_dict["ws_site"] = ws_site
        self.value_dict["rest_site"] = rest_site

        self.value_dict["ok"] = True
        self.save_key()
        self.destroy()

    def get_key(self):
        try:
            with open("keys//user.hbk", 'r') as f:
                str_key = f.read()
                self.value_dict["access_key"] = str_key.split("++++")[0].strip().replace("\n", "")
                self.value_dict["secret_key"] = str_key.split("++++")[1].strip().replace("\n", "")
        except Exception as e:
            pass

    def save_key(self):
        try:
            is_save = self.ckb_save_val.get()
            if is_save:
                str_key = "{}++++{}".format(self.value_dict["access_key"], self.value_dict["secret_key"])
                with open("keys//user.hbk", 'w') as f:
                    f.write(str_key)
        except Exception as e:
            pass

    def on_cancel(self):
        self.value_dict["ok"] = False
        self.destroy()

    def on_save_key(self):
        save_path = filedialog.asksaveasfilename(filetypes=[("HBK", ".hbk")])  # 返回文件名
        try:
            str_key = "{}++++{}".format(self.access_key.get(), self.secret_key.get())
            with open(save_path, 'w') as f:
                f.write(str_key)
            print(save_path)
        except Exception as e:
            print(e)
            pass

    def on_open_key(self):
        save_path = filedialog.askopenfilename(filetypes=[("HBK", ".hbk")])  # 返回文件名
        try:
            # print(save_path)
            config.NICK_NAME = os.path.basename(save_path).split(".")[0]
            with open(save_path, 'r') as f:
                str_key = f.read()
                self.access_key.set(str_key.split("++++")[0].strip().replace("\n", ""))
                self.secret_key.set(str_key.split("++++")[1].strip().replace("\n", ""))
        except Exception as e:
            print(e)

if __name__ == '__main__':
    pass