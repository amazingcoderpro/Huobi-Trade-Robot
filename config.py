#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/16
# Function: basic configure

# APIKEY
ACCESS_KEY = ""
SECRET_KEY = ""
PRIVATE_KEY = open("secp256k1-key.pem", "rb").read()
ACCOUNT_ID = 0


# websocket 服务地址
WS_URL_PRO = "wss://api.huobipro.com/ws"
WS_URL_HX = "wss://api.hadax.com/ws"
WS_URL_BR = "wss://api.huobi.br.com/ws"

WS_URLS = {"BR": WS_URL_BR, "HX": WS_URL_HX, "PRO": WS_URL_PRO}
CURRENT_WS_URL = WS_URLS["BR"]

# REST API 请求地址
REST_MARKET_URL_PRO = "https://api.huobi.pro/market"
REST_TRADE_URL_PRO = "https://api.huobi.pro/v1"

# 子站点
REST_MARKET_URL_HX = "https://api.hadax.com/market"
REST_TRADE_URL_HX = "https://api.hadax.com/v1"

# 国内测试站点，不支持交易
REST_MARKET_URL_BR = "https://api.huobi.br.com/market"
REST_TRADE_URL_BR = "https://api.huobi.br.com/v1"

REST_URLS = {"BR": [REST_MARKET_URL_BR, REST_TRADE_URL_BR],
             "HX": [REST_MARKET_URL_HX, REST_TRADE_URL_HX],
             "PRO": [REST_MARKET_URL_PRO, REST_TRADE_URL_PRO]}

CURRENT_REST_MARKET_URL = REST_URLS["BR"][0]
CURRENT_REST_TRADE_URL = REST_URLS["BR"][1]

# symbols
# BTC、XRP，ETH，EOS  兑 USDT,    EOS兑ETH
SB_BTCUSDT = "btcusdt"
SB_ETHUSDT = "ethusdt"
SB_XRPUSDT = "xrpusdt"
SB_EOSUSDT = "eosusdt"
SB_EOSETH = "eoseth"

# 以下是需要订阅的数据
NEED_TOBE_SUB_SYMBOL = []

# klines
KL_1MIN = "1min"
KL_5MIN = "5min"
KL_15MIN = "15min"
KL_30MIN = "30min"
KL_60MIN = "60min"
KL_1DAY = "1day"
KL_1WEEK = "1week"
KL_1MON = "1mon"
KL_1YEAR = "1year"
#KL_ALL = [KL_1MIN, KL_5MIN, KL_15MIN, KL_30MIN, KL_60MIN, KL_1DAY, KL_1WEEK, KL_1MON]
KL_ALL = [KL_1MIN, KL_15MIN, KL_5MIN]#,KL_5MIN,KL_30MIN KL_1DAY
KL_HISTORY = [KL_1MIN, KL_15MIN]#, KL_1DAY KL_5MIN,, KL_30MIN
KL_REALTIME = KL_1MIN

# depth type
# step0, step1, step2, step3, step4, step5（合并深度0-5）；step0时，不合并深度
DEPTH = ["step0", "step1", "step2", "step3", "step4", "step5"]

# symbol partition
# main主区，innovation创新区，bifurcation分叉区
SYMBOL_PARTITION = ["main", "innovation", "bifurcation"]

# 账号状态
ACCOUNT_STATE_WORKING = "working"  # 正常
ACCOUNT_STATE_LOCK = "lock"  # 锁定

# 订单类型
BUY_MARKET = "buy-market"  # 市价买
SELL_MARKET = "sell-market"  # 市价卖
BUY_LIMIT = "buy-limit"  # 限价买
SELL_LIMIT = "sell-limit"  # 限价卖
BUY_IOC = "buy-ioc"  # IOC买单
SELL_IOC = "sell-ioc"  # IOC卖单
SUBMIT_CANCEL = "submit-cancel"  # 已提交撤单申请

# 订单状态
SUBMITTING = "submitting"  # 正在提交
SUBMITTED = "submitted"       # 已提交
PARTIAL_FILLED = "partial-filled"  # 部分成交,
PARTIAL_CANCELED = "partial-canceled"  # 部分撤销
FILLED = "filled"       # 完全成交
CANCELED = "canceled"  # 已撤销

# 返回结果状态
STATUS_OK = "ok"
STATUS_ERROR = "error"

# 数据库配置
DB_SAVE = False
DB_HOST = "127.0.0.1"
DB_PORT = 27017
DB_NAME = "Huobi"
DB_USER = ""
DB_PASSWORD = ""

#
NET_TIMEOUT = 45
RETRY_TIMES = -1  # 小于0无限重试


TRADE_MIN_LIMIT_VALUE = 20  # 单次最小交易額不能低於20美金
TRADE_MAX_LIMIT_VALUE = 2000  # 单次最大交易額不能高於1000美金

WAIT_BUY_PRICE = [0, 0, 0]
WAIT_BUY_ACCOUNT = [0, 0, 0]
WAIT_SELL_PRICE = [0, 0, 0]
WAIT_SELL_ACCOUNT = [0, 0, 0]

ROOT = None
RISK = 1.0  # 取值0.5－－1.5之间，默认是１，越大越激进（买的更低，卖得更高，风险承受能力越强），越小越保守．

#是否邮件通知
EMAIL_NOTIFY = False
WECHAT_NOTIFY = True
ALARM_NOTIFY = False            # 是否弹窗提醒
ALARM_TIME = 30                 # 弹窗提醒时长, 最多不能超过120，否则可能错过交易点
ALARM_TRADE_DEFAULT = True      # 弹窗提醒后, 人工未处理时, 默认是否交易
TRADE_HISTORY_REPORT_INTERVAL = 24  # 历史交易记录播报周期, 小时
ACCOUNT_REPORT_INTERVAL = 2     # 账户情况播报周期, 小时


# 邮件\微信通知对象
# EMAILS = ["wcadaydayup@163.com", "2879230281@qq.com", "371606063@qq.com", "790840993@qq.com", "383362849@qq.com", "351172940@qq.com", "182089859@qq.com", "278995617@qq.com", "2931429366@qq.com"]
EMAILS = []
WECHATS = [u"信链众创量化1.0版"]
EMAILS_VIP = ["wcadaydayup@163.com", "1447385994@qq.com", "bbb201@126.com"]
WECHATS_VIP = [u"长城1211", u"追风少年人"]

TRADE_ALL_LOG = {}
LIMIT_MIN_POSITION = 0.2    #期望最低持仓比
FORCE_POSITION_MIN = 0       #是否强制保持最 少持仓比，如果是，无论何种情况都保持该持仓比例，否则系统将在持仓比低于最小持仓比后降低买入标准以尽快达到持仓比

LIMIT_MAX_POSITION = 0.8      #期望的最高持仓比
FORCE_POSITION_MAX = 0       #是否强制保持最大持仓比，如果是，无论何种情况都保持不超过该持仓比，否则系统将在持仓比高于最大持仓比后降低卖出准以尽快降低持仓比

SEND_HISTORY_NOW = 0
SEND_ACCOUNT_NOW = 0
NICK_NAME = ""