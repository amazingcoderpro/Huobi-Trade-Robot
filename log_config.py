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
from datetime import datetime
from logging import handlers
import queue
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import config

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
TO_ADDRS = "wcadaydayup@163.com;wuchangandaydayup@163.com"
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
receiver = "wcadaydayup@163.com, 1447385994@qq.com"
rceiver_list = ["wcadaydayup@163.com", "1447385994@qq.com"]
"""
"bbb201@126.com", "2879230281@qq.com", "371606063@qq.com", "790840993@qq.com",
                "383362849@qq.com", "351172940@qq.com", "182089859@qq.com", "278995617@qq.com", "2931429366@qq.com"
"""
receiver_own = "wcadaydayup@163.com"#bbb201@126.com,
rceiver_list_own = ["wcadaydayup@163.com"]#"bbb201@126.com",

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
    if not config.EMAIL_NOTIFY:
        logging.getLogger().warning("email notify is closed")
        return False

    if config.EMAILS:
        receiver_list = config.EMAILS
        receiver = ", ".join(receiver_list)

    logging.getLogger().info("send mail  owner={}, to={}, text={}".format(own, receiver_list, text))
    try:
        msg = MIMEText(text, 'plain', 'utf-8')      # 中文需参数‘utf-8'，单字节字符不需要
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = '{}<{}>'.format(from_name, sender)
        if own:
            msg['To'] = receiver_own
        else:
            msg['To'] = receiver

        smtp = smtplib.SMTP_SSL(smtpserver)
        smtp.login(sender, sender_password)
        if own:
            smtp.sendmail(sender, rceiver_list_own, msg.as_string())
        else:
            smtp.sendmail(sender, rceiver_list, msg.as_string())
        smtp.close()
    except Exception as e:
        logging.getLogger().exception(str(e))
        print("send mail failed. e = {}".format(e))


def make_msg(flag, symbol, percent, current_price, amount=0):
    if percent < 1:
        percent = percent*100

    percent = round(percent, 1)
    amount = round(amount, 2)
    current_price = round(current_price, 3)

    if flag == 0:
        flag = u"买入"
        if amount > 0:
            msg = u"[{}{}] {}比例: {}%, {}金额: {}$, 当前价格: {}$.".format(flag, symbol, flag, percent, flag, amount, current_price)
        else:
            msg = u"[{}{}] {}比例: {}%, 当前价格: {}$.".format(flag, symbol, flag, percent, current_price)

    else:
        flag = u"卖出"
        if amount > 0:
            msg = u"[{}{}] {}比例: {}%, {}数量: {}个, 当前价格: {}$.".format(flag, symbol, flag, percent, flag, amount, current_price)
        else:
            msg = u"[{}{}] {}比例: {}%, 当前价格: {}$.".format(flag, symbol, flag, percent, current_price)

    return msg


if __name__ == "__main__":
    # send_mail("123", own=True)
    msg = make_msg(1, "eosusdt", 0.4, 4.63, 50)
    print(msg)