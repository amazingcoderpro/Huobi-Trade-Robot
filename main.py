#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/18
# Function:

from tkinter import Frame, Tk, Label, Button, Checkbutton, IntVar, StringVar, Text, END, Toplevel, Entry, messagebox
from tkinter.scrolledtext import ScrolledText
import queue
import logging
import threading
from greesbar import GressBar
from huobi import Huobi
import process
from strategy_pool import StrategyPool
import strategies
from tkinter.messagebox import askyesno
import log_config
import huobi
import config
logger = logging.getLogger(__name__)
CURRENT_PRICE = 1


class MainUI():
    def __init__(self, root):
        self.notify_queue = queue.Queue()
        self.gress_bar_init_history = GressBar()
        self.gress_bar_verify_user = GressBar()
        self.root = root
        self.top = None
        self._is_user_valid = False
        self._user_info = {}
        self._strategy_dict = {}
        root.title("Huobi Trade")
        log_config.init_log_config(use_mail=False)

        self._hb = None
        self._strategy_pool = StrategyPool()
        # self.ckb_macd_val = IntVar()
        # self.ckb_macd = Checkbutton(root, text='MACD', variable=self.ckb_macd_val, onvalue=1, offvalue=0, command=self.call_ckb_macd).pack()

        # self.label = Label(root, text="This is our first GUI!")
        # self.label.pack()
        #
        # self.init_history_button = Button(root, text="Init History", command=self.init_history, width=20)
        #
        self.start_button = Button(root, text="Start Work", command=self.start_work, width=20)
        # self.start_button.pack()

        self.stop_button = Button(root, text="Stop Work", command=self.stop_work, width=20)
        # self.stop_button.pack()

        self.register_button = Button(root, text="Register Strategy", command=self.register_strategy, width=20)
        # self.register_button.pack()

        self.start_check_strategy_button = Button(root, text="Start Check Strategy", command=self.start_check_strategy, width=20)
        # self.start_check_strategy_button.pack()

        self.stop_check_strategy_button = Button(root, text="Stop Check Strategy", command=self.stop_check_strategy, width=20)
        # self.stop_check_strategy_button.pack()

        self.clean_st_button = Button(root, text="Clean Strategy", command=self.clean_strategy, width=20)
        # self.clean_st_button.pack()
        self.verify_identity_button = Button(root, text="Verify Identity", command=self.set_up_config, width=20)

        self.init_history_button = Button(root, text="Init History", command=self.init_history_asyn, width=20)

        self.strategy_setting_button = Button(root, text="Strategy Config", command=self.set_up_strategy, width=20)
        self.system_setting_button = Button(root, text="System Config", command=self.set_up_system, width=20)


        self.label_pop = Label(root, text="POP: ", width=5)

        self.price_text = StringVar()
        self.price_text.set("")
        self.price_label = Label(root, textvariable=self.price_text, foreground='red', background="gray",
                                 font=("", 14, 'bold'), width=22)
        # self.price_label.pack()

        self.label_bal = Label(root, text="Balance: ", width=7)
        self.bal_text = StringVar()
        self.bal_text.set("")
        self.bal_label = Label(root, textvariable=self.bal_text, foreground='red', background="gray",
                               font=("", 14, 'bold'), width=40)

        self.label_coin = Label(root, text="Total: ", width=5)
        self.coin_text = StringVar()
        self.coin_text.set("")
        self.coin_label = Label(root, textvariable=self.coin_text, foreground='red', background="gray",
                                font=("", 14, 'bold'), width=22)

        self.label_profit = Label(root, text="Profit: ", width=7)
        self.profit_text = StringVar()
        self.profit_text.set("")
        self.profit_label = Label(root, textvariable=self.profit_text, foreground='red', background="gray",
                                  font=("", 14, 'bold'), width=30)
        self.clean_profit_button = Button(root, text="Clean", command=self.clean_profit, width=10)

        # row6 = Frame(root)
        # row6.pack(fill="x", ipadx=1, ipady=1)

        self.label_kdj = Label(root, text="KDJ_15M: ", width=8)
        self.kdj_text = StringVar()
        self.kdj_text.set("")
        self.kdj_label = Label(root, textvariable=self.kdj_text, foreground='red', background="gray",
                               font=("", 12, 'bold'), width=20)

        self.label_uml = Label(root, text="BOLL: ", width=6)
        self.uml_text = StringVar()
        self.uml_text.set("")
        self.uml_label = Label(root, textvariable=self.uml_text, foreground='red', background="gray",
                               font=("", 12, 'bold'), width=50)

        # self.label_worth = Label(root, text="Worth: ", width=5)
        # self.worth_text = StringVar()
        # self.worth_text.set("Worth")
        # self.worth_label = Label(root, textvariable=self.worth_text, foreground='blue', background="gray",
        #                          font=("", 14, 'bold'), width=12)

        self.label_run_log = Label(root, text="run log: ", width=10)
        self.log_text = ScrolledText(root, width=60, height=26)
        self.label_trade_log = Label(root, text="trade log: ", width=10)
        self.trade_text = ScrolledText(root, width=60, height=26)
        # self.log_text.pack()
        # 创建一个TAG，其前景色为红色
        self.log_text.tag_config('BUY', foreground='green', background="orange", font=("", 11, 'bold'))
        self.log_text.tag_config('SELL', foreground='red', background="orange", font=("", 11, 'bold'))
        self.log_text.tag_config('WARNING', foreground='orange')
        self.log_text.tag_config('ERROR', foreground='red')
        self.log_text.tag_config('EXCEPTION', foreground='red')
        self.log_text.tag_config('CRITICAL', background="red")
        self.log_text.tag_config('SHOW', foreground='green', font=("", 11, 'bold'))
        self.log_text.see(END)

        self.trade_text.tag_config('BUY', foreground='green', background="orange", font=("", 11, 'bold'))
        self.trade_text.tag_config('SELL', foreground='red', background="orange", font=("", 11, 'bold'))
        self.log_text.see(END)

        self.verify_identity_button.grid(row=0, column=0)
        self.init_history_button.grid(row=1, column=0)
        self.start_button.grid(row=2, column=0)
        self.strategy_setting_button.grid(row=3, column=0)
        self.system_setting_button.grid(row=4, column=0)

        self.register_button.grid(row=5, column=0)
        self.start_check_strategy_button.grid(row=6, column=0)
        self.clean_st_button.grid(row=7, column=0)
        self.stop_check_strategy_button.grid(row=8, column=0)
        self.stop_button.grid(row=9, column=0)


        self.label_pop.grid(row=0, column=1)
        self.price_label.grid(row=0, column=2)

        self.label_bal.grid(row=0, column=3)
        self.bal_label.grid(row=0, column=4, columnspan=2)

        self.label_coin.grid(row=1, column=1)
        self.coin_label.grid(row=1, column=2)
        # self.label_worth.grid(row=0, column=7)
        # self.worth_label.grid(row=0, column=8)

        self.label_profit.grid(row=1, column=3)
        self.profit_label.grid(row=1, column=4)
        self.clean_profit_button.grid(row=1, column=5)

        # k d 指标位置
        # row6.grid(row=2, column=1)
        self.label_kdj.grid(row=2, column=1)
        self.kdj_label.grid(row=2, column=2)
        self.label_uml.grid(row=2, column=3)
        self.uml_label.grid(row=2, column=4, columnspan=2)

        self.label_run_log.grid(row=3, column=1)
        self.log_text.grid(row=4, column=1, rowspan=5, columnspan=3)
        self.label_trade_log.grid(row=3, column=4)
        self.trade_text.grid(row=4, column=4, rowspan=5, columnspan=3)

        self.start_button.config(state="disabled")
        self.register_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        self.clean_st_button.config(state="disabled")
        self.stop_check_strategy_button.config(state="disabled")
        self.start_check_strategy_button.config(state="disabled")
        self.init_history_button.config(state="disabled")

        self.working = False

    def init_history_asyn(self):
        def init_history(hb):
            ret = self._hb.init()  # 这一步是必须的，先同步处理
            ret2 = hb.init_history()
            self.gress_bar_init_history.quit()
            if not (ret and ret2):
                logger.error("init service failed.")
                log_config.output2ui("init service failed.", 3)
                messagebox.showwarning("Error", "init history data failed.")
                return False
            log_config.output2ui("Init history data successfully!", 8)
            self.start_button.config(state="normal")
            self.register_button.config(state="normal")
            self.init_history_button.config(state="disabled")

        huobi.save_history_trade_vol(config.NEED_TOBE_SUB_SYMBOL)
        if not self._hb:
            self._hb = Huobi()
        th = threading.Thread(target=init_history, args=(self._hb,))
        th.setDaemon(True)
        th.start()
        self.gress_bar_init_history.start()
        return True

    def start_work(self):
        def start(hb):
            logger.info("start work!!")
            log_config.output2ui("start work!!", 1)
            hb.run()
            logger.warning("work over!!")
            log_config.output2ui("work over!!", 2)

        if not self._hb:
            self._hb = Huobi()
        th = threading.Thread(target=start, args=(self._hb,))
        th.setDaemon(True)
        th.start()
        self.stop_button.config(state="normal")
        self.start_button.config(state="disabled")
        self.start_check_strategy_button.config(state="normal")
        self.verify_identity_button.config(state="disabled")
        self.working = True

    def stop_work(self):
        logger.info("stop_work!")
        log_config.output2ui("stop_work!")
        if self._hb:
            self._hb.exit()
        self.stop_check_strategy()

        self.stop_button.config(state="disabled")
        self.start_button.config(state="normal")
        self.register_button.config(state="normal")
        self.start_check_strategy_button.config(state="disabled")
        # self.verify_identity_button.config(state="normal")
        self.init_history_button.config(state="normal")
        self.verify_identity_button.config(state="normal")
        log_config.output2ui("Stop work successfully!", 8)
        self.working = False

    def start_check_strategy(self):
        # 策略检测线程启动
        logger.info("start_check_strategy...")
        log_config.output2ui("start_check_strategy...")
        self._strategy_pool.start_work()
        self.start_check_strategy_button.config(state="disabled")
        self.stop_check_strategy_button.config(state="normal")
        log_config.output2ui("Start check strategy successfully!", 8)

    def stop_check_strategy(self):
        logger.warning("stop_check_strategy...")
        log_config.output2ui("stop_check_strategy...", 2)
        self._strategy_pool.stop_work()
        self.start_check_strategy_button.config(state="normal")
        self.stop_check_strategy_button.config(state="disabled")
        log_config.output2ui("Stop check strategy successfully!", 8)

    def register_strategy(self):
        logger.info("register_strategy.")
        log_config.output2ui("register_strategy.")
        self._strategy_pool.clean_all()
        for strategy in strategies.STRATEGY_LIST:
            logger.info("register_strategy, strategy={}".format(strategy.name))
            log_config.output2ui("register_strategy, strategy={}".format(strategy.name))
            self._strategy_pool.register(strategy)
        self.clean_st_button.config(state="normal")
        self.register_button.config(state="disabled")
        log_config.output2ui("Register strategy successfully!", 8)

    def clean_strategy(self):
        logger.warning("clean_strategy...")
        log_config.output2ui("clean_strategy...", 2)
        self._strategy_pool.clean_all()
        self.clean_st_button.config(state="disabled")
        self.register_button.config(state="normal")
        log_config.output2ui("Clean strategy successfully!", 8)

    # def call_ckb_macd(self):
    #     print("check macd val=%d" % self.ckb_macd_val.get())

    def center_window(self, width, height):
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(size)

    def wait_buy_sell(self, price):
        if not price or not self.working:
            return False

        # logger.info("wait buy {}/{}, wait sell {}/{}, current price={}".format(config.WAIT_BUY_PRICE, config.WAIT_BUY_ACCOUNT, config.WAIT_SELL_PRICE, config.WAIT_SELL_ACCOUNT,price))
        if config.WAIT_BUY_PRICE>0 and config.WAIT_BUY_ACCOUNT>0.00001:
            if price <= config.WAIT_BUY_PRICE:
                ret = strategies.buy_market(config.NEED_TOBE_SUB_SYMBOL[0], amount=config.WAIT_BUY_ACCOUNT, record=False, current_price=price)
                if ret[0]:
                    log_config.output2ui("Wait to buy succeed! wait buy price={}, amount={}, actural price={}, amount={}".format(config.WAIT_BUY_PRICE, config.WAIT_BUY_ACCOUNT, price, ret[1]), 6)
                    logger.warning("Wait to buy succeed! wait buy price={}, amount={}, actural price={}, amount={}".format(config.WAIT_BUY_PRICE, config.WAIT_BUY_ACCOUNT, price, ret[1]))
                    config.WAIT_BUY_ACCOUNT = config.WAIT_BUY_ACCOUNT - ret[1]
                    log_config.send_mail("挂单买入: wait buy price={}, amount={}, actural price={}, amount={}".format(
                            config.WAIT_BUY_PRICE, config.WAIT_BUY_ACCOUNT, price, ret[1]))


        if config.WAIT_SELL_PRICE>0 and config.WAIT_SELL_ACCOUNT>0.00001:
            if price >= config.WAIT_SELL_PRICE:
                ret = strategies.sell_market(config.NEED_TOBE_SUB_SYMBOL[0], amount=config.WAIT_SELL_ACCOUNT, record=False, current_price=price)
                if ret[0]:
                    log_config.output2ui(
                        "Wait to sell succeed! wait sell price={}, amount={}, actural price={}, amount={}".format(
                            config.WAIT_SELL_PRICE, config.WAIT_SELL_ACCOUNT, price, ret[1]), 7)
                    logger.warning("Wait to sell succeed! wait sell price={}, amount={}, actural price={}, amount={}".format(
                            config.WAIT_SELL_PRICE, config.WAIT_SELL_ACCOUNT, price, ret[1]))
                    config.WAIT_SELL_ACCOUNT = config.WAIT_SELL_ACCOUNT - ret[1]
                    log_config.send_mail("挂单卖出: wait sell price={}, amount={}, actural price={}, amount={}".format(
                            config.WAIT_SELL_PRICE, config.WAIT_SELL_ACCOUNT, price, ret[1]))

    def update_coin(self, price=None):
        """
        更新盈利信息
        :param price:
        :return:
        """
        try:
            if not price:
                price_text = self.price_text.get()
                price = 0
                if len(price_text.split(":")) > 1:
                    price = float(price_text.split(":")[1])
                else:
                    price = 0
            else:
                price = float(price)

            bal_text = self.bal_text.get()
            coin_str = bal_text.split(",")[0].split(":")[1].split("/")
            dollar_str = bal_text.split(",")[1].split(":")[1].split("/")
            if len(coin_str) > 0 and len(dollar_str) > 0:
                coin_trade = float(coin_str[0])
                coin_frozen = float(coin_str[1])

                dollar_trade = float(dollar_str[0])
                dollar_frozen = float(dollar_str[1])
                total_coin_value = round(coin_trade + coin_frozen + (dollar_trade + dollar_frozen) / price, 3)
                total_dollar_value = round((coin_trade + coin_frozen) * price + dollar_trade + dollar_frozen, 3)
                self.coin_text.set("{}/{}".format(total_coin_value, total_dollar_value))
                if not process.ORG_COIN:
                    process.ORG_COIN = total_coin_value
                    process.ORG_DOLLAR = total_dollar_value

                profit_coin = round(total_coin_value - process.ORG_COIN, 3)
                profit_dollar = round(total_dollar_value - process.ORG_DOLLAR, 3)
                self.profit_text.set("{}/{}".format(profit_coin, profit_dollar))
        except Exception as e:
            pass
            # logger.exception("update_coin e={}".format(e))

    def update_ui(self):
        # # 每1000毫秒触发自己，形成递归，相当于死循环
        # self.root.after(1000, self.process_msg)
        logger.info("Welcome to Huobi Trade Tool")
        log_config.output2ui("Welcome to Huobi Trade Tool", 8)
        log_config.output2ui("Please Click [Verify Identity] to authenticate", 8)

        def update_price(price_text):
            while True:
                try:
                    msg = process.REALTIME_PRICE.get(block=True)
                    # print("update_price {}".format(msg))
                    (key, value), = msg.items()
                    global CURRENT_PRICE
                    CURRENT_PRICE = float(value)
                    price_text.set("{}:{}".format(key.upper(), value))

                    self.wait_buy_sell(price=CURRENT_PRICE)
                    self.update_coin(price=value)
                except Exception as e:
                    logger.exception("update_price exception....")
                    log_config.output2ui("update_price exception....", 3)
                    continue

        def update_balance(bal_text):
            while True:
                try:
                    msg = process.REALTIME_BALANCE.get(block=True)
                    bal_text.set(str(msg))
                except Exception as e:
                    logger.exception("update_balance exception....")
                    log_config.output2ui("update_balance exception....", 3)
                    continue

        def update_ui_log(log_text, trade_text):
            while True:
                try:
                    if not log_config.REALTIME_LOG.empty():
                        msg_dict = log_config.REALTIME_LOG.get(block=True)
                        if msg_dict["level"] == "BUY" or msg_dict["level"] == "SELL":
                            trade_text.configure(state='normal')
                            trade_text.insert(END, msg_dict["msg"], msg_dict["level"])
                            trade_text.see(END)
                            trade_text.configure(state='disabled')
                        else:
                            log_text.configure(state='normal')
                            log_text.insert(END, msg_dict["msg"], msg_dict["level"])
                            log_text.see(END)
                            log_text.configure(state='disabled')
                except Exception as e:
                    logger.exception("update_ui_log exception....")
                    log_config.output2ui("update_ui_log exception....", 3)
                    continue

        def update_kdj(kdj_text):
            while True:
                try:
                    kdj_15min = process.REALTIME_KDJ_15MIN.get(block=True)
                    # kdj_5min = process.REALTIME_KDJ_5MIN.get(block=True)
                    kdj_text.set("{}/{}/{}".format(round(kdj_15min[0], 2), round(kdj_15min[1], 2), round(kdj_15min[2], 2)))
                except Exception as e:
                    logger.exception("update_kdj exception....")
                    log_config.output2ui("update_kdj exception....", 3)

        def update_uml(uml_text):
            while True:
                try:
                    global CURRENT_PRICE
                    uml = process.REALTIME_UML.get(block=True)
                    diff1 = uml[0] - uml[1]
                    diff2 = uml[1] - uml[2]
                    uml_text.set("{}/{}/{}-{}/{}-{}/{}".format(round(uml[0], 3), round(uml[1], 3), round(uml[2], 3), round(diff1, 3), round(diff2, 3), round(diff1 / CURRENT_PRICE, 4), round(diff2 / CURRENT_PRICE, 4)))
                except Exception as e:
                    logger.exception("update_uml exception....")
                    log_config.output2ui("update_uml exception....", 3)

        th = threading.Thread(target=update_price, args=(self.price_text,))
        th.setDaemon(True)
        th.start()
        th = threading.Thread(target=update_ui_log, args=(self.log_text, self.trade_text, ))
        th.setDaemon(True)
        th.start()
        th = threading.Thread(target=update_balance, args=(self.bal_text,))
        th.setDaemon(True)
        th.start()

        th = threading.Thread(target=update_uml, args=(self.uml_text,))
        th.setDaemon(True)
        th.start()

        th = threading.Thread(target=update_kdj, args=(self.kdj_text,))
        th.setDaemon(True)
        th.start()
        return True

    def close_window(self):
        ans = askyesno("Warning", message="Are you sure to quit？")
        if ans:
            self.gress_bar_init_history.quit()
            self.gress_bar_verify_user.quit()
            self.stop_check_strategy()
            self.stop_work()
            self.root.destroy()
        else:
            return

    def verify_user_information(self):
        def verify_user_by_get_balance(currency, ak, sk, ws_site, rest_site, retry):
            from rs_util import HuobiREST
            config.CURRENT_WS_URL = config.WS_URLS[ws_site]
            config.CURRENT_REST_MARKET_URL = config.REST_URLS[rest_site][0]
            config.CURRENT_REST_TRADE_URL = config.REST_URLS[rest_site][1]
            hrs = HuobiREST(config.CURRENT_REST_MARKET_URL, config.CURRENT_REST_TRADE_URL, ak, sk, config.PRIVATE_KEY)
            hrs.get_accounts()
            # balance = strategies.get_balance(
            #     currency, ak, sk, retry)
            #
            self.gress_bar_verify_user.quit()
            if hrs.account_id and hrs.account_state == config.ACCOUNT_STATE_WORKING:
                # if balance:
                self._is_user_valid = True
                config.ACCESS_KEY = self._user_info.get("access_key", None)
                config.SECRET_KEY = self._user_info.get("secret_key", None)
                config.NEED_TOBE_SUB_SYMBOL.clear()
                config.NEED_TOBE_SUB_SYMBOL.append(self._user_info.get("trade", None))
                self._is_user_valid = True
                # self.verify_identity_button.config(state="disabled")
                self.init_history_button.config(state="normal")
                self.start_button.config(state="normal")
                strategies.update_balance(is_first=True)
                log_config.output2ui("Authentication passed!", 8)
            else:
                messagebox.showwarning("Error", "Authentication failed!")
                log_config.output2ui("Authentication failed!", 3)

        th = threading.Thread(target=verify_user_by_get_balance, args=(
            self._user_info.get("trade", None)[0:3],
            self._user_info.get("access_key", None),
            self._user_info.get("secret_key", None),
            self._user_info.get("ws_site", "BR"),
            self._user_info.get("rest_site", "BR"),
            3,))
        th.setDaemon(True)
        th.start()
        self.gress_bar_verify_user.start(text="Verifying user identity, please wait a moment...")

    def set_up_config(self):
        from popup_account import PopupAccountConfig
        pop = PopupAccountConfig(self._user_info, "Verify identity")
        self.root.wait_window(pop)
        if not self._user_info.get("ok", False):
            return
        logger.info("{}".format(self._user_info))
        log_config.output2ui("{}".format(self._user_info))
        self.price_text.set("")
        self.bal_text.set("")
        self.coin_text.set("")
        self.verify_user_information()
        # self.top = Toplevel(self.root)
        # label = Label(self.top, text="ACCESS_KEY")
        # label.pack()
        # entry = Entry(self.top)
        # entry.pack()
        #
        # btn = Button(self.top, text="OK")
        # btn.pack()

    def set_up_strategy(self):
        # from popup_trade import TradeStrategy
        # ret_data = {}
        # pop = TradeStrategy("wqrwqrqwrqwr", ret_data, 10)
        # self.root.wait_window(pop)
        # print(ret_data)
        from popup_strategy import PopupStrategy
        import strategies
        pop = PopupStrategy(strategies.move_stop_profit_params,
                            strategies.stop_loss_params,
                            strategies.kdj_buy_params,
                            strategies.kdj_sell_params,
                            strategies.vol_price_fly_params,
                            strategies.boll_strategy_params,
                            "Strategy config")
        self.root.wait_window(pop)
        print(strategies.kdj_buy_params)

    def set_up_system(self):
        from popup_system import PopupSystem
        value_dict = {"is_email": config.EMAIL_NOTIFY, "is_alarm": config.ALARM, "trade_min": config.TRADE_MIN_LIMIT_VALUE,
                      "trade_max": config.TRADE_MAX_LIMIT_VALUE, "wait_buy_price": config.WAIT_BUY_PRICE,
                      "wait_buy_account": config.WAIT_BUY_ACCOUNT, "wait_sell_price":config.WAIT_SELL_PRICE, "wait_sell_account":config.WAIT_SELL_ACCOUNT}
        pop = PopupSystem(value_dict)
        self.root.wait_window(pop)
        if pop.is_ok:
            config.EMAIL_NOTIFY = value_dict["is_email"]
            config.ALARM = value_dict["is_alarm"]
            config.TRADE_MIN_LIMIT_VALUE = value_dict["trade_min"]
            config.TRADE_MAX_LIMIT_VALUE = value_dict["trade_max"]
            config.WAIT_BUY_PRICE = value_dict["wait_buy_price"]
            config.WAIT_BUY_ACCOUNT = value_dict["wait_buy_account"]
            config.WAIT_SELL_PRICE = value_dict["wait_sell_price"]
            config.WAIT_SELL_ACCOUNT = value_dict["wait_sell_account"]

    def clean_profit(self):
        process.ORG_COIN = None
        self.profit_text.set("0/0")


if __name__ == '__main__':
    root = Tk()
    # root.geometry('80x80+10+10')
    my_gui = MainUI(root)
    config.ROOT = root
    root.protocol('WM_DELETE_WINDOW', my_gui.close_window)
    my_gui.center_window(1250, 600)
    root.maxsize(1250, 600)
    # root.minsize(320, 240)
    # root.iconbitmap('spider_128px_1169260_easyicon.net.ico')
    my_gui.update_ui()
    # my_gui.init_history_asyn()
    root.mainloop()
    logger.info("==========over================")
