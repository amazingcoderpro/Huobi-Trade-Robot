#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/30
# Function: 

from tkinter import Toplevel, Label, Button, Entry, StringVar, LEFT, RIGHT, Checkbutton, Frame, messagebox, OptionMenu, IntVar
class PopupConfig(Toplevel):
    def __init__(self, value_dict, title=""):
        Toplevel.__init__(self)
        self.value_dict = value_dict
        self.access_key = StringVar()
        self.ckb_save_val = IntVar()
        self.ckb_save = None
        self.get_key()
        self.access_key.set(self.value_dict.get("access_key", ""))
        self.secret_key = StringVar()
        self.secret_key.set(self.value_dict.get("secret_key", ""))
        self.trade = StringVar()
        self.trade.set(self.value_dict.get("trade", "ethusdt"))
        self.ws_site = StringVar()
        self.ws_site.set(self.value_dict.get("ws_site", "BR"))
        self.rest_site = StringVar()
        self.rest_site.set(self.value_dict.get("rest_site", "BR"))
        self.setup_ui()
        self.title(title)

    def setup_ui(self):
        row1 = Frame(self)
        row1.pack(fill="x")
        Label(row1, text="ACCESS_KEY: ", width=15).pack(side=LEFT)
        Entry(row1, textvariable=self.access_key, width=40).pack(side=LEFT)

        row2 = Frame(self)
        row2.pack(fill="x", ipadx=1, ipady=1)
        Label(row2, text="SECRET_KEY: ", width=15).pack(side=LEFT)
        Entry(row2, textvariable=self.secret_key, width=40).pack(side=LEFT)

        # row2 = Frame(self)
        # row2.pack(fill="x", ipadx=1, ipady=1)
        self.ckb_save = Checkbutton(row2, text='Save', variable=self.ckb_save_val, onvalue=1, offvalue=0).pack()

        row3 = Frame(self)
        row3.pack(fill="x", ipadx=1, ipady=1)
        Label(row3, text="TRADE: ", width=15).pack(side=LEFT)
        lst_trade = ['ethusdt', 'btcusdt', 'eosusdt', 'xrpusdt', 'eoseth']
        # self.trade.set(lst_trade[0])
        OptionMenu(row3, self.trade, *lst_trade).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x", ipadx=1, ipady=1)
        Label(row3, text="WebSocket Site: ", width=15).pack(side=LEFT)
        lst_site = ['BR', 'PRO', 'HX']
        # self.ws_site.set(lst_site[0])
        OptionMenu(row3, self.ws_site, *lst_site).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x", ipadx=1, ipady=1)
        Label(row3, text="RestAPI Site: ", width=15).pack(side=LEFT)
        # self.rest_site.set(lst_site[0])
        OptionMenu(row3, self.rest_site, *lst_site).pack(side=LEFT)

        row3 = Frame(self)
        row3.pack(fill="x")
        Button(row3, text="Cancel", command=lambda: self.on_cancel(), width=10).pack(side=RIGHT)
        Button(row3, text="OK", command=lambda: self.on_ok(), width=10).pack(side=RIGHT)

    def on_ok(self):
        access_key = self.access_key.get()
        secret_key = self.secret_key.get()
        trade = self.trade.get()
        ws_site = self.ws_site.get()
        rest_site = self.rest_site.get()
        if not access_key or not secret_key:
            messagebox.showwarning("Warning", "User's key should not be empty!")  # 提出警告对话窗
            return
        self.value_dict["access_key"] = access_key.strip().replace("\n", "")
        self.value_dict["secret_key"] = secret_key.strip().replace("\n", "")
        self.value_dict["trade"] = trade
        self.value_dict["ws_site"] = ws_site
        self.value_dict["rest_site"] = rest_site
        self.value_dict["ok"] = True
        self.save_key()
        self.destroy()

    def get_key(self):
        try:
            with open("temp.hbk", 'r') as f:
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
                with open("temp.hbk", 'w') as f:
                    f.write(str_key)
        except Exception as e:
            pass

    def on_cancel(self):
        self.value_dict["ok"] = False
        self.destroy()

if __name__ == '__main__':
    pass