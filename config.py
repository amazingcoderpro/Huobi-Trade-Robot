#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/16
# Function: basic configure

RUN_MODE = "product"    #product/debug
STATUS = ""#after_login, after_api_verify, after_trade_setting, running, pausing,
SYSTEM_NAME = "DDU智能量化交易系统"
REGISTER_URL = "https://www.huobi.de.com/topic/invited/?invite_code=8jbg4&from=groupmessage"
TITLE = u"DDU量化交易系统v2.0.0 (官方交流QQ群:761222621, 管理员:15691820861)"

KL_1MIN = "1min"
KL_5MIN = "5min"
KL_15MIN = "15min"
KL_30MIN = "30min"
KL_60MIN = "60min"
KL_1DAY = "1day"
KL_1WEEK = "1week"
KL_1MON = "1mon"
KL_1YEAR = "1year"
HOST = "47.75.10.215"
# HOST = "127.0.0.1"

CURRENT_ACCOUNT = ""            # 当前用户账号
CURRENT_PASSWORD = ""
CURRENT_PLATFORM = "huobi"      # 当前平台
ACCESS_KEY = ""
SECRET_KEY = ""
CURRENT_SYMBOLS = {}            # 用户选择的交易对{'USDT': {'trade': 0, 'frozen': 0, 'coins': [{'coin': 'HT', 'trade': 0, 'frozen': 0}], 'principal': 0}, 'BTC': {'trade': 0, 'frozen': 0, 'coins': []}, 'ETH': {'trade': 0, 'frozen': 0, 'coins': []}, 'HT': {'trade': 0, 'frozen': 0, 'coins': []}, 'HUSD': {'trade': 0, 'frozen': 0, 'coins': [{'coin': 'XRP', 'trade': 0, 'frozen': 0}]}}

NEED_TOBE_SUB_SYMBOL = []

# 平台及期配置信息字典
PLATFORMS = {
    "huobi": {
        "display": u"火币",
        "private_key": b"-----BEGIN EC PRIVATE KEY-----\r\nMHQCAQEEIJxC7lk2nTcVUj+Dh3iIelrGIFwt/lPwJYcUsX10fkr9oAcGBSuBBAAK\r\noUQDQgAEJYDjtP9s7i1FU0Gp3xXq0KQptrtxy63bb3TwlTo49GyasdhZYPF1HILk\r\nTskvXRsWal24HAelzpJWnFzXwZnRpw==\r\n-----END EC PRIVATE KEY-----",
        "account_id": 0,
        "ws_url": {"pro": "wss://api.huobipro.com/ws", "hx": "wss://api.hadax.com/ws",
                   "br": "wss://api.huobi.br.com/ws", "default": "wss://api.huobi.br.com/ws"},
        "rest_market_url": {"pro": "https://api.huobi.pro/market", "hx": "https://api.hadax.com/market",
                            "br": "https://api.huobi.br.com/market", "default": "https://api.huobi.br.com/market"},
        "rest_trade_url": {"pro": "https://api.huobi.pro/v1", "hx": "https://api.hadax.com/v1",
                           "br": "https://api.huobi.br.com/v1", "default": "https://api.huobi.br.com/v1"},
        "kline_all": [KL_1MIN, KL_15MIN, KL_5MIN, KL_60MIN, KL_1DAY],
        "kline_history": [KL_1MIN, KL_15MIN, KL_60MIN, KL_1DAY],
        "kline_realtime": KL_1MIN,
        "depth": ["step0", "step1", "step2", "step3", "step4", "step5"],
        "symbol_partition": ["main", "innovation", "bifurcation"],  # main主区，innovation创新区，bifurcation分叉区
        "trade_pairs": {
                "USDT": ["EOS", "BTC", "ETH", "XRP", "LTC", "BCH", "ETC", "HT", "ADA", "IOTA", "OMG", "ZEC", "DASH", "MDS",
                      "XMR", "HB10", "RSR", "TRX", "TOP", "ATOM", "IRIS", "IOST", "TT", "ONT", "HPT", "NEO", "LAMB", "NEW", "ALGO",
                               "BSV", "ITC", "BTT", "BTM", "ATP", "ZIL", "HC", "QTUM", "PAI", "LINK", "NAS", "GXC", "NKN", "IRIS",
                               "ELF", "CMT", "DOGE", "AE", "WICC", "XLM", "LBA", "ELA", "WTC", "CTXC", "DTA", "HIT", "ACT", "THETA",
                               "SOC", "RUFF", "VET", "NULS", "OCN", "KAN", "BTS", "SNT", "BIX", "SMT", "LET", "XEM", "DCR", "STORJ",
                               "CVC", "ZRX", "NANO", "STEEM", "GNT", "WAVES"],
                      "BTC": ["EOS", "ETH", "XRP", "LTC", "BCH", "ETC", "HT", "ADA", "IOTA", "OMG", "ZEC", "DASH", "MDS",
                      "XMR", "HB10", "RSR", "TRX", "TOP", "ATOM", "IRIS", "IOST", "TT", "ONT", "HPT", "NEO", "LAMB", "NEW", "XMX",
                              "UUU", "ALGO", "BOX", "SHE", "ATP", "IIC", "PORTAL", "CNN", "BSV", "LAMB", "GET", "KCASH", "EKT",
                              "ITC", "COVA", "NKN", "TOS", "NEO", "BUT", "YCC", "HPT", "BTT", "MEX", "BKBT", "ZIL", "LINK", "PNT",
                              "FTI", "BTM", "TNT", "PC", "HC", "ABT", "PAI", "CMT", "TNB", "AST", "DOGE", "EGCC", "SSP", "MT",
                              "LXT", "IRIS", "GXC", "ETN", "HOT", "XLM", "QTUM", "BAT", "GTC", "NAS", "MAN", "ELA", "CTXC", "EDU",
                              "UTK", "HIT", "XTZ", "IDT", "ZJLT", "DAC", "LBA", "AE", "SWFTC", "UC", "XZC", "TOPC", "NPXS",
                              "WAX", "MUSK", "EKO", "PAY", "TRIO", "REQ", "VET", "WICC", "UGAS", "STK", "ELF", "GAS", "CHAT",
                              "DGD", "YEE", "WTC", "REN", "SEELE", "LUN", "AAC", "OCN", "DATX", "BCV", "ARDR", "ACT", "ZLA",
                              "DTA", "KAN", "NEXO", "NULS", "DAT", "WAN", "THETA", "DBC", "CVCOIN", "XVG", "MTN", "RCCC", "18C",
                              "AIDOC", "MANA", "GSC", "BLZ", "QASH", "SMT", "RDN", "LOOM", "DGB", "UIP", "DOCK", "SOC", "ZEN",
                              "MXC", "BTS", "SRN", "PROPY", "QUN", "MEET", "SNC", "ICX", "PHX", "WPR", "RUFF", "NCC", "BIX",
                              "ZRX", "KNC", "GNX", "SNT", "APPC", "LYM", "XEM", "DCR", "SC", "WAVES", "POLY", "RCN", "FAIR",
                              "NANO", "STEEM", "NCASH", "LET", "RTE", "KMD", "CVNT", "BFT", "LSK", "EVX", "SALT", "MTX", "OST",
                              "STORJ", "GNT", "CVC", "QSP", "MTL", "ENG", "GRS", "MCO", "POWER", "ADX", "RBTC", "SBTC", "BCD",
                              "BCX", "BIFI", "BTG"],
                      "ETH": ["EOS", "XRP", "LTC", "BCH", "ETC", "HT", "ADA", "IOTA", "OMG", "ZEC", "DASH", "MDS",
                      "XMR", "HB10", "RSR", "TRX", "TOP", "ATOM", "IRIS", "IOST", "TT", "ONT", "HPT", "NEO", "LAMB", "NEW", "XMX",
                              "UUU", "ALGO", "BOX", "SHE", "ATP", "IIC", "PORTAL", "CNN", "BSV", "LAMB", "GET", "KCASH", "EKT",
                              "ITC", "COVA", "NKN", "TOS", "NEO", "BUT", "YCC", "HPT", "BTT", "MEX", "BKBT", "ZIL", "LINK", "PNT",
                              "FTI", "BTM", "TNT", "PC", "HC", "ABT", "PAI", "CMT", "TNB", "AST", "DOGE", "EGCC", "SSP", "MT",
                              "LXT", "IRIS", "GXC", "ETN", "HOT", "XLM", "QTUM", "BAT", "GTC", "NAS", "MAN", "ELA", "CTXC", "EDU",
                              "UTK", "HIT", "XTZ", "IDT", "ZJLT", "DAC", "LBA", "AE", "SWFTC", "UC", "XZC", "TOPC", "NPXS",
                              "WAX", "MUSK", "EKO", "PAY", "TRIO", "REQ", "VET", "WICC", "UGAS", "STK", "ELF", "GAS", "CHAT",
                              "DGD", "YEE", "WTC", "REN", "SEELE", "LUN", "AAC", "OCN", "DATX", "BCV", "ARDR", "ACT", "ZLA",
                              "DTA", "KAN", "NEXO", "NULS", "DAT", "WAN", "THETA", "DBC", "CVCOIN", "XVG", "MTN", "RCCC", "18C",
                              "AIDOC", "MANA", "GSC", "BLZ", "QASH", "SMT", "RDN", "LOOM", "DGB", "UIP", "DOCK", "SOC", "ZEN",
                              "MXC", "BTS", "SRN", "PROPY", "QUN", "MEET", "SNC", "ICX", "PHX", "WPR", "RUFF", "NCC", "BIX",
                              "ZRX", "KNC", "GNX", "SNT", "APPC", "LYM", "XEM", "DCR", "SC", "WAVES", "POLY", "RCN", "FAIR",
                              "NANO", "STEEM", "NCASH", "LET", "RTE", "KMD", "CVNT", "BFT", "LSK", "EVX", "SALT", "MTX", "OST",
                              "STORJ", "GNT", "CVC", "QSP", "MTL", "ENG", "GRS", "MCO", "POWER", "ADX", "RBTC", "SBTC", "BCD",
                              "BCX", "BIFI", "BTG"],
                      "HT": ["EOS", "BTC", "ETH", "XRP", "LTC", "BCH", "ETC", "HT", "ADA", "IOTA", "OMG", "ZEC", "DASH", "MDS",
                      "XMR", "HB10", "RSR", "TRX", "TOP", "ATOM", "IRIS", "IOST", "TT", "ONT", "HPT", "NEO", "LAMB", "NEW", "KCASH",
                             "MT", "NKN", "ATP", ""],
                      "HUSD": ["USDT", "BTC", "ETH", "XRP", "EOS", "HT"]
              },
        "account_state_working": "working",  # 正常
        "account_state_lock": "lock",
    },
    "binance": {
        "display": u"币安",
        "trade_pairs": {"USDT": [], "BTC": [], "ETH": [], "HUSD": []}
    },
    "okex": {
        "display": "OKEx",
        "trade_pairs": {"USDT": [], "BTC": [], "ETH": [], "HUSD": []}
    }
}




# PRIVATE_KEY = open("secp256k1-key.pem", "rb").read()
PRIVATE_KEY = b"-----BEGIN EC PRIVATE KEY-----\r\nMHQCAQEEIJxC7lk2nTcVUj+Dh3iIelrGIFwt/lPwJYcUsX10fkr9oAcGBSuBBAAK\r\noUQDQgAEJYDjtP9s7i1FU0Gp3xXq0KQptrtxy63bb3TwlTo49GyasdhZYPF1HILk\r\nTskvXRsWal24HAelzpJWnFzXwZnRpw==\r\n-----END EC PRIVATE KEY-----"

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
SB_RSRUSDT = "rsrusdt"

SUPPORT_TRADE_LEFT = ["EOS", "BTC", "ETH", "XRP", "LTC", "BCH", "ETC", "HT", "ADA", "IOTA", "OMG", "ZEC", "DASH", "MDS",
                      "XMR", "HB10", "RSR", "TRX", "TOP", "ATOM", "IRIS", "IOST", "TT", "ONT", "HPT", "NEO", "LAMB", "NEW"]
# 以下是需要订阅的数据
SUPPORT_TRADE_RIGHT = ["USDT", "HUSD", "BTC", "ETH", "HT"]
# NEED_TOBE_SUB_SYMBOL = []
# SUB_LEFT = ""
# SUB_RIGHT = ""

# klines

#KL_ALL = [KL_1MIN, KL_5MIN, KL_15MIN, KL_30MIN, KL_60MIN, KL_1DAY, KL_1WEEK, KL_1MON]
KL_ALL = [KL_1MIN, KL_15MIN, KL_5MIN]#KL_60MIN, KL_1DAY#,KL_5MIN,KL_30MIN KL_1DAY
KL_HISTORY = [KL_1MIN, KL_15MIN]#, KL_60MIN, KL_1DAY KL_1DAY KL_5MIN,, KL_30MIN
KL_REALTIME = KL_1MIN

# depth type
# step0, step1, step2, step3, step4, step5（合并深度0-5）；step0时，不合并深度
DEPTH = ["step0", "step1", "step2", "step3", "step4", "step5"]

# symbol partition
# main主区，innovation创新区，bifurcation分叉区
SYMBOL_PARTITION = ["main", "innovation", "bifurcation"]

# 账号状态


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


TRADE_MIN_LIMIT_VALUE = 1  # 单次最小交易額不能低於20美金
TRADE_MAX_LIMIT_VALUE = 2000  # 单次最大交易額不能高於1000美金

WAIT_BUY_PRICE = [0, 0, 0]
WAIT_BUY_ACCOUNT = [0, 0, 0]
WAIT_SELL_PRICE = [0, 0, 0]
WAIT_SELL_ACCOUNT = [0, 0, 0]

ROOT = None
RISK = 1.05  # 取值0.5－－1.5之间，默认是１，越大越激进（买的更低，卖得更高，风险承受能力越强），越小越保守．

#是否邮件通知
EMAIL_NOTIFY = False
WECHAT_NOTIFY = False
ALARM_NOTIFY = False            # 是否弹窗提醒
ALARM_TIME = 20                 # 弹窗提醒时长, 最多不能超过120，否则可能错过交易点
ALARM_TRADE_DEFAULT = True      # 弹窗提醒后, 人工未处理时, 默认是否交易
TRADE_HISTORY_REPORT_INTERVAL = 24  # 历史交易记录播报周期, 小时
ACCOUNT_REPORT_INTERVAL = 2     # 账户情况播报周期, 小时


# 邮件\微信通知对象
# EMAILS = ["wcadaydayup@163.com", "2879230281@qq.com", "371606063@qq.com", "790840993@qq.com", "383362849@qq.com", "351172940@qq.com", "182089859@qq.com", "278995617@qq.com", "2931429366@qq.com"]
EMAILS = []
# WECHATS = [u"信链众创量化1.0版"]
WECHATS=[]
# EMAILS_VIP = ["wcadaydayup@163.com", "1447385994@qq.com", "bbb201@126.com"]
EMAILS_VIP = []
# WECHATS_VIP = [u"长城1211", u"追风少年人"]
WECHATS_VIP = []

TRADE_ALL_LOG = {}
LIMIT_MIN_POSITION = 0.1    #期望最低持仓比
FORCE_POSITION_MIN = 0       #是否强制保持最 少持仓比，如果是，无论何种情况都保持该持仓比例，否则系统将在持仓比低于最小持仓比后降低买入标准以尽快达到持仓比

LIMIT_MAX_POSITION = 0.9      #期望的最高持仓比
FORCE_POSITION_MAX = 0       #是否强制保持最大持仓比，如果是，无论何种情况都保持不超过该持仓比，否则系统将在持仓比高于最大持仓比后降低卖出准以尽快降低持仓比

SEND_HISTORY_NOW = 0
SEND_ACCOUNT_NOW = 0
NICK_NAME = u"用户昵称"

# 交易风格字典
TRADE_MODE_CONFIG_STD = {
    "keep_0": {"display": u"保守-",
               "limit_trades": 6,       # 最大买入次数，超过这个次数，不论何种补仓模式都不再补仓，对于不同的补仓模式，这个值会动态减小，比如平方队列时，最多买入4次
               "limit_profit": 0.05,    # 要求的盈利比例
               "back_profit": 0.02,     # 盈利回撤比例
               "track": 1,              # 是否启动追踪止盈
               "grid": 1,               # 是否启用网格止盈方案
               "smart_first": 1,        # 是否启用智能建仓
               # "multiple_list": [10, 20, 40, 80, 160, 320], #倍投的比例队列，用不到
               "patch_mode": "multiple",    # 补仓的模式，默认为倍投
               "first_trade": 0.06,     # 首单买比占比（占本金预算的比例)
               "patch_interval": 0.10,        # 补仓间隔
               "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
               "expect_profit_m": 0.08,     # 月预估收益
               "risk": 0.84             # 风险系数，主要用于智能买入和卖出时参考
               },
    "keep": {"display": u"保守",
             "limit_trades": 6,
             "limit_profit": 0.05,
             "back_profit": 0.02,
             "track": 1,  # 是否启动追踪止盈
             "grid": 1,  # 是否启用网格止盈方案
             "smart_first": 1,        # 是否启用智能建仓
             "patch_mode": "multiple",    # 补仓的模式，默认为倍投
             # "multiple_list": [10, 20, 40, 80, 160, 320],
             "first_trade": 0.09,
             "patch_interval": 0.10,
             "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
             "expect_profit_m": 0.10,
             "risk": 0.88,
             },
    "keep_1": {"display": u"保守+",
               "limit_trades": 6,
               "limit_profit": 0.05,
               "back_profit": 0.02,
               "smart_first": 1,  # 是否启用智能建仓
               "track": 1,  # 是否启动追踪止盈
               "grid": 1,  # 是否启用网格止盈方案
               "patch_mode": "multiple",    # 补仓的模式，默认为倍投
               # "multiple_list": [10, 20, 40, 80, 160, 320],
               "first_trade": 0.12,
               "patch_interval": 0.1,
               "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
               "expect_profit_m": 0.12,
               "risk": 0.92
               },
    "robust_0": {"display": u"稳健-",
                 "limit_trades": 8,
                 "limit_profit": 0.04,
                 "back_profit": 0.01,
                 "track": 1,  # 是否启动追踪止盈
                 "grid": 1,  # 是否启用网格止盈方案
                 "smart_first": 1,  # 是否启用智能建仓
                 "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                 # "multiple_list": [5, 10, 20, 40, 80, 160, 320, 640],
                 "first_trade": 0.041,
                 "patch_interval": 0.08,
                 "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                 "expect_profit_m": 0.16,
                 "risk": 0.96
                 },
    "robust": {"display": u"稳健",
               "limit_trades": 8,
               "limit_profit": 0.04,
               "back_profit": 0.01,
               "track": 1,  # 是否启动追踪止盈
               "grid": 1,  # 是否启用网格止盈方案
               "smart_first": 1,  # 是否启用智能建仓
               "patch_mode": "multiple",  # 补仓的模式，默认为倍投
               # "multiple_list": [5, 10, 20, 40, 80, 160, 320, 640],
               "first_trade": 0.049,
               "patch_interval": 0.08,
               "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
               "expect_profit_m": 0.18,
               "risk": 1
               },
    "robust_1": {"display": u"稳健+",
                 "limit_trades": 8,
                 "limit_profit": 0.04,
                 "back_profit": 0.01,
                 "track": 1,  # 是否启动追踪止盈
                 "grid": 1,  # 是否启用网格止盈方案
                 "smart_first": 1,  # 是否启用智能建仓
                 "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                 # "multiple_list": [5, 10, 20, 40, 80, 160, 320, 640],
                 "first_trade": 0.057,
                 "patch_interval": 0.08,
                 "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                 "expect_profit_m": 0.20,
                 "risk": 1.04
                 },
    "aggressive_0": {"display": u"激进-",
                     "limit_trades": 10,
                     "limit_profit": 0.03,
                     "back_profit": 0.01,
                     "track": 1,  # 是否启动追踪止盈
                     "grid": 1,  # 是否启用网格止盈方案
                     "smart_first": 1,  # 是否启用智能建仓
                     "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                     # "multiple_list": [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
                     "first_trade": 0.0175,
                     "patch_interval": 0.06,
                     "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                     "expect_profit_m": 0.24,
                     "risk": 1.08
                     },
    "aggressive": {"display": u"激进",
                   "limit_trades": 10,
                   "limit_profit": 0.03,
                   "back_profit": 0.01,
                   "track": 1,  # 是否启动追踪止盈
                   "grid": 1,  # 是否启用网格止盈方案
                   "smart_first": 1,  # 是否启用智能建仓
                   "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                   # "multiple_list": [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
                   "first_trade": 0.0195,
                   "patch_interval": 0.06,
                   "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                   "expect_profit_m": 0.26,
                   "risk": 1.12
                   },
    "aggressive_1": {"display": u"激进+",
                     "limit_trades": 10,
                     "limit_profit": 0.03,
                     "back_profit": 0.01,
                     "track": 1,  # 是否启动追踪止盈
                     "grid": 1,  # 是否启用网格止盈方案
                     "smart_first": 1,  # 是否启用智能建仓
                     "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                     # "multiple_list": [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
                     "first_trade": 0.0215,
                     "patch_interval": 0.06,
                     "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                     "expect_profit_m": 0.28,
                     "risk": 1.16
                     },
}


# 交易风格字典
TRADE_MODE_CONFIG = {
    "keep_0": {"display": u"保守-",
               "limit_trades": 6,       # 最大买入次数，超过这个次数，不论何种补仓模式都不再补仓，对于不同的补仓模式，这个值会动态减小，比如平方队列时，最多买入4次
               "limit_profit": 0.04,    # 要求的盈利比例
               "back_profit": 0.015,     # 盈利回撤比例
               "track": 1,              # 是否启动追踪止盈
               "grid": 1,               # 是否启用网格止盈方案
               "smart_first": 1,        # 是否启用智能建仓
               # "multiple_list": [10, 20, 40, 80, 160, 320], #倍投的比例队列，用不到
               "patch_mode": "multiple",    # 补仓的模式，默认为倍投
               "first_trade": 0.06,     # 首单买比占比（占本金预算的比例)
               "patch_interval": 0.08,        # 补仓间隔
               "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
               "expect_profit_m": 0.085,     # 月预估收益
               "risk": 0.84             # 风险系数，主要用于智能买入和卖出时参考
               },
    "keep": {"display": u"保守",
             "limit_trades": 6,
             "limit_profit": 0.04,
             "back_profit": 0.015,
             "track": 1,  # 是否启动追踪止盈
             "grid": 1,  # 是否启用网格止盈方案
             "smart_first": 1,        # 是否启用智能建仓
             "patch_mode": "multiple",    # 补仓的模式，默认为倍投
             # "multiple_list": [10, 20, 40, 80, 160, 320],
             "first_trade": 0.09,
             "patch_interval": 0.08,
             "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
             "expect_profit_m": 0.10,
             "risk": 0.88,
             },
    "keep_1": {"display": u"保守+",
               "limit_trades": 6,
               "limit_profit": 0.04,
               "back_profit": 0.015,
               "smart_first": 1,  # 是否启用智能建仓
               "track": 1,  # 是否启动追踪止盈
               "grid": 1,  # 是否启用网格止盈方案
               "patch_mode": "multiple",    # 补仓的模式，默认为倍投
               # "multiple_list": [10, 20, 40, 80, 160, 320],
               "first_trade": 0.12,
               "patch_interval": 0.075,
               "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
               "expect_profit_m": 0.12,
               "risk": 0.92
               },
    "robust_0": {"display": u"稳健-",
                 "limit_trades": 8,
                 "limit_profit": 0.03,
                 "back_profit": 0.01,
                 "track": 1,  # 是否启动追踪止盈
                 "grid": 1,  # 是否启用网格止盈方案
                 "smart_first": 1,  # 是否启用智能建仓
                 "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                 # "multiple_list": [5, 10, 20, 40, 80, 160, 320, 640],
                 "first_trade": 0.041,
                 "patch_interval": 0.065,
                 "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                 "expect_profit_m": 0.16,
                 "risk": 0.96
                 },
    "robust": {"display": u"稳健",
               "limit_trades": 8,
               "limit_profit": 0.028,
               "back_profit": 0.01,
               "track": 1,  # 是否启动追踪止盈
               "grid": 1,  # 是否启用网格止盈方案
               "smart_first": 1,  # 是否启用智能建仓
               "patch_mode": "multiple",  # 补仓的模式，默认为倍投
               # "multiple_list": [5, 10, 20, 40, 80, 160, 320, 640],
               "first_trade": 0.049,
               "patch_interval": 0.06,
               "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
               "expect_profit_m": 0.18,
               "risk": 1
               },
    "robust_1": {"display": u"稳健+",
                 "limit_trades": 8,
                 "limit_profit": 0.027,
                 "back_profit": 0.09,
                 "track": 1,  # 是否启动追踪止盈
                 "grid": 1,  # 是否启用网格止盈方案
                 "smart_first": 1,  # 是否启用智能建仓
                 "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                 # "multiple_list": [5, 10, 20, 40, 80, 160, 320, 640],
                 "first_trade": 0.057,
                 "patch_interval": 0.055,
                 "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                 "expect_profit_m": 0.20,
                 "risk": 1.04
                 },
    "aggressive_0": {"display": u"激进-",
                     "limit_trades": 10,
                     "limit_profit": 0.026,
                     "back_profit": 0.007,
                     "track": 1,  # 是否启动追踪止盈
                     "grid": 1,  # 是否启用网格止盈方案
                     "smart_first": 1,  # 是否启用智能建仓
                     "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                     # "multiple_list": [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
                     "first_trade": 0.0175,
                     "patch_interval": 0.045,
                     "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                     "expect_profit_m": 0.24,
                     "risk": 1.08
                     },
    "aggressive": {"display": u"激进",
                   "limit_trades": 10,
                   "limit_profit": 0.026,
                   "back_profit": 0.006,
                   "track": 1,  # 是否启动追踪止盈
                   "grid": 1,  # 是否启用网格止盈方案
                   "smart_first": 1,  # 是否启用智能建仓
                   "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                   # "multiple_list": [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
                   "first_trade": 0.0195,
                   "patch_interval": 0.04,
                   "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                   "expect_profit_m": 0.26,
                   "risk": 1.12
                   },
    "aggressive_1": {"display": u"激进+",
                     "limit_trades": 10,
                     "limit_profit": 0.026,
                     "back_profit": 0.005,
                     "track": 1,  # 是否启动追踪止盈
                     "grid": 1,  # 是否启用网格止盈方案
                     "smart_first": 1,  # 是否启用智能建仓
                     "patch_mode": "multiple",  # 补仓的模式，默认为倍投
                     # "multiple_list": [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
                     "first_trade": 0.0215,
                     "patch_interval": 0.035,
                     "patch_ref": 0,           # 0--参考均价，１-参考上次买入价
                     "expect_profit_m": 0.28,
                     "risk": 1.16
                     },
}

# 补仓的几种队列
PATCH_CONFIG = {
    "multiple": {"list": [1, 2, 4, 8, 16, 32, 64, 128, 256, 512], "display": u"倍投"},
    "square": {"list": [2, 4, 16, 256, 65536], "display": u"平方"},
    "fibonacci": {"list": [1, 1, 2, 3, 5, 8, 13, 21, 34, 55], "display": u"斐波那契"},
    "lucas": {"list": [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199], "display": u"卢卡斯"},
    "flat": {"list": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "display": u"平推"}
}

move_stop_profit_params = {"check": 1, "msf_min": 0.018, "msf_back": 0.21}
stop_loss_params = {"check": 0, "percent": 0.03}
kdj_buy_params = {"check": 1, "k": 23, "d": 21, "buy_percent": 0.22, "up_percent": 0.004, "peroid": "15min"}
kdj_sell_params = {"check": 1, "k": 82, "d": 80, "sell_percent": 0.3, "down_percent": 0.005, "peroid": "15min"}
vol_price_fly_params = {"check": 1, "vol_percent": 1.2, "high_than_last": 2, "price_up_limit": 0.01, "buy_percent": 0.3,
                        "peroid": "5min"}
boll_strategy_params = {"check": 1, "peroid": "15min", "open_diff1_percent": 0.025, "open_diff2_percent": 0.025,
                        "close_diff1_percent": 0.0025, "close_diff2_percent": 0.0025, "open_down_percent": -0.02,
                        "open_up_percent": 0.003, "open_buy_percent": 0.35, "trade_percent": 1.5, "close_up_percent": 0.03,
                        "close_buy_percent": 0.5}

# 策略配置字典
STRATEGIES_CONFIG = {
    "buy": {
            "kdj": {"display": u"KDJ买入指标", "check": 1, "lk": 23, "ld": 21, "mk":45, "md": 43, "up_percent": 0.004, "period": "15min"},
            "boll": {"display": u"BOLL买入指标", "check": 1, "period": "15min", "open_diff1_percent": 0.025, "open_diff2_percent": 0.025,
            "close_diff1_percent": 0.0025, "close_diff2_percent": 0.0025, "open_down_percent": -0.02,
            "open_up_percent": 0.003, "open_buy_percent": 0.35, "trade_percent": 1.5, "close_up_percent": 0.03,
            "close_buy_percent": 0.5},
             "low": {"display": u"阶段低吸", "check": 1, "period": "15min"},
            "fly": {"display": u"量价齐升", "check": 1, "vol_percent": 1.2, "high_than_last": 2, "price_up_limit": 0.01, "buy_percent": 0.3,
            "period": "5min"},
            "right_now": {"display": u"立即买入"}
            },
    "sell": {
            "kdj": {"display": u"KDJ卖出指标", "check": 1, "k": 82, "d": 80, "down_percent": 0.005, "period": "15min"},
            "boll": {"display": u"BOLL卖出指标", "check": 1, "period": "15min", "open_diff1_percent": 0.025, "open_diff2_percent": 0.025,
                "close_diff1_percent": 0.0025, "close_diff2_percent": 0.0025, "open_down_percent": -0.02,
                "open_up_percent": 0.003, "open_buy_percent": 0.35, "trade_percent": 1.5, "close_up_percent": 0.03,
                "close_buy_percent": 0.5},
            "high": {"display": u"阶段高抛", "check": 1, "period": "15min"},
            "move_stop_profit": {"display": u"移动止盈", "check": 1, "profit": 0, "back_profit": 0}
        }
}


PRINCIPAL = 0.0         # 本金
TRADE_MODE = "aggressive"   # 当前选择的交易风格，稳健
TRADE_GRID = 1
INTERVAL_REF = {0: "整体均价", 1: "上单价格"}      # 间隔补单参考，0-参考整体持仓均价，1-参考上一单买入价

# 单次交易信息，这样的一次交易记录，将被包含在一组执行单元中, 除非是手动买入的
TRADE = {
    "buy_type": "auto",         # 买入模式：auto 自动买入(机器策略买入)，man手动买入,
    "sell_type": "profit",      # 要求的卖出模式，机器买入的一般都为止盈卖出。可选：profit 止盈卖出（默认）， no-不要卖出，针对手动买入的单，smart-使用高抛，kdj等策略卖出
    "limit_profit": -1,              # 大于零代表使用当前的盈利比例，否则使用所属交易组的盈利比例
    "back_profit": -1,               # 追踪回撤系数, 同上
    "track": -1,                     # 是否追踪止盈，同上
    "buy_time": None,
    "sell_time": None,
    "coin": "EOS",
    "money": "USDT",
    "amount": 0,              # 买入或卖出的币量
    "buy_price": 0,            # 实际买入成交的价格
    "cost": 0,               # 实际花费的计价货币量
    "is_sell": 1,           # 是否已经卖出
    "sell_price": 0,        # 实际卖出的价格
    "profit_percent": 0,    # 盈利比，卖出价格相对于买入价格
    "profit": 0,            # 盈利额，只有卖出后才有
}


# 一组执行单元，买和卖都在里面
TRADE_GROUP = {
    "build": "smart",           # 建仓触发模式smart－－智能建仓，　auto－－自动建仓
    "mode": "",                  #robust,keep..按何种交易风格执行，　若未设置，则默认使用全局的交易参数，
    "coin": "",             #EOS等　
    "money": "",        #USDT等　
    "trades": [],            # 每一次交易记录，
    "grid": -1,              # 是否开启网格交易, 小于零代表使用全局配置
    "track": -1,             # 是否开启追踪止盈, 小于零代表使用全局配置
    "amount": 0,         # 持仓数量（币）
    "cost": 0,           # 当前持仓费用（计价货币）
    "avg_price": 0,      # 持仓均价
    "max_cost": 0,      # 这组交易中最多时持仓花费，用于计算收益比
    "profit": 0,        # 这组策略的总收益， 每次卖出后都进行累加
    "profit_percent": 0,    # 整体盈利比（整体盈利比，当前总盈利数除以最大花费,　total_profit_amount/max_cost）
    "last_profit_percent": 0,   # 尾单盈利比（最后一单的盈利比）
    "limit_profit": -1,      # 止盈比例，　可单独设置，如果未设置（-1），则使用当前所选择的交易策略的止盈比例
    "back_profit": -1,       # 追踪比例，　可单独设置，如果未设置（-1），则使用当前所选择的交易策略的追踪比例
    "buy_counts": 0,             # 已建单数，买入次数
    "sell_counts": 0,            # 卖出单数，卖出的次数，其实就是尾单收割次数
    "patch_index": 0,           # 当前补单序号，每买入一单后，path_index加上，　每卖出一单后，pathc_index减1
    "patch_ref": -1,             # 补仓参考，0--整体均价，１－－参考上一单买入价格，　小于零代表使用全局
    "patch_interval": -1,     # 补仓间隔，　小于零代表使用全局
    "last_buy_price": 0,    # 最后一次买入价格，补仓时有可能会选择参考上次买入价，如果上一单已经卖出，那么参考上上一单，以此类推
    "start_time": None,     # 建仓时间
    "end_time": None,       # 如果为none代表还未结束
    "last_update": None,
    "uri": "",  # 唯一标识，建仓时间加随机数，如20190608123012336
    "principal": -1, #当前这组交易的预算,未单独设置的话(小于零)，则默认为全局本金预算除以监控的币对数，
}


TRADE_PAIRS = []            # {"coin": "", "money": "", "percent": 1} 当前需要监控的币种，支持一个计价货币下的多个币种同时交易
TRADE_RECORDS_NOW = []      # 机器人当前所有需要监控的交易
TRADE_RECORDS_HISTORY = []  # 机器人所有历史交易记录
MAN_BUY_RECORDS = []    # 人为买入记录

