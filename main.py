#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/18
# Function:
import time
import datetime
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
import wechat_helper
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
        self.first_login = True
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
        self.verify_identity_button = Button(root, text="Verify Identity", command=self.set_up_account, width=20)

        self.init_history_button = Button(root, text="Init History", command=self.init_history_asyn, width=20)

        self.strategy_setting_button = Button(root, text="Strategy Config", command=self.set_up_strategy, width=20)
        self.system_setting_button = Button(root, text="System Config", command=self.set_up_system, width=20)

        self.label_pop = Label(root, text="实时价格: ", width=15)
        self.price_text = StringVar()
        self.price_text.set("")
        self.price_label = Label(root, textvariable=self.price_text, foreground='red', background="gray",
                                 font=("", 12, 'bold'), width=25)
        # self.price_label.pack()

        self.label_bal = Label(root, text="当前账户余额(币,金): ", width=15)
        self.bal_text = StringVar()
        self.bal_text.set("")
        self.bal_label = Label(root, textvariable=self.bal_text, foreground='red', background="gray",
                               font=("", 12, 'bold'), width=25)

        self.label_coin = Label(root, text="当前账户总资产(按币/金): ", width=20)
        self.coin_text = StringVar()
        self.coin_text.set("")
        self.coin_label = Label(root, textvariable=self.coin_text, foreground='red', background="gray",
                                font=("", 12, 'bold'), width=30)

        self.label_profit = Label(root, text="盈利情况(币/金本位): ", width=20)
        self.profit_text = StringVar()
        self.profit_text.set("")
        self.profit_label = Label(root, textvariable=self.profit_text, foreground='red', background="gray",
                                  font=("", 12, 'bold'), width=25)
        self.clean_profit_button = Button(root, text="重置", command=self.reset_profit, width=8)

        # row6 = Frame(root)
        # row6.pack(fill="x", ipadx=1, ipady=1)

        self.label_kdj = Label(root, text="15分钟KDJ: ", width=15)
        self.kdj_text = StringVar()
        self.kdj_text.set("")
        self.kdj_label = Label(root, textvariable=self.kdj_text, foreground='red', background="gray",
                               font=("", 12, 'bold'), width=25)

        self.label_uml = Label(root, text="布林线: ", width=15)
        self.uml_text = StringVar()
        self.uml_text.set("")
        self.uml_label = Label(root, textvariable=self.uml_text, foreground='red', background="gray",
                               font=("", 12, 'bold'), width=40)

        # 初始信息
        self.label_origin = Label(root, text="初始价格/币数/USDT/总价值: ", width=25)
        self.origin_text = StringVar()
        self.origin_text.set("")
        self.origin_label = Label(root, textvariable=self.origin_text, foreground='red', background="gray",
                               font=("", 12, 'bold'), width=30)

        self.label_now = Label(root, text="大盘涨跌幅/账户涨跌幅: ", width=22)
        self.now_text = StringVar()
        self.now_text.set("")
        self.now_label = Label(root, textvariable=self.now_text, foreground='red', background="gray",
                               font=("", 12, 'bold'), width=30)

        self.label_run_log = Label(root, text="运行日志: ", width=10)
        self.log_text = ScrolledText(root, width=60, height=26)
        self.label_trade_log = Label(root, text="交易日志: ", width=10)
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
        self.system_setting_button.grid(row=2, column=0)
        self.strategy_setting_button.grid(row=3, column=0)
        self.start_button.grid(row=4, column=0)

        self.register_button.grid(row=5, column=0)
        self.start_check_strategy_button.grid(row=6, column=0)
        self.clean_st_button.grid(row=7, column=0)
        self.stop_check_strategy_button.grid(row=8, column=0)
        self.stop_button.grid(row=9, column=0)


        self.label_pop.grid(row=0, column=1)
        self.price_label.grid(row=0, column=2)

        self.label_origin.grid(row=0, column=3)
        self.origin_label.grid(row=0, column=4)


        self.label_bal.grid(row=1, column=1)
        self.bal_label.grid(row=1, column=2)#columnspan=2

        self.label_coin.grid(row=1, column=3)
        self.coin_label.grid(row=1, column=4)
        # self.label_worth.grid(row=0, column=7)
        # self.worth_label.grid(row=0, column=8)

        self.label_profit.grid(row=2, column=1)
        self.profit_label.grid(row=2, column=2)

        self.label_now.grid(row=2, column=3)
        self.now_label.grid(row=2, column=4)

        self.clean_profit_button.grid(row=2, column=5)

        # k d 指标位置
        # row6.grid(row=2, column=1)
        self.label_kdj.grid(row=3, column=1)
        self.kdj_label.grid(row=3, column=2)
        self.label_uml.grid(row=3, column=3)
        self.uml_label.grid(row=3, column=4)    #columnspan=2

        self.label_run_log.grid(row=4, column=1)
        self.log_text.grid(row=5, column=1, rowspan=5, columnspan=3)
        self.label_trade_log.grid(row=4, column=4)
        self.trade_text.grid(row=5, column=4, rowspan=5, columnspan=3)

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
            logger.info("wait_buy_sell not be trigger!")
            return False

        buy_prices = config.WAIT_BUY_PRICE
        buy_amounts = config.WAIT_BUY_ACCOUNT
        sell_prices = config.WAIT_SELL_PRICE
        sell_amounts = config.WAIT_SELL_ACCOUNT

        symbol = config.NEED_TOBE_SUB_SYMBOL[0]
        for i, buy_price in enumerate(buy_prices):
            # 循环遍历挂单买
            buy_amount = buy_amounts[i]
            if buy_price > 0 and buy_amount > config.TRADE_MIN_LIMIT_VALUE:
                if price <= buy_price:
                    ret = strategies.buy_market(symbol, amount=buy_amount, record=True, current_price=price)
                    if ret[0]:
                        msg = "挂单买入{}成功: 挂单价格={}$, 挂单金额={}$, 实际价格={}$, 实际买入金额={}$.".format(symbol, buy_price, buy_amount, price, ret[1])
                        success = False
                        if ret[0] == 1:
                            msg += "-交易成功！"
                            config.WAIT_BUY_ACCOUNT[i] = buy_amount - ret[1]
                            success = True
                        elif ret[0] == 2:
                            msg += "-交易被取消, 此次交易额未达到设置的最低交易额限制()$!".format(config.TRADE_MIN_LIMIT_VALUE)
                        elif ret[0] == 3:
                            msg += "-交易失败, 失败原因:{}！".format(ret[2])
                        log_config.output2ui(msg, 6)
                        logger.warning(msg)
                        log_config.notify_user(msg, own=True)
                        log_config.notify_user(log_config.make_msg(0, symbol, price))



            # 循环遍历挂单卖
            sell_price = sell_prices[i]
            sell_amount = sell_amounts[i]
            if sell_price > 0 and sell_amount > 0.00001:
                if price >= sell_price:
                    ret = strategies.sell_market(symbol, amount=sell_amount, record=False, current_price=price)
                    if ret[0]:
                        config.WAIT_SELL_ACCOUNT[i] = sell_amount - ret[1]
                        msg = "挂单卖出{}: 挂单价格={}, 挂单个数={}个, 实际价格={}, 实际挂单卖出个数={}个.".format(symbol,
                                sell_price, sell_amount, price, ret[1])
                        success = False
                        if ret[0] == 1:
                            msg += "-交易成功！"
                            config.WAIT_SELL_ACCOUNT[i] = sell_amount - ret[1]
                            success = True
                        elif ret[0] == 2:
                            msg += "-交易被取消, 此次交易额未达到设置的最低交易额限制()$!".format(config.TRADE_MIN_LIMIT_VALUE)
                        elif ret[0] == 3:
                            msg += "-交易失败, 失败原因:{}！".format(ret[2])
                        log_config.output2ui(msg, 7)
                        logger.warning(msg)
                        log_config.notify_user(msg, own=True)
                        log_config.notify_user(log_config.make_msg(1, symbol, price))


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
            coin_str = bal_text.split(",")[0].split("/")
            dollar_str = bal_text.split(",")[1].split("/")
            if len(coin_str) > 0 and len(dollar_str) > 0:
                coin_trade = float(coin_str[0])
                coin_frozen = float(coin_str[1])

                dollar_trade = float(dollar_str[0])
                dollar_frozen = float(dollar_str[1])
                total_coin_value = coin_trade + coin_frozen + (dollar_trade + dollar_frozen) / price
                total_dollar_value = (coin_trade + coin_frozen) * price + dollar_trade + dollar_frozen
                self.coin_text.set("{}/{}".format(round(total_coin_value, 4), round(total_dollar_value, 2)))
                if not process.ORG_COIN_TOTAL:
                    process.START_TIME = datetime.datetime.now()
                    process.ORG_CHICANG = (coin_trade+coin_frozen)*price/total_dollar_value
                    process.ORG_COIN_TRADE = coin_trade
                    process.ORG_COIN_FROZEN = coin_frozen
                    process.ORG_DOLLAR_TRADE = dollar_trade
                    process.ORG_DOLLAR_FROZEN = dollar_frozen
                    process.ORG_COIN_TOTAL = total_coin_value
                    process.ORG_DOLLAR_TOTAL = total_dollar_value
                    process.ORG_PRICE = price
                    # 更新总额, 初始化更新一次即可
                    self.origin_text.set("{}/{}/{}/{}".format(price, round(coin_trade + coin_frozen,4), round(dollar_trade + dollar_frozen, 2), round(total_dollar_value, 2)))

                profit_coin = round(total_coin_value - process.ORG_COIN_TOTAL, 3)
                profit_dollar = round(total_dollar_value - process.ORG_DOLLAR_TOTAL, 3)
                self.profit_text.set("{}/{}".format(profit_coin, profit_dollar))

                #更新大盘涨跌幅和当前账户的涨跌幅
                self.now_text.set("{}% / {}%".format(round((price-process.ORG_PRICE)*100/process.ORG_PRICE, 2), round((total_dollar_value - process.ORG_DOLLAR_TOTAL)*100 / process.ORG_DOLLAR_TOTAL, 3)))
        except Exception as e:
            logger.exception("update_coin e={}".format(e))

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

        def notify_profit_info():
            hour_report_start_time = None
            daily_report_start_time = None
            while 1:
                time.sleep(60)
                if self.working:
                    now_time = datetime.datetime.now()
                    if not daily_report_start_time:
                        daily_report_start_time = now_time
                    else:
                        if (now_time-daily_report_start_time).total_seconds() > 86400:
                            today_logs = [y for x, y in config.TRADE_ALL_LOG.items() if x > daily_report_start_time]
                            daily_report_start_time = now_time
                            daily_msg = "最近１天的交易记录如下:\n"+"\n".join(today_logs)
                            log_config.output2ui(daily_msg, 8)
                            logger.warning(daily_msg)
                            log_config.notify_user(daily_msg, own=True)

                    if not hour_report_start_time:
                        hour_report_start_time = now_time
                    else:
                        if (now_time-hour_report_start_time).total_seconds() > 7200:
                            hour_report_start_time = now_time

                            global CURRENT_PRICE
                            bal0, bal0_f, bal1, bal1_f = strategies.update_balance()
                            total = (bal0+bal0_f)*CURRENT_PRICE+bal1+bal1_f
                            chicang = ((bal0 + bal0_f) * CURRENT_PRICE) / total
                            dapan_profit = round((CURRENT_PRICE - process.ORG_PRICE) * 100 / process.ORG_PRICE, 2)
                            account_profit = round((total - process.ORG_DOLLAR_TOTAL) * 100 / process.ORG_DOLLAR_TOTAL, 2)
                            is_win = u"是" if account_profit>=dapan_profit else u"否"
                            msg_own = u"\n火币量化交易系统运行中:\n币种:{}\n用户风险承受力:{}\n启动时间:{}\n当前时间:{}\n启动时价格:{}" \
                                      u"\n当前价格:{}" \
                                      u"\n启动时持币量:可用{},冻结{},仓位{}%" \
                                      u"\n当前持币量:可用{},冻结{},仓位{}%" \
                                      u"\n启动时持金量:可用{},冻结{}" \
                                      u"\n当前持金量:可用{},冻结{}" \
                                      u"\n当前账户总价值:${}\n大盘涨跌幅:{}%\n当前账户涨跌幅:{}%\n当前盈利：{}$\n是否跑羸大盘:{}".format(
                                config.NEED_TOBE_SUB_SYMBOL[0].upper(), config.RISK,
                                process.START_TIME.strftime("%Y/%m/%d, %H:%M:%S"),
                                now_time.strftime("%Y/%m/%d, %H:%M:%S"), round(process.ORG_PRICE, 2),
                                round(CURRENT_PRICE, 2),
                                round(process.ORG_COIN_TRADE, 4), round(process.ORG_COIN_FROZEN, 4),
                                round(process.ORG_CHICANG * 100, 2), round(bal0, 4), round(bal0_f, 4), round(chicang * 100, 2),
                                round(process.ORG_DOLLAR_TRADE, 2), round(process.ORG_DOLLAR_FROZEN, 2), round(bal1, 2), round(bal1_f, 2),
                                round(total, 2), dapan_profit, account_profit, round(total - process.ORG_DOLLAR_TOTAL, 2), is_win)

                            msg_other = u"火币量化交易系统运行中:\n币种:{}\n用户风险承受力:{}\n启动时间:{}\n当前时间:{}\n启动时价格:{}\n当前价格:{}\n启动时持币量:可用{},冻结{},仓位{}%\n当前持币量:可用{},冻结{},仓位{}%\n启动时持金量:可用{},冻结{}\n当前持金量:可用{},冻结{}\n当前账户总资产:${}\n大盘涨跌幅:{}%\n当前账户涨跌幅:{}%\n当前盈利：{}$\n是否跑羸大盘:{}"\
                                .format(config.NEED_TOBE_SUB_SYMBOL[0].upper(), config.RISK,
                                    process.START_TIME.strftime("%Y/%m/%d, %H:%M:%S"),
                                    now_time.strftime("%Y/%m/%d, %H:%M:%S"),
                                    round(process.ORG_PRICE, 2), round(CURRENT_PRICE, 2),
                                    "***", "***", round(process.ORG_CHICANG * 100, 2), "***", "***", round(chicang * 100, 2),
                                    "***", "***", "***", "***",
                                    "***",
                                    dapan_profit,
                                    account_profit,"***",
                                    is_win)
                            log_config.output2ui(msg_own, level=8)
                            logger.warning(msg_own)
                            ret1 = log_config.notify_user(msg_own, own=True)
                            ret2 = log_config.notify_user(msg_other)


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

        th = threading.Thread(target=notify_profit_info)
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

    def set_up_account(self):
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
        def login_wechat():
            print("需要扫码登录微信！")
            wechat_helper.login_wechat()

        from popup_system import PopupSystem
        value_dict = {"is_email": config.EMAIL_NOTIFY, "is_alarm": config.ALARM_NOTIFY, "is_alarm_trade": config.ALARM_TRADE_DEFAULT,
                      "trade_min": config.TRADE_MIN_LIMIT_VALUE, "alarm_time": config.ALARM_TIME,
                      "trade_max": config.TRADE_MAX_LIMIT_VALUE, "wait_buy_price": config.WAIT_BUY_PRICE,
                      "wait_buy_account": config.WAIT_BUY_ACCOUNT, "wait_sell_price":config.WAIT_SELL_PRICE, "wait_sell_account":config.WAIT_SELL_ACCOUNT,
                      "risk": config.RISK, "emails": config.EMAILS, "wechats": config.WECHATS}

        pop = PopupSystem(value_dict)
        self.root.wait_window(pop)
        if pop.is_ok:
            config.EMAIL_NOTIFY = value_dict["is_email"]
            config.ALARM_NOTIFY = value_dict["is_alarm"]
            config.ALARM_TRADE_DEFAULT = value_dict["is_alarm_trade"]
            config.ALARM_TIME = value_dict["alarm_time"]

            config.TRADE_MIN_LIMIT_VALUE = value_dict["trade_min"]
            config.TRADE_MAX_LIMIT_VALUE = value_dict["trade_max"]
            config.WAIT_BUY_PRICE = value_dict["wait_buy_price"]
            config.WAIT_BUY_ACCOUNT = value_dict["wait_buy_account"]
            config.WAIT_SELL_PRICE = value_dict["wait_sell_price"]
            config.WAIT_SELL_ACCOUNT = value_dict["wait_sell_account"]
            config.RISK = value_dict["risk"]
            emails = value_dict.get("emails", "").strip().split("\n")
            wechats = value_dict.get("wechats", "").strip().split("\n")
            log_config.output2ui("system config:\n{}！".format(value_dict))
            is_login = value_dict.get("login_wechat_now", 0)
            config.EMAILS = []
            for email in emails:
                if email and len(email) > 5 and "@" in email:
                    config.EMAILS.append(email)

            config.WECHATS = []
            for wechat in wechats:
                if wechat and len(wechat) > 2:
                    config.WECHATS.append(wechat)

            if config.EMAIL_NOTIFY and config.WECHATS and is_login:
                log_config.output2ui("需要扫码登录微信！")
                self.first_login = False
                th = threading.Thread(target=login_wechat)
                th.setDaemon(True)
                th.start()

    def reset_profit(self):
        process.ORG_COIN_TOTAL = None
        self.bal_text.set("")
        strategies.update_balance()
        self.profit_text.set("0/0")
        self.origin_text.set("0/0/0/0")


if __name__ == '__main__':
    root = Tk()
    # root.geometry('80x80+10+10')
    my_gui = MainUI(root)
    config.ROOT = root
    root.protocol('WM_DELETE_WINDOW', my_gui.close_window)
    my_gui.center_window(1350, 610)
    root.maxsize(1350, 610)
    # root.minsize(320, 240)
    # root.iconbitmap('spider_128px_1169260_easyicon.net.ico')
    my_gui.update_ui()
    # my_gui.init_history_asyn()
    root.mainloop()
    logger.info("==========over================")
