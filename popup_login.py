#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2019/6/11
# Function:

from tkinter import Toplevel, Label, Button, Entry, StringVar, LEFT, Checkbutton, Frame, messagebox, IntVar, ACTIVE
import config
import webbrowser


# 自定义对话框类，继承Toplevel
class MyDialog(Toplevel):
    # 定义构造方法
    def __init__(self, parent, title=None, modal=True, delta_x=400, delta_y=200):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        # 设置标题
        if title: 
            self.title(title)
        self.parent = parent
        # 用于返回结果
        self.result = {"is_ok": False}
        
        # 调用init_widgets方法来初始化对话框界面
        self.initial_focus = self.setup_ui()

        # 根据modal选项设置是否为模式对话框
        if modal: 
            self.grab_set()
        
        if not self.initial_focus:
            self.initial_focus = self
        
        # 为"WM_DELETE_WINDOW"协议使用self.on_ok事件处理方法
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # 根据父窗口来设置对话框的位置
        self.geometry("+%d+%d" % (parent.winfo_rootx()+delta_x, parent.winfo_rooty()+delta_y))

        # 让对话框获取焦点
        self.initial_focus.focus_set()
        self.wait_window(self)
        
    # 通过该方法来创建自定义对话框的内容，继承类重写
    def setup_ui(self):
        # 创建对话框的主体内容
        frame = Frame(self)
        # 创建并添加Label
        Label(frame, text='用户名', font=12, width=10).grid(row=1, column=0)
        # 创建并添加Entry,用于接受用户输入的用户名
        self.name_entry = Entry(frame, font=16)
        self.name_entry.grid(row=1, column=1)
        # 创建并添加Label
        Label(frame, text='密  码', font=12, width=10).grid(row=2, column=0)
        # 创建并添加Entry,用于接受用户输入的密码
        self.pass_entry = Entry(frame, font=16)
        self.pass_entry.grid(row=2, column=1)
        frame.pack(padx=5, pady=5)


        f = Frame(self)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(f, text="确定", width=10, command=self.on_ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(f, text="取消", width=10, command=self.on_cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_ok)
        f.pack()
        

    # 该方法可对用户输入的数据进行校验
    def validate(self):
        # 可重写该方法
        return True
    
    # 该方法可处理用户输入的数据
    def process_input(self):
        pass
        # user_name = self.name_entry.get()
        # user_pass = self.pass_entry.get()
        # messagebox.showinfo(message='用户输入的用户名: %s, 密码: %s'% (user_name , user_pass))
        
    def on_ok(self, event=None):
        # 如果不能通过校验，让用户重新输入
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.result["is_ok"] = True
        self.withdraw()
        self.update_idletasks()
        # 获取用户输入数据
        self.process_input()
        # 将焦点返回给父窗口
        self.parent.focus_set()
        # 销毁自己
        self.destroy()
        
    def on_cancel(self, event=None):
        # 将焦点返回给父窗口
        self.result["is_ok"] = False
        self.parent.focus_set()
        # 销毁自己
        self.destroy()


class PopupLogin(MyDialog):
    def __init__(self, parent,  title="登录", modal=True):
        MyDialog.__init__(self,  parent, title=title, modal=modal)

    def setup_ui(self):
        frame = Frame(self)
        Label(frame, text=u'账号:', width=10).grid(row=1, column=0)
        # 创建并添加Entry,用于接受用户输入的用户名
        self.account_str = StringVar()
        self.account_str.set(config.CURRENT_ACCOUNT)
        self.account = Entry(frame, textvariable=self.account_str, width=20)
        self.account.grid(row=1, column=1)

        # 创建并添加Label
        Label(frame, text=u'密码:', width=10).grid(row=2, column=0)
        # 创建并添加Entry,用于接受用户输入的密码
        self.password_str = StringVar()
        self.password_str.set(config.CURRENT_PASSWORD)

        self.password = Entry(frame, textvariable=self.password_str, width=20)
        self.password.grid(row=2, column=1)
        self.password["show"] = "*"

        self.remember = IntVar()
        self.remember.set(1)
        Checkbutton(frame, text=u'记住密码', variable=self.remember, onvalue=1, offvalue=0, width=6).grid(row=2, column=2)

        register = Label(frame, text=u'没有账号？点这里去注册', width=20, fg="brown", justify="left", wraplength=480)
        register.grid(row=3, column=1)
        register.bind("<ButtonPress-1>", self.on_register)
        frame.pack(padx=5, pady=5)

        f = Frame(self)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(f, text="确定", width=10, command=self.on_ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        # 创建"确定"按钮,位置绑定self.on_ok处理方法
        w = Button(f, text="取消", width=10, command=self.on_cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_ok)
        f.pack()

    def on_register(self, event):
        webbrowser.open(config.REGISTER_URL)

    def validate(self):
        account = self.account_str.get()
        password = self.password_str.get()
        if not account or not password:
            messagebox.showwarning(u"提示", u"账号、密码不能为空!")  # 提出警告对话窗
            return False

        if len(account) < 6 or len(password) < 6:
            messagebox.showwarning(u"提示", u"输入的账号或密码无效!")  # 提出警告对话窗
            return False
        return True

    def process_input(self):
        account = self.account_str.get()
        password = self.password_str.get()
        self.result["account"] = account
        self.result["password"] = password
        self.result["remember"] = self.remember.get()

    def get_account(self):
        try:
            with open("user.hbk", 'r') as f:
                str_key = f.read()
                self.value_dict["access_key"] = str_key.split("++++")[0].strip().replace("\n", "")
                self.value_dict["secret_key"] = str_key.split("++++")[1].strip().replace("\n", "")
        except Exception as e:
            pass

if __name__ == '__main__':
    pass