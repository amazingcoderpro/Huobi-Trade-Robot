#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/7/2
# Function:

# decorator for recall func when func return is not True
def deco_retry(retry_times=3):
    def _deco_retry(func):
        def wrapper(*args, **kwargs):
            for i in range(retry_times):
                print("call {} retry = {}".format(func.__name__, i))
                ret = func(*args, **kwargs)
                if ret:
                    return ret
            return ret
        return wrapper
    return _deco_retry

@deco_retry()
def func(ok=1):
    if ok == 1:
        return True
    else:
        return False

if __name__ == '__main__':
    print(func(1))