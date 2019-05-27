#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/7/1
# Function: 

import time
from tkinter import Toplevel, Button,  LEFT, RIGHT, Frame, END
from tkinter.scrolledtext import ScrolledText
import threading
# import win32com.client
# import winsound
RUNING = True

class PopupTrade(Toplevel):
    def __init__(self, message="交易提醒", show_time=60, title="Trade Alarm"):
        Toplevel.__init__(self)
        self.alarm_th = None
        self.is_run = True
        self.message = message
        self.show_time = show_time
        self.is_ok = False
        self.is_cancel = False
        global RUNING
        RUNING = True
        self.setup_ui()
        self.title(title)


    def setup_ui(self):
        row1 = Frame(self)
        row1.pack(fill="x")
        # Label(row1, text=self.message, width=60).pack(side=LEFT)
        self.trade_text = ScrolledText(row1, width=50, height=10)
        self.trade_text.pack(side=LEFT)
        self.trade_text.insert(END, self.message)

        row3 = Frame(self)
        row3.pack(fill="x")
        # Button(row3, text="Reset", command=lambda: self.on_reset(), width=10).pack(side=RIGHT)
        Button(row3, text="Cancel", command=lambda: self.on_cancel(), width=10).pack(side=RIGHT)
        Button(row3, text="OK", command=lambda: self.on_ok(), width=10).pack(side=RIGHT)
        self.alarm()

    def alarm(self):
        def alarm_th(timeout):
            global RUNING
            while timeout>0 and RUNING:
                # winsound.Beep(2015, 1000)
                print("Beep-----------------------")
                time.sleep(1)
                timeout -= 1
            self.destroy()

        self.alarm_th = threading.Thread(target=alarm_th, args=(self.show_time, ))
        self.alarm_th.setDaemon(True)
        self.alarm_th.start()

    def on_ok(self):
        self.is_ok = True
        global RUNING
        RUNING = False
        self.destroy()

    def on_cancel(self):
        self.is_cancel = True
        global RUNING
        RUNING = False
        self.destroy()


if __name__ == '__main__':
    value_dict = {}
    pt = PopupTrade()
    pt.setup_ui()
    time.sleep(100)
