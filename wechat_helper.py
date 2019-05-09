#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2019/5/8
# Function:

import logging
import itchat

logger = logging.getLogger()


def login_wechat():
    # 登录微信 登录比较费时，大概10s
    itchat.auto_login(hotReload=True)


def send_to_wechat(msg, nick_names=None):
    rooms = itchat.get_chatrooms()

    # 如是要room是空代表登录失效
    if not rooms:
        login_wechat()

    if not nick_names:
        res = itchat.send(msg=msg)
    else:
        find_names = []
        for r in rooms:
            if r["NickName"] in nick_names:
                find_names.append(r["UserName"])
                if len(find_names) == len(nick_names):
                    break
        else:
            fs = itchat.get_friends()
            for f in fs:
                if f["NickName"] in nick_names:
                    find_names.append(f["UserName"])
                    if len(find_names) == len(nick_names):
                        break
            else:
                cts = itchat.get_contact()
                for c in cts:
                    if c["NickName"] in nick_names:
                        find_names.append(c["UserName"])
                        if len(find_names) == len(nick_names):
                            break

        if not find_names:
            logger.error(f"find_names is empty!!, input names={nick_names}")
            return False
        else:
            if len(find_names) == len(nick_names):
                logger.info(f"find all input names, find names={find_names}")
            else:
                logger.info(f"find part input names, find names={find_names}, input names={nick_names}")

        for name in find_names:
            res = itchat.send(toUserName=name, msg=msg)
            if res.get("BaseResponse", {}).get("Ret", -1) == 0:
                logger.info(f"send to wechat success,to user={name}, res={res},  msg=\n{msg}")
                return True
            else:
                logger.info(f"send to wechat failed,to user={name}, res={res},  msg=\n{msg}")
                return False


if __name__ == '__main__':
    print(0)

    # login_wechat()
    print(1)
    send_to_wechat("我这边是公司办的，我没跑，好像想不用个人跑．", ["二环小栗旬"])
