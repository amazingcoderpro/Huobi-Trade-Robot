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
from threading import Thread
from datetime import datetime
from logging import handlers
import queue
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
LOG_FILE_NAME = "{}_{}.log".format(LOG_FILE_PREFIX, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))       # your_log_file_name.log
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
UI_LOG_LEVEL_LIST = ["INFO", "SHOW", "WARNING", "ERROR", "BUY", "SELL", "LINK", "DEBUG"]
UI_LOG_LEVEL = 0

# email notify sell/buy
sender = 'wcadaydayup@163.com'
sender_password = "998zhiyao998"
subject = 'Huobi Trade Notify'
smtpserver = 'smtp.163.com'
from_name = u'火币量化交易系统'


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
    if config.RUN_MODE == "product":
        return

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
    # 对于debug信息，非debug版本不展示
    if level == 7 and config.RUN_MODE != "debug":
        return

    level = 0 if level < 0 else level
    level = 0 if level > 6 else level

    # 转换成新的时间格式(2018-06-16 18:02:20)
    time_now = datetime.now()
    str_time = time_now.strftime("%Y%m%d %H:%M:%S")

    global REALTIME_LOG
    if level != 1:
        format_msg = "[{}] {}\n".format(str_time, msg)
    else:
        format_msg = msg + "\n"

    msg_dict = {"level": UI_LOG_LEVEL_LIST[level], "msg": format_msg}
    REALTIME_LOG.put(msg_dict)

    # 将所有交易信息保存下来
    if level in [4, 5]:
        config.TRADE_ALL_LOG[time_now] = format_msg


class UILogHandler(logging.Handler):
    def __init__(self, log_queue):
        self._queue = log_queue
        logging.Handler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self._queue.put(msg)


def add_handler(handler):
    logging.getLogger().addHandler(handler)


def notify_user(msg, own=False):
    def send_wechat(msg, own=False):
        # 发送微信
        try:
            if not config.WECHAT_NOTIFY:
                logging.getLogger().info("send wechat have been disabled.")

            time_str = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            msg = u"[{}]\n用户: {}\n{}".format(time_str, config.CURRENT_ACCOUNT, msg)
            logging.getLogger().info("start to send wechat. own={}, msg={}".format(own,msg))
            if own:
                ret = wechat_helper.send_to_wechat(msg, config.WECHATS_VIP, own=True)
            else:
                ret = wechat_helper.send_to_wechat(msg, config.WECHATS)
        except Exception as e:
            logging.getLogger().exception("send wechat e={}".format(e))
            ret = False

        return ret

    def send_mail(msg, own=False):
        # 发送邮件
        if not config.EMAIL_NOTIFY:
            logging.getLogger().info("send mail have been disabled. msg={}".format(msg))
            return True

        if own:
            receiver_list = config.EMAILS_VIP
            receiver_str = ", ".join(receiver_list)
        else:
            receiver_list = config.EMAILS
            receiver_str = ", ".join(receiver_list)

        if not all([receiver_str, receiver_list]):
            logging.getLogger().warning("send email have been cancelled. receive list is empty! own={}, text={}".format(own, msg))
            return True

        ret = True
        time_str = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        msg = "[{}] {}".format(time_str, msg)

        logging.getLogger().info("send mail owner={}, to={}, text={}".format(own, receiver_list, msg))
        try:
            email = MIMEText(msg, 'plain', 'utf-8')      # 中文需参数‘utf-8'，单字节字符不需要
            if own:
                new_subject = subject+"[VIP]"
            else:
                new_subject = subject
            email['Subject'] = Header(new_subject, 'utf-8')
            email['From'] = '{}<{}>'.format(from_name, sender)
            email['To'] = receiver_str

            smtp = smtplib.SMTP_SSL(smtpserver)
            smtp.login(sender, sender_password)
            smtp.sendmail(sender, receiver_list, email.as_string())
            smtp.close()
        except Exception as e:
            logging.getLogger().exception("send mail failed. e = {}".format(e))
            ret = False

        return ret

    th = Thread(target=send_wechat, args=(msg, own))
    th.setDaemon(True)
    th.start()

    return send_mail(msg, own)


def make_msg(flag, symbol, current_price, percent=0, amount=0, last_price=0, params="***"):
    msg = "unknown"
    try:
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

        if last_price > 0:
            last_price = round(last_price, 5)

        current_price = round(current_price, 5)

        if flag == 0:
            flag = u"买入"
            msg = u"[{}{}] {}比例: {}%, {}金额: {}$, 当前价格: {}$. \n买入依据: {}".format(flag, symbol, flag, percent, flag, amount, current_price, params)
        else:
            flag = u"卖出"
            if last_price:
                msg = u"[{}{}] {}比例: {}%, {}数量: {}个, 当前价格: {}$, 之前买入价格: {}$. \n卖出依据: {}".format(flag, symbol, flag, percent,
                                                                                              flag, amount, current_price,
                                                                                              last_price, params)
            else:
                msg = u"[{}{}] {}比例: {}%, {}数量: {}个, 当前价格: {}$. \n卖出依据: {}".format(flag, symbol, flag, percent, flag,
                                                                                   amount, current_price, last_price,
                                                                                   params)

    except Exception as e:
        logging.getLogger().info("make_msg e={}".format(e))

    logging.getLogger().info("make_msg return={}".format(msg))
    return msg


if __name__ == "__main__":
    # notify_user("123", own=True)
    msg = make_msg(1, "eosusdt", 0.4, 4.63, 50)
    wechat_helper.send_to_wechat(msg, ["Justkidding"])
    # wechat.send_to_wechat(msg)