#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/7/23
# Function: 


import win32com.client
import winsound
speak = win32com.client.Dispatch('SAPI.SPVOICE')
winsound.Beep(2015, 3000)
winsound.MessageBeep(winsound.MB_OK)
speak.Speak('程序运行完毕!')

# if __name__ == '__main__':
#     pass