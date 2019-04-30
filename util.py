#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/17
# Function:
import time
import logging
logger = logging.getLogger(__name__)

class Singleton(type):
    def __init__(cls, name, bases, dic):
        super(Singleton, cls).__init__(name, bases, dic)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


# 将时间戳转成时间字符串，精度precision取值["second", "minute", "hour", "day", "month", "year"]
def timestamp2time(stamp, precision="second"):
    try:
        # 不要毫秒
        stamp_no_ms = stamp
        if stamp > 2000000000:
            stamp_no_ms /= 1000

        str_time = ""
        # 转换成localtime
        time_local = time.localtime(int(stamp_no_ms))
        # 转换成新的时间格式(2018-06-16 17:28:54)
        if precision == "second":
            str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        elif precision == 'minute':
            str_time = time.strftime("%Y-%m-%d %H:%M", time_local)
        elif precision == 'hour':
            str_time = time.strftime("%Y-%m-%d %H", time_local)
        elif precision == 'day':
            str_time = time.strftime("%Y-%m-%d", time_local)
        elif precision == 'month':
            str_time = time.strftime("%Y-%m", time_local)
        elif precision == 'year':
            str_time = time.strftime("%Y", time_local)

        logger.info("{}-->{}".format(stamp, str_time))
        return str_time
    except Exception as e:
        logger.exception("e=".format(e))
        return ""


def time2timestamp(time_str):
    # 转换成时间数组
    timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = int(time.mktime(timeArray))
    logger.info("{}-->{}".format(time_str, timestamp))
    return timestamp


# decorator for recall func when func return is not True
def deco_retry(retry_times=3):
    def _deco_retry(func):
        def wrapper(*args, **kwargs):
            for i in range(retry_times):
                ret = func(*args, **kwargs)
                logger.info("deco_retry call {} retry = {}, ret={}".format(func.__name__, i, ret))
                if isinstance(ret, tuple):
                    if ret[0] == 200 and ret[1]:
                        return ret
                else:
                    if ret:
                        return ret
            return ret
        return wrapper
    return _deco_retry

# 0--返回当前时间戳，1-返回当前时间串
def current_time(type=0):
    # 获取当前时间
    time_now = int(time.time())
    # 转换成localtime
    time_local = time.localtime(time_now)
    # 转换成新的时间格式(2018-06-16 18:02:20)
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    logger.info("current local time: {}, timestamp: {}".format(str_time, time_now))
    if type == 0:
        return time_now
    else:
        return str_time


if __name__ == '__main__':
    timestamp2time(1529164800)
    time2timestamp("2018-06-16 17:48:22")
    current_time()
    import copy
    a = {"a": 1}
    b = copy.deepcopy(a)
    a.clear()
    print(b)
