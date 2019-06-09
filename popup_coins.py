#-*-coding:utf-8-*- 
__author__ = 'Administrator'
import tkinter as tk

root = tk.Tk()

GIRLS = ['西施', '貂蝉', '王昭君', '杨玉环']

v = []

for girl in GIRLS:  # 显示四大美女的显示框
    　　v.append(tk.IntVar())


　　  # variable：把变量放到最后一个 ,
　　b = tk.Checkbutton(root, text=girl, variable=v[-1])
　　b.pack(side=tk.LEFT)

for each in v:  # 显示状态的框
    　　l = tk.Label(root, textvariable=each)
　　l.pack(side=tk.LEFT)

tk.mainloop()
