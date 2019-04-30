#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/20
# Function: A simple example for using init_log_config()

from log_config.log_config import init_log_config
import logging
logger = logging.getLogger(__name__)


def produce_log():

    logger.debug("this is a message of debug level.")
    logger.info("this is a message of info level.")
    logger.error("this is a message of error level")


def test():
    try:
        # raise()
        a = 5 / 0
    except Exception as e:
        logger.exception("this is a message of error level\n e={}".format(e))


if __name__ == '__main__':
    init_log_config()
    produce_log()
    test()
