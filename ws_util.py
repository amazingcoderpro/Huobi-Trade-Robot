#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/15
# Function: huobi websocket api访问方法

from websocket import create_connection
# import gzip
from gzip import decompress
import time
import json
from threading import Thread
import config
import logging
import log_config
logger = logging.getLogger(__name__)


"""Huobi websocket api接口工具类"""
class HuobiWS:
    def __init__(self, url, retry=config.RETRY_TIMES, timeout=config.NET_TIMEOUT):
        self._ws = None     #websocket 连接实例
        self._ws_url = url  #指定要连接的站点
        self._sub_map = {}  #用于记录所有的订阅信息{channel:process_func}
        self._req_map = {}  #用于记录一次性请求信息{channel:process_func},收到回复后会删除，主要是用来记录回调处理
        self._run = False   #用于记录是否接收ws推送
        self._retry = retry
        self._timeout = timeout

    #建立websocket连接
    def ws_connect(self):
        ts = -1
        retry = self._retry
        if config.STATUS != "running":
            retry = 5
        while(ts <= retry):
            ws = None
            try:
                ws = create_connection(self._ws_url, timeout=self._timeout)
                # ws = WebSocket()
            except Exception as e:
                logger.exception('connect {} websocket error, e={}, retry={}'.format(self._ws_url, e, ts))
                log_config.output2ui(u"建立服务器连接, 重试中...[{}]".format(ts+2), 0)
                # log_config.output2ui('connect {} websocket error, e={}, retry={}'.format(self._ws_url, e, ts), 4)
                if ws:
                    ws.shutdown()
                time.sleep(2)
                if retry >= 0:
                    ts += 1
                else:
                    pass
            else:
                self._ws = ws
                logger.info("connect web socket succeed.")
                log_config.output2ui(u"建立服务器连接成功.", 0)
                return True

        logger.critical("create connection failed.")
        log_config.output2ui(u"建立服务器连接失败.", 3)
        # raise(Exception("connect web socket server failed."))
        return False

    #用于网络错误时重新连接，resub为true时则会重新订阅所有的channel
    def ws_reconnect(self, resub=True):
        logger.warning("--------------reconnect .... ")
        log_config.output2ui("--------------reconnect .... ", 7)
        if self._ws:
            self._ws.shutdown()
            self._ws = None
            time.sleep(1)

        #如果连接失败，返回False
        if not self.ws_connect():
            return False

        #连接成功，判断是否需要重新订阅之前的channel
        if resub:
            for k, v in self._sub_map.items():
                self.ws_sub(k, v, redo=True)
        return True

    #关闭websocket连接
    def ws_close(self):
        logging.info("close web socket.")
        log_config.output2ui("取消实时行情订阅", 0)
        self._run = False
        if self._ws:
            self._ws.shutdown()
            self._ws = None

        #断开之后，原来的注册不再生效，清空
        self._sub_map.clear()
        self._req_map.clear()

    def __del__(self):
        self.ws_close()

    #订阅频道，callback 为所订阅频道推送数的处理函数，默认为none
    def ws_sub(self, channel, call_back=None, redo=False):
        if channel in self._sub_map.keys() and not redo:
            return True

        if not self._ws:
            logger.warning("please create web socket before sub.")
            log_config.output2ui("please create web socket before sub.", 7)
            return False

        index = len(self._sub_map)
        sub_body = {"sub": channel,
                    "id": "id{}".format(index)}

        str_sub_body = json.dumps(sub_body)
        # print("%r" %str_sub_body)
        ret = self._ws.send(str_sub_body)

        # ret = self._ws.send("""{"sub": "market.btcusdt.kline.5min","id": "id10"}""")
        if ret:
            self._sub_map[channel] = call_back
            # logger.info("SUB: {} have subscribed successfully".format(channel))
            log_config.output2ui("SUB: {} have subscribed successfully".format(channel), 7)
            return True
        else:
            logger.error("SUB: {} failed. ret={}, request body={}".format(channel, ret, str_sub_body))
            # log_config.output2ui("SUB:  {} failed. ret={}, request body={}".format(channel, ret, str_sub_body), 3)
            return False

    #取消某个频道的订阅
    def ws_unsub(self, channel):
        if channel not in self._sub_map.keys():
            logger.warning("channel: {} had not be subscribed".format(channel))
            log_config.output2ui("channel: {} had not be subscribed".format(channel), 7)
            return False

        if not self._ws:
            logger.warning("please create web socket before unsub.")
            log_config.output2ui("please create web socket before unsub.", 7)
            return False


        index = len(self._sub_map)
        unsub_body = {"UNSUB": channel,
                      "id": "id{}".format(index)}
        str_unsub_body = json.dumps(unsub_body)
        ret = self._ws.send(str_unsub_body)
        if ret:
            self._sub_map.pop(channel)
            logger.info("{} have un-subscribed successfully".format(channel))
            log_config.output2ui("{} have un-subscribed successfully".format(channel), 7)
            return True
        else:
            logger.error("UNSUB {} failed. ret={}, request body={}".format(channel, ret, str_unsub_body))
            log_config.output2ui("UNSUB {} failed. ret={}, request body={}".format(channel, ret, str_unsub_body), 7)
            return False

    #发起一次请求
    def ws_req(self, channel, call_back=None, t_from=None, t_to=None):
        if not self._ws:
            logger.warning("please create web socket before req.")
            log_config.output2ui("please create web socket before req.", 7)
            return False
        logger.info("REQ: {}".format(channel))
        log_config.output2ui("REQ: {}".format(channel), 7)
        index = len(self._req_map)
        req_body = {"req": channel,
                    "id": "id{}".format(index)}
        if t_from or t_to:
            req_body["from"] = t_from
            req_body["to"] = t_to

        str_req_body = json.dumps(req_body)
        ret = self._ws.send(str_req_body)
        if ret:
            self._req_map[channel] = call_back
            logger.info("REQ: {} have request successfully".format(channel))
            log_config.output2ui("REQ: {} have request successfully".format(channel), 7)
            return True
        else:
            logger.error("REQ: request {} failed. ret={}, request body={}".format(channel, ret, str_req_body))
            log_config.output2ui("REQ: request {} failed. ret={}, request body={}".format(channel, ret, str_req_body), 7)
            return False

    #开始建立接收线程
    def start_recv(self):
        thread_recv = Thread(target=self.ws_thread_recv)
        self._run = True
        thread_recv.setDaemon(True)
        thread_recv.start()

    #接收线程
    def ws_thread_recv(self,):
        while (self._run):
            compress_data = None
            try:
                compress_data = self._ws.recv()
            except Exception as e:
                logger.exception("receive data error: {}, data:{}".format(e, compress_data))
                # log_config.output2ui("receive data error: {}, data:{}".format(e, compress_data), 4)
                # 如果已经关闭了，则不需要重连
                if self._run:
                    logger.warning("need reconnect..")
                    log_config.output2ui(u"服务器断开, 正在重连...", 2)
                    ret = self.ws_reconnect(resub=True)
                    #如查重连失败，则接收线程退出
                    if not ret:
                        logger.critical("-------reconnect failed. ws_thread_recv exit..")
                        log_config.output2ui(u"平台服务器多次重连失败, 系统无法正常运行, 请检查网络状况！", 3)
                        raise(Exception("平台服务器多次重连失败，请检查网络！"))
                        break
                else:
                    logger.info("don't need reconnect, ws_thread_recv exit..")
                    log_config.output2ui(u"断开平台服务器连接.")
                    return
                time.sleep(1)
                continue

            try:
                result = decompress(compress_data).decode('utf-8')
            except Exception as e:
                logger.exception("depress data error, e={}, data={}".format(e, compress_data))
                # log_config.output2ui("depress data error, e={}, data={}".format(e, compress_data), 4)
                continue

            if "error" in result:
                logger.error("----------ERROR: receive data error. error response: \n {}".format(result))
                # log_config.output2ui("----------ERROR: receive data error. error response: \n {}".format(result), 3)
            # print("++ ws_thread_recv: {}".format(result))
            if "ping" in result:
                #处理ping消息
                pong_body = result.replace("ping", "pong")
                self._ws.send(pong_body)
            elif "subbed" in result:
                pass
                # logger.info("+++SUB SUCCESSFULLY: {}".format(result))
                log_config.output2ui("+++SUB SUCCESSFULLY: {}".format(result), 7)
            else:
                #处理订阅和请求响应
                res = eval(result)
                process = None
                channel = res.get("ch", "")
                if channel != "":
                    #处理订阅消息响应
                    if channel in self._sub_map.keys():
                        process = self._sub_map[channel]
                else:
                    #处理请求消息响应
                    rep = res.get("rep", "")
                    logger.info("REQ: response: {}".format(res))
                    if rep in self._req_map.keys():
                        process = self._req_map[rep]
                        self._req_map.pop(rep)

                 #回调函数调用
                if process:
                    try:
                        process(res)
                    except Exception as e:
                        logger.exception("process {} catch exception.e={}".format(channel, e))
                        # log_config.output2ui("process {} catch exception.e={}".format(channel, e), 4)


def btcusdt_k5_process(response):
    print("btcusdt_k5_process: {}".format(response))


def ethusdt_k5_process(response):
    print("ethusdt_k5_process: {}".format(response))

def ethusdt_k5_req_process(response):
    print("ethusdt_k5_req_process: {}".format(response))

def kline_req_process(response):
    print("kline_req_process: {}".format(response))
    print(len(response["data"]))

if __name__ == '__main__':
    from config import CURRENT_WS_URL, WS_URL_PRO
    import process

    hws = HuobiWS(url=WS_URL_PRO)
    if not hws.ws_connect():
        print("-------connect websocket failed...exit")
        exit(1)

    #测试订阅（重复）
    hws.ws_sub("market.eosusdt.kline.1year", process.kline_sub_msg_process)
    #
    hws.ws_sub("market.eosusdt.kline.1min", process.kline_sub_msg_process)
    # hws.ws_sub("market.ethusdt.kline.5min", kline_msg_process)
    # print(hws._sub_map)
    # hws.ws_req("market.eosusdt.kline.1day", process.kline_req_msg_process, t_from=1508947200, t_to=1527782400)
    # 请求 KLine 数据 market.$symbol.kline.$period 这个接口最多只能返回300条数据 ，亲测！！
    hws.ws_req("market.eosusdt.kline.15min", process.kline_req_msg_process, t_from=1557122524-106000, t_to=1557122524)

    #开始启动接收线程
    hws.start_recv()

    time.sleep(120)
    hws.ws_close()
    for channel, df in process.KLINE_DATA.items():
        print("\n{} data:\n{}".format(channel, df))
        process.plot_candle_chart(df, type=2, pic_name=channel)
    exit(1)

    # #hws.ws_unsub("market.ethusdt.kline.5min")
    # print(hws._sub_map)
    #
    # #hws.ws_unsub("market.btcusdt.kline.5min")
    # print(hws._sub_map)
    # time.sleep(15)
    #
    # hws.ws_req("market.ethusdt.kline.5min", ethusdt_k5_req_process)
    # time.sleep(5)
    #
    # # 订阅 Market Depth 数据
    # hws.ws_sub("market.ethusdt.depth.step5")
    # hws.ws_req("market.ethusdt.depth.step5")
    #
    # # 订阅 Trade Detail 数据
    # hws.ws_sub("market.ethusdt.trade.detail")
    # hws.ws_req("market.ethusdt.trade.detail")
    #
    # time.sleep(15)
    # hws.ws_close()
    #
    # plot_candle_chart(df, "abc.png")

