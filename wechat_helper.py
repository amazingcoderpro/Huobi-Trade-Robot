#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2019/5/8
# Function:

import logging
# import itchat
from itchat import get_contact, get_chatrooms, get_friends, send, auto_login, logout
logger = logging.getLogger()


def login_wechat():
    # 登录微信 登录比较费时，大概10s
    return auto_login(hotReload=False)


def logout_wechat():
    try:
        return logout()
    except:
        pass

def send_to_wechat(msg, nick_names=None, own=False):
    msg = str(msg)
    try:
        rooms = get_chatrooms(update=True)
    except:
        login_wechat()
        rooms = get_chatrooms(update=True)

    if (not nick_names) and own:
        try:
            send(msg=msg, toUserName="filehelper")
        except:
            logger.exception("send to filehelper failed.")
            return False
        return True

    retry = 3
    find_names = []
    while (retry>0 and not find_names):
        for r in rooms:
            if r["NickName"] in nick_names:
                find_names.append(r["UserName"])
                if len(find_names) == len(nick_names):
                    break
        else:
            try:
                fs = get_friends(update=True)
                for f in fs:
                    if f["NickName"] in nick_names:
                        find_names.append(f["UserName"])
                        if len(find_names) == len(nick_names):
                            break
                else:
                    cts = get_contact(update=True)
                    for c in cts:
                        if c["NickName"] in nick_names:
                            find_names.append(c["UserName"])
                            if len(find_names) == len(nick_names):
                                break
            except Exception as e:
                logger.error("find names exception, e={}, retry={}".format(e, retry))

        retry -= 1

    if not find_names:
        logger.error(f"find names is empty!!, input names={nick_names}")
        return False
    else:
        if len(find_names) == len(nick_names):
            logger.info(f"find all input names, find names={find_names}, input names={nick_names}")
        else:
            logger.info(f"find part input names, find names={find_names}, input names={nick_names}")

    ret = True
    for name in find_names:
        try:
            res = send(msg=msg, toUserName=name)
            if res.get("BaseResponse", {}).get("Ret", -1) == 0:
                logger.info(f"send to wechat success,to user={name}, res={res}")
            else:
                logger.warning(f"send to wechat failed,to user={name}, res={res}, msg=\n{msg}")
        except Exception as e:
            logger.exception("send wechat exception, e={}, msg=\n{}".format(e, msg))
            ret = False
            continue

    return ret


if __name__ == '__main__':
    print(0)

    login_wechat()

    # send_to_wechat(u"我这边是公司办的，我没跑，好像想不用个人跑．", ["二环小栗旬"])
