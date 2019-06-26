#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/30
# Function: 
import os
from tkinter import Label, Button, Entry, StringVar, LEFT, RIGHT, Checkbutton, Frame, \
    messagebox, OptionMenu, IntVar, filedialog, N, S, E, W, ACTIVE
import config
from popup_login import MyDialog


class PopupAPI(MyDialog):
    def __init__(self, parent, title=u"API设置"):
        MyDialog.__init__(self, parent, title, modal=True)

    def setup_ui(self):
        self.platform = StringVar()
        frame = Frame(self)
        Label(frame, text=u"选择平台: ", width=15).grid(row=0, column=0)
        lst_platforms = [value["display"] for key, value in config.PLATFORMS.items()]
        self.platform.set(config.PLATFORMS.get(config.CURRENT_PLATFORM, {}).get("display", u"火币"))
        self.opt_platform = OptionMenu(frame, self.platform, *lst_platforms)
        self.opt_platform.grid(row=0, column=1, sticky=N+S+W)

        self.access_key = StringVar()
        self.access_key.set(config.ACCESS_KEY)

        self.secret_key = StringVar()
        self.secret_key.set(config.SECRET_KEY)

        Label(frame, text="Access Key: ", width=15).grid(row=1, column=0)
        self.ety_access = Entry(frame, textvariable=self.access_key, width=40)
        self.ety_access.grid(row=1, column=1)
        self.btn_import = Button(frame, text=u"导入密钥对", command=lambda: self.on_open_key(), width=10)
        self.btn_import.grid(row=1, column=2)

        Label(frame, text="Secret Key: ", width=15).grid(row=2, column=0)
        self.ety_secret = Entry(frame, textvariable=self.secret_key, width=40)
        self.ety_secret.grid(row=2, column=1)
        self.btn_save = Button(frame, text=u"保存密钥对", command=lambda: self.on_save_key(), width=10)
        self.btn_save.grid(row=2, column=2)

        self.remember = IntVar()
        self.remember.set(1)
        Checkbutton(frame, text=u'记住API', variable=self.remember, onvalue=1, offvalue=0, width=6).grid(row=3, column=0)

        self.load_histor = IntVar()
        self.load_histor.set(1)
        Checkbutton(frame, text=u'加载历史交易记录', variable=self.load_histor, onvalue=1, offvalue=0, width=15).grid(row=3, column=1)


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
        access_key = self.access_key.get()
        secret_key = self.secret_key.get()
        if not access_key or not secret_key:
            messagebox.showwarning(u"提示", u"用户密钥不能为空!")  # 提出警告对话窗
            return False

        if len(access_key) < 10 or len(secret_key) < 10:
            messagebox.showwarning(u"提示", u"输入的密钥无效!")  # 提出警告对话窗
            return False

        return True

    # 该方法可处理用户输入的数据
    def process_input(self):
        access_key = self.access_key.get()
        secret_key = self.secret_key.get()

        self.result["access_key"] = access_key.strip().replace("\n", "")
        self.result["secret_key"] = secret_key.strip().replace("\n", "")
        self.result["platform_display"] = self.platform.get()
        for plt, cfg in config.PLATFORMS.items():
            if cfg["display"] == self.result["platform_display"]:
                self.result["platform"] = plt
        self.result["remember"] = self.remember.get()
        self.result["load_history"] = self.load_histor.get()

    def on_save_key(self):
        access_key = self.access_key.get()
        secret_key = self.secret_key.get()
        if len(access_key) < 10 or len(secret_key) < 10:
            messagebox.showwarning(u"提示", u"请输入合法的key后再保存！")
            return

        save_path = filedialog.asksaveasfilename(filetypes=[("HBK", ".hbk")])  # 返回文件名
        if not save_path.endswith(".hbk"):
            save_path += ".hbk"
        try:
            str_key = "{}++++{}".format(self.access_key.get(), self.secret_key.get())
            with open(save_path, 'w') as f:
                f.write(str_key)
        except Exception as e:
            print(e)
            pass

    def on_open_key(self):
        save_path = filedialog.askopenfilename(filetypes=[("HBK", ".hbk")])  # 返回文件名
        if not save_path:
            return
        try:
            config.NICK_NAME = os.path.basename(save_path).split(".")[0]
            with open(save_path, 'r') as f:
                str_key = f.read()
                self.access_key.set(str_key.split("++++")[0].strip().replace("\n", ""))
                self.secret_key.set(str_key.split("++++")[1].strip().replace("\n", ""))
        except Exception as e:
            messagebox.showwarning(u"提示", u"导入的密钥文件格式错误！")
            return


if __name__ == '__main__':
    pass