#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/20
# Function:
'''
Provide a function  for anyone who want to configure log parameters easily,
just call init_log_config before your use the module of logging that build-in python
'''


import os
import logging
import threading
from datetime import datetime
from logging import handlers
import queue
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import config
import wechat_helper
# formatter
FORMATTER = "%(asctime)s [%(threadName)s] [%(filename)s:%(funcName)s:%(lineno)d] " \
            "%(levelname)s %(message)s"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# log file args
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
is_exists = os.path.exists(os.path.join(BASE_DIR, "logs"))
if not is_exists:
    os.makedirs(os.path.join(BASE_DIR, "logs"))
LOG_FILE_PREFIX = "HuobiTrade"
LOG_FILE_NAME = "logs//{}_{}.log".format(LOG_FILE_PREFIX, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))       # your_log_file_name.log
# LOG_FILE_PATH = os.path.join(BASE_DIR, "log", LOG_FILE_NAME)   # your log full path
LOG_FILE_PATH = LOG_FILE_NAME
LOG_FILE_SIZE = 10 * 1024 * 1024                        # the limit of log file size
LOG_BACKUP_COUNT = 10                                    # backup counts

# log mail args, You need to correct the following variables if you want to use email notification function
MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 25
FROM_ADDR = 'wcadaydayup@163.com'
TO_ADDRS = "wcadaydayup@163.com"
SUBJECT = 'Huobi Trade Application Runtime Error'
CREDENTIALS = ('wcadaydayup@163.com', '998zhiyao998')

# log level args
LOG_OUTPUT_LEVEL = logging.DEBUG
LOG_FILE_LEVEL = logging.INFO
LOG_CONSOLE_LEVEL = logging.DEBUG
LOG_MAIL_LEVEL = logging.CRITICAL

REALTIME_LOG = queue.Queue()
UI_LOG_LEVEL_LIST = ["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION", "CRITICAL", "BUY", "SELL", "SHOW"]
UI_LOG_LEVEL = 1

# email notify sell/buy
sender = 'wcadaydayup@163.com'
sender_password = "998zhiyao998"
subject = 'Huobi Trade Notify'
smtpserver = 'smtp.163.com'
from_name = 'Huobi Trade Developer'


def init_log_config(use_mail=False):
    '''
    Do basic configuration for the logging system. support ConsoleHandler, RotatingFileHandler and SMTPHandler
    :param use_mail: Whether to use the email notification function, default False
    :return: None
    '''
    logging.basicConfig(level=LOG_OUTPUT_LEVEL,
                        format=FORMATTER,
                        datefmt=DATE_FORMAT)

    # add rotating file handler
    rf_handler = handlers.RotatingFileHandler(LOG_FILE_PATH, maxBytes=LOG_FILE_SIZE, backupCount=LOG_BACKUP_COUNT)
    rf_handler.setLevel(LOG_FILE_LEVEL)
    formatter = logging.Formatter(FORMATTER)
    rf_handler.setFormatter(formatter)
    logging.getLogger().addHandler(rf_handler)

    # add smtp handler if use_mail is True
    if use_mail:
        mail_handler = handlers.SMTPHandler(
            mailhost=(MAIL_SERVER, MAIL_PORT),
            fromaddr=FROM_ADDR,
            toaddrs=TO_ADDRS.split(";"),
            subject=SUBJECT,
            credentials=CREDENTIALS
        )
        mail_handler.setLevel(LOG_MAIL_LEVEL)
        mail_handler.setFormatter(logging.Formatter(FORMATTER))
        logging.getLogger().addHandler(mail_handler)


def output2ui(msg, level=UI_LOG_LEVEL):
    if level < UI_LOG_LEVEL:
        return
    level = 0 if level < 0 else level
    level = 8 if level > 8 else level

    # 转换成新的时间格式(2018-06-16 18:02:20)
    time_local = time.localtime(int(time.time()))
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

    global REALTIME_LOG
    if level == 8:
        format_msg = "--- {} ---\n".format(msg)
    else:
        format_msg = "[{}]{} {} \n".format(str_time, UI_LOG_LEVEL_LIST[level], msg)
    msg_dict = {"level": UI_LOG_LEVEL_LIST[level], "msg": format_msg}
    REALTIME_LOG.put(msg_dict)

    # if level >= 6:
    #     import smtplib
    #     smtp = smtplib.SMTP("smtp.163.com")
    #     smtp.login("email", "password")
    #     smtp.sendmail("wcadaydayup@163.com", msg)
    #     smtp.close()


class UILogHandler(logging.Handler):
    def __init__(self, log_queue):
        self._queue = log_queue
        logging.Handler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self._queue.put(msg)


def add_handler(handler):
    logging.getLogger().addHandler(handler)


def send_mail(text, own=False):
    def async_send_mail(text, owe=False):
        # 发送微信
        ret = True
        logging.getLogger("start to send wechat. own={}".format(own))
        if own:
            ret = wechat_helper.send_to_wechat(text, config.OWNNER_WECHATS)
        else:
            if config.WECHAT_NOTIFY:
                ret = wechat_helper.send_to_wechat(text, config.WECHATS)
        return ret

        # 发送邮件
        receiver_list = []
        receiver_str = ""
        if own:
            receiver_list = config.OWNER_EMAILS
            receiver_str = ", ".join(receiver_list)
        else:
            if config.EMAIL_NOTIFY and config.EMAILS:
                receiver_list = config.EMAILS
                receiver_str = ", ".join(receiver_list)

        if not receiver_list or not receiver_str:
            logging.getLogger().warning("send email cancelled. receive list is empty! own={}, text={}".format(own, text))
        else:
            logging.getLogger().info("send mail owner={}, to={}, text={}".format(own, receiver_list, text))
            try:
                msg = MIMEText(text, 'plain', 'utf-8')      # 中文需参数‘utf-8'，单字节字符不需要
                msg['Subject'] = Header(subject, 'utf-8')
                msg['From'] = '{}<{}>'.format(from_name, sender)
                msg['To'] = receiver_str

                smtp = smtplib.SMTP_SSL(smtpserver)
                smtp.login(sender, sender_password)
                smtp.sendmail(sender, receiver_list, msg.as_string())
                smtp.close()
            except Exception as e:
                logging.getLogger().exception("send mail failed. e = {}".format(e))

    th = threading.Thread(target=async_send_mail, args=(text, own))
    th.setDaemon(True)
    th.start()


def make_msg(flag, symbol, current_price, percent=0, amount=0, last_price=0, params="***"):
    if percent == 0:
        percent = "***"
    else:
        if percent < 1:
            percent = percent * 100
        percent = round(percent, 2)

    if amount <= 0:
        amount = "***"
    else:
        amount = round(amount, 4)

    if last_price <= 0:
        last_price = "***"
    else:
        last_price = round(last_price, 3)

    current_price = round(current_price, 3)

    if flag == 0:
        flag = u"买入"
        msg = u"[{}{}] {}比例: {}%, {}金额: {}$, 当前价格: {}$. \n买入依据: {}".format(flag, symbol, flag, percent, flag, amount, current_price, params)
    else:
        flag = u"卖出"
        if last_price>0:
            msg = u"[{}{}] {}比例: {}%, {}数量: {}个, 当前价格: {}$. \n卖出依据: {}".format(flag, symbol, flag, percent, flag, amount, current_price, last_price, params)
        else:
            msg = u"[{}{}] {}比例: {}%, {}数量: {}个, 当前价格: {}$, 之前买入价格: {}$. \n卖出依据: {}".format(flag, symbol, flag, percent,
                                                                                          flag, amount, current_price,
                                                                                          last_price, params)

    logging.getLogger().info("make_msg return={}".format(msg))
    return msg


if __name__ == "__main__":
    # send_mail("123", own=True)
    msg = make_msg(1, "eosusdt", 0.4, 4.63, 50)
    wechat_helper.send_to_wechat(msg, ["Justkidding"])
    # wechat.send_to_wechat(msg)