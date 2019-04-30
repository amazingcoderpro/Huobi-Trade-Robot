#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/19
# Function:
from threading import Thread
import time
import logging
import log_config
logger = logging.getLogger(__name__)


class StrategyPool:
    def __init__(self):
        self._pool = []
        self._run = False

    def register(self, strategy):
        strategy.last_check_time = int(time.time())
        self._pool.append(strategy)

    def unregister(self, strategy_name):
        for st in self._pool:
            if st.name == strategy_name:
                self._pool.remove(st)
                break

    def clean_all(self):
        self._pool.clear()

    def start_work(self):
        def check_strategy():
            while self._run:
                time.sleep(3)
                try:
                    for st in self._pool:
                        st.run()
                        if st.state == 0:
                            self._pool.remove(st)
                except Exception as e:
                    #捕获异常，防止策略检测线程崩溃
                    logger.exception("run strategy [{}] failed. e = {}".format(st.name, e))
                    log_config.output2ui("run strategy [{}] failed. e = {}".format(st.name, e), 4)

        self._run = True
        check_thread = Thread(target=check_strategy)
        check_thread.setDaemon(True)
        check_thread.start()

    def stop_work(self):
        self._run = False


class Strategy:
    def __init__(self, func, check_period, execute_times=-1, after_execute_sleep=0,
                 state=1, is_after_execute_pause=False, name=""):
        self._check_period = check_period   # 执行周期
        self._func = func          #执行方法
        self._name = name           #策略名称
        self._last_check_time = int(time.time()) #上次被调用检测调用时间
        # self._check_times = check_times  #可被检测的次数，-1--一直会被调用检测，0--不会被调用， 大于0---执行次数
        self._execute_times = execute_times     #可被执行的次数，-1--策略被触发后还一直会被调用，0--触发后不会被调用， 大于0---执行次数
        self._state = state     #0--停止， 1--working, 2--pause
        self._last_execute_time = 0      # 上次被触发的时间
        self._after_execute_sleep = after_execute_sleep # 被触发后休眠时间
        self._is_after_execute_pause = is_after_execute_pause

    @property
    def last_check_time(self):
        return self._last_check_time

    @last_check_time.setter
    def last_check_time(self, check_time):
        self._last_check_time = check_time

    @property
    def check_period(self):
        return self._check_period

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def run(self):
        if not self.should_be_check():
            return False

        if self._execute_times > 0:
            self._execute_times -= 1
        # self._last_check_time = current_time
        logger.info("strategy is called, name={}, _execute_times={}".format(self._name, self._execute_times))
        log_config.output2ui("strategy is called, name={}, _execute_times={}".format(self._name, self._execute_times))
        ret = False
        try:
            ret = self._func()
        except Exception as e:
            logger.exception("check strategy:{} catch exception".format(self._name))
            log_config.output2ui("check strategy:{} catch exception: {}".format(self._name, e), 4)
        else:
            if ret:
                logger.warning("strategy be triggered, name={}".format(self._name))
                log_config.output2ui("strategy be triggered, name={}".format(self._name), 2)
                self._last_execute_time = int(time.time())  #策略被执行了
                if self._is_after_execute_pause:
                    self._state = 2 #pause
            else:
                logger.info("strategy don't be trigger, name={}".format(self._name))
        finally:
            current_time = int(time.time())
            self._last_check_time = current_time

    def should_be_check(self):
        # logger.debug("should_be_check...")
        if self._state != 1:
            # logger.debug("should_be_check return false, state={}".format(self._state))
            return False

        if self._execute_times == 0:
            # logger.debug("should_be_check return false, _execute_times={}".format(self._execute_times))
            return False    #

        current_time = int(time.time())
        if current_time-self._last_check_time < self._check_period:
            # logger.debug("should_be_check return false, _last_check_time={}".format(self._last_check_time))
            return False

        if self._last_execute_time > 0 and current_time-self._last_execute_time < self._after_execute_sleep:
            # logger.debug("should_be_check return false, _last_execute_time={}, _after_execute_sleep={}"
            #             .format(self._last_execute_time, self._after_execute_sleep))
            return False
        logger.info("should_be_check return True")
        return True


def test1():
    print("test1 be called")


def test2():
    print("test2 be called")


def test3():
    print("test3 be called")


if __name__ == '__main__':
    st = Strategy(test1, 5, 1, name="st1")
    st2 = Strategy(test2, 8, 3, name="st2")
    st3 = Strategy(test3, 3, -1, name="st3")
    st_pool = StrategyPool()
    st_pool.register(st)
    st_pool.register(st2)
    st_pool.register(st3)
    st_pool.start_work()
    time.sleep(20)
    st_pool.stop_work()
