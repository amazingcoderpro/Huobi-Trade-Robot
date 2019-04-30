#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/16
# Function: 

import time
def timestamp2time(stamp):
    #不要毫秒
    stamp_no_ms = stamp
    if stamp > 2000000000:
        stamp_no_ms /= 1000

    #转换成localtime
    time_local = time.localtime(int(stamp_no_ms))
    #转换成新的时间格式(2018-06-16 17:28:54)
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    print("{}-->{}".format(stamp, str_time))
    return str_time


def time2timestamp(time_str):
    # 转换成时间数组
    timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = int(time.mktime(timeArray))
    print("{}-->{}".format(time_str, timestamp))
    return timestamp


#0--返回当前时间戳，1-返回当前时间串
def current_time(type=0):
    # 获取当前时间
    time_now = int(time.time())
    # 转换成localtime
    time_local = time.localtime(time_now)
    # 转换成新的时间格式(2018-06-16 18:02:20)
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    print("current local time: {}, timestamp: {}".format(str_time, time_now))
    if type == 0:
        return time_now
    else:
        return str_time

def send_mail():
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header

    sender = 'wcadaydayup@163.com'
    sender_password = "998zhiyao998"
    receiver = "wcadaydayup@163.com;wuchangandaydayup@163.com"
    subject = 'Huobi Trade Runtime Info'
    smtpserver = 'smtp.163.com'
    username = ''
    password = ''

    msg = MIMEText('大家关好窗户', 'plain', 'utf-8')  # 中文需参数‘utf-8'，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = 'Huobi Developer<wcadaydayup@163.com>'
    msg['To'] = receiver

    smtp = smtplib.SMTP(smtpserver)
    ret = smtp.login(sender, sender_password)
    ret = smtp.sendmail(sender, receiver, msg.as_string())
    smtp.close()



if __name__ == '__main__':
    timestamp2time(1530311473725)
    timestamp2time(1530313958828)
    timestamp2time(1530304898056)
    timestamp2time(1530331111377)
    exit(1)
    #k1day
    timestamp2time(1508947200)
    timestamp2time(1529164800)
    #k5min
    timestamp2time(1508990400)
    timestamp2time(1509037500)
    time2timestamp("2017-08-01 00:00:00")
    time2timestamp("2018-06-01 00:00:00")
    current_time()
    send_mail()


