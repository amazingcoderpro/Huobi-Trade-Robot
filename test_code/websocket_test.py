#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/11
# Function: 
from websocket import sock_opt
import socket

def func():
    import websocket
    ws = websocket.WebSocket()
    ws.connect("wss://api.huobipro.com/ws", sock_opt=((socket.IPPROTO_TCP, socket.TCP_NODELAY),))

if __name__ == '__main__':
    func()
