#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/18
# Function: 

from tkinter import *
from tkinter import ttk
import time


class GressBar():
    def __init__(self):
        self.master = None

    def start(self, text=None):
        top = Toplevel()
        self.master = top
        top.overrideredirect(True)
        # top.attributes("-toolwindow", 1)
        top.wm_attributes("-topmost", 1)
        top.title("Huobi Trade")
        # Label(top, text="正在初始化网络和历史数据，请稍等……", fg="green").pack(pady=2)
        # default_text = "Initializing network and historical data, please wait a moment..."
        default_text = u"正在初始化网络和历史数据，请稍等..."
        if text:
            default_text = text
        Label(top, text=default_text, fg="green").pack(pady=2)
        prog = ttk.Progressbar(top, mode='indeterminate', length=220)
        prog.pack(pady=10, padx=35)
        prog.start()

        top.resizable(False, False)
        top.update()
        curWidth = top.winfo_width()
        curHeight = top.winfo_height()
        scnWidth, scnHeight = top.maxsize()
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        top.geometry(tmpcnf)
        top.mainloop()

    def quit(self):
        if self.master:
            self.master.destroy()

if __name__ == '__main__':
    gb = GressBar()
    gb.start()
    time.sleep(10)
    gb.quit()