#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/7/23
# Function: 


# import win32com.client
# import winsound
# speak = win32com.client.Dispatch('SAPI.SPVOICE')
# winsound.Beep(2015, 3000)
# winsound.MessageBeep(winsound.MB_OK)
# speak.Speak('程序运行完毕!')

# if __name__ == '__main__':
#     pass
# import queue
# aq = queue.Queue(maxsize=2)
# aq.put(1)
# print(11)
# aq.put(2, block=False)
# print(22)
# print(aq.get(block=False))
import json
import requests


def encode_str(source="123456"):
    import hashlib
    sha = hashlib.sha256()
    sha.update(str(source).encode("utf-8"))
    encode_source = sha.hexdigest()
    print(encode_source)
    return encode_source

data = {"account": "17502964994", "password": encode_str("123456")}
json_data = json.dumps(data)
headers = {'Content-Type': 'application/json'}
url = "http://127.0.0.1:5000/huobi/login/"
ret = requests.post(url=url, headers=headers, data=json_data)
print(ret.status_code)

print(json.loads(ret.text))

# if __name__ == '__main__':
#     encode_str()