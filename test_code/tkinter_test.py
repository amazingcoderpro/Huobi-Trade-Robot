#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/18
# Function:
g_t = 0

from tkinter import Tk, Label, Button, Checkbutton, IntVar
import queue
import time
import threading
from greesbar import GressBar
class MyFirstGUI:
    def __init__(self, root):
        self.notify_queue = queue.Queue()
        self.gress_bar = GressBar()
        self.root = root
        root.title("A simple GUI")
        self.ckb_macd_val = IntVar()
        self.ckb_macd = Checkbutton(root, text='MACD', variable=self.ckb_macd_val, onvalue=1, offvalue=0, command=self.call_ckb_macd).pack()

        self.label = Label(root, text="This is our first GUI!")
        self.label.pack()

        self.greet_button = Button(root, text="Greet", command=self.execute_asyn)
        self.greet_button.pack()

        self.close_button = Button(root, text="Close", command=root.quit)
        self.close_button.pack()

    def greet(self):
        print("Greetings!")

    def call_ckb_macd(self):
        print("check macd val=%d" % self.ckb_macd_val.get())

    def center_window(self, width, height):
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
        self.root.geometry(size)


    def process_msg(self):
        # 每1000毫秒触发自己，形成递归，相当于死循环
        self.root.after(1000, self.process_msg)
        print("process msg")
        while not self.notify_queue.empty():
            try:
                msg = self.notify_queue.get()
                print(msg)
                if msg[0] == 1:
                    print("gressbar quit")
                    self.gress_bar.quit()
            except queue.Empty:
                pass

    def execute_asyn(self):
        #定义一个scan函数，放入线程中去执行耗时扫描
        def scan(_queue):
            # 这里代理所有阻塞的耗时操作。
            while 1:
                time.sleep(1)
                global g_t
                g_t += 1
                print("scan--do something ---")
                if g_t > 10:
                    break
                else:
                    _queue.put((0,))

            _queue.put((1,))

        th = threading.Thread(target=scan, args=(self.notify_queue,))
        th.setDaemon(False)
        th.start()
        #启动进度条
        self.gress_bar.start()

if __name__ == '__main__':
    root = Tk()
    my_gui = MyFirstGUI(root)
    my_gui.center_window(300, 240)
    # root.maxsize(600, 400)
    root.minsize(300, 240)
    #root.iconbitmap('spider_128px_1169260_easyicon.net.ico')
    my_gui.process_msg()
    #my_gui.execute_asyn()
    root.mainloop()