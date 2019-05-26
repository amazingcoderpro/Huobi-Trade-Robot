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
import requests
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
        self.verify = True
        self.notify_queue = queue.Queue()
        self.gress_bar_init_history = GressBar()
        self.gress_bar_verify_user = GressBar()
        self.root = root
        self.top = None
        self._is_user_valid = False
        self._user_info = {}
        self._strategy_dict = {}
        root.title("火币量化交易系统(15691820861)")
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
        self.start_button = Button(root, text=u"开始工作", command=self.start_work, width=20)
        # self.start_button.pack()

        self.stop_button = Button(root, text=u"停止工作", command=self.stop_work, width=20)
        # self.stop_button.pack()

        self.register_button = Button(root, text=u"注册策略", command=self.register_strategy, width=20)
        # self.register_button.pack()

        self.start_check_strategy_button = Button(root, text=u"开始执行策略", command=self.start_check_strategy, width=20)
        # self.start_check_strategy_button.pack()

        self.stop_check_strategy_button = Button(root, text="停止执行策略", command=self.stop_check_strategy, width=20)
        # self.stop_check_strategy_button.pack()

        self.clean_st_button = Button(root, text="清空策略", command=self.clean_strategy, width=20)
        # self.clean_st_button.pack()
        self.verify_identity_button = Button(root, text="身份验证", command=self.set_up_account, width=20)

        self.init_history_button = Button(root, text="系统初始化", command=self.init_history_asyn, width=20)

        self.strategy_setting_button = Button(root, text="策略配置", command=self.set_up_strategy, width=20)
        self.system_setting_button = Button(root, text="系统配置", command=self.set_up_system, width=20)

        self.label_pop = Label(root, text=u"实时价格: ", width=15)
        self.price_text = StringVar()
        self.price_text.set("")
        self.price_label = Label(root, textvariable=self.price_text, foreground='blue', background="gray",
                                 font=("", 12, 'bold'), width=25)
        # self.price_label.pack()

        self.label_bal = Label(root, text=u"当前账户余额(币,金): ", width=15)
        self.bal_text = StringVar()
        self.bal_text.set("")
        self.bal_label = Label(root, textvariable=self.bal_text, foreground='blue', background="gray",
                               font=("", 12, 'bold'), width=25)

        self.label_coin = Label(root, text=u"当前账户总资产(按币/金/仓位): ", width=22)
        self.coin_text = StringVar()
        self.coin_text.set("")
        self.coin_label = Label(root, textvariable=self.coin_text, foreground='blue', background="gray",
                                font=("", 12, 'bold'), width=30)

        self.label_profit = Label(root, text=u"盈利情况(币/金本位): ", width=20)
        self.profit_text = StringVar()
        self.profit_text.set("")
        self.profit_label = Label(root, textvariable=self.profit_text, foreground='blue', background="gray",
                                  font=("", 12, 'bold'), width=25)
        self.clean_profit_button = Button(root, text=u"重置", command=self.reset_profit, width=8)

        # row6 = Frame(root)
        # row6.pack(fill="x", ipadx=1, ipady=1)

        self.label_kdj = Label(root, text=u"15分钟KDJ: ", width=15)
        self.kdj_text = StringVar()
        self.kdj_text.set("")
        self.kdj_label = Label(root, textvariable=self.kdj_text, foreground='#9A32CD', background="gray",
                               font=("", 12, 'bold'), width=25)

        self.label_uml = Label(root, text=u"布林线: ", width=15)
        self.uml_text = StringVar()
        self.uml_text.set("")
        self.uml_label = Label(root, textvariable=self.uml_text, foreground='#9A32CD', background="gray",
                               font=("", 12, 'bold'), width=30)

        # 初始信息
        self.label_origin = Label(root, text=u"初始价格/币数/USDT/总价值: ", width=25)
        self.origin_text = StringVar()
        self.origin_text.set("")
        self.origin_label = Label(root, textvariable=self.origin_text, foreground='blue', background="gray",
                               font=("", 12, 'bold'), width=30)

        self.nick_name_text = StringVar()
        self.nick_name_text.set(config.NICK_NAME)
        self.nick_name_text_label = Label(root, textvariable=self.nick_name_text, foreground='blue', background="gray",
                               font=("", 12, 'bold'), width=10)

        self.label_now = Label(root, text=u"大盘涨跌幅/账户涨跌幅: ", width=22)
        self.now_text = StringVar()
        self.now_text.set("")
        self.now_label = Label(root, textvariable=self.now_text, foreground='blue', background="gray",
                               font=("", 12, 'bold'), width=30)

        self.label_run_log = Label(root, text=u"运行日志: ", width=10)
        self.log_text = ScrolledText(root, width=60, height=26)
        self.label_trade_log = Label(root, text=u"交易日志: ", width=10)
        self.trade_text = ScrolledText(root, width=60, height=26)
        # self.log_text.pack()
        # 创建一个TAG，其前景色为红色
        self.log_text.tag_config('BUY', foreground='green', background="#C1CDC1", font=("", 11, 'bold'))
        self.log_text.tag_config('SELL', foreground='red', background="#BC8F8F", font=("", 11, 'bold'))
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

        # self.register_button.grid(row=5, column=0)
        # self.start_check_strategy_button.grid(row=6, column=0)
        # self.clean_st_button.grid(row=7, column=0)
        # self.stop_check_strategy_button.grid(row=8, column=0)
        self.stop_button.grid(row=5, column=0)

        self.label_pop.grid(row=0, column=1)
        self.price_label.grid(row=0, column=2)

        self.label_origin.grid(row=0, column=3)
        self.origin_label.grid(row=0, column=4)
        self.nick_name_text_label.grid(row=0, column=5)

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
                log_config.output2ui(u"系统初始化失败!", 3)
                messagebox.showwarning("Error", u"系统初始化失败!")
                return False
            log_config.output2ui(u"系统初始化成功!", 8)
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
            log_config.output2ui(u"系统启动!!", 1)
            hb.run()
            logger.warning("work over!!")
            log_config.output2ui(u"工作结束!!", 2)

        if not self.verify:
            log_config.output2ui(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!", 5)
            messagebox.showerror(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!")
            return

        process.ORG_COIN_TRADE = None
        process.ORG_COIN_FROZEN = None
        process.ORG_DOLLAR_TRADE = None
        process.ORG_DOLLAR_FROZEN = None
        process.ORG_COIN_TOTAL = None
        process.ORG_DOLLAR_TOTAL = None
        process.ORG_PRICE = None
        process.ORG_DOLLAR_TOTAL = None  # 总价值金量, 所有资产换成usdt

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

        # log_config.output2ui("Stop work successfully!", 8)
        log_config.output2ui(u"系统已停止工作!", 8)
        self.working = False

    def start_check_strategy(self):
        if not self.verify:
            log_config.output2ui(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!", 5)
            return

        # 策略检测线程启动
        logger.info("start_check_strategy...")
        log_config.output2ui(u"启动策略...")
        self._strategy_pool.start_work()
        self.start_check_strategy_button.config(state="disabled")
        self.stop_check_strategy_button.config(state="normal")
        log_config.output2ui(u"启动策略成功，将为您智能发现最佳交易时机并进行自动交易！", 8)

    def stop_check_strategy(self):
        logger.warning("stop_check_strategy...")
        log_config.output2ui(u"停止执行策略...", 2)
        self._strategy_pool.stop_work()
        self.start_check_strategy_button.config(state="normal")
        self.stop_check_strategy_button.config(state="disabled")
        log_config.output2ui(u"停止执行策略成功!", 8)

    def register_strategy(self):
        if not self.verify:
            log_config.output2ui(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!", 5)
            return

        logger.info("register_strategy.")
        log_config.output2ui(u"注册策略...")
        self._strategy_pool.clean_all()
        for strategy in strategies.STRATEGY_LIST:
            logger.info("register_strategy, strategy={}".format(strategy.name))
            log_config.output2ui("register_strategy, strategy={}".format(strategy.name))
            self._strategy_pool.register(strategy)
        self.clean_st_button.config(state="normal")
        self.register_button.config(state="disabled")
        log_config.output2ui(u"注册策略成功!", 8)

    def clean_strategy(self):
        logger.warning("clean_strategy...")
        log_config.output2ui(u"清空所有策略...", 2)
        self._strategy_pool.clean_all()
        self.clean_st_button.config(state="disabled")
        self.register_button.config(state="normal")
        log_config.output2ui(u"清空所有策略成功!", 8)

    # def call_ckb_macd(self):
    #     print("check macd val=%d" % self.ckb_macd_val.get())

    def center_window(self, width, height):
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(size)

    def wait_buy_sell(self, price):
        if not price or not self.working:
            logger.info("wait_buy_sell not be trigger!, price={}, working={}".format(price, self.working))
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
                        msg = u"挂单买入{}成功: 挂单价格={}$, 挂单金额={}$, 实际价格={}$, 实际买入金额={}$.".format(symbol, buy_price, buy_amount, price, ret[1])
                        success = False
                        if ret[0] == 1:
                            msg += u"-交易成功！"
                            config.WAIT_BUY_ACCOUNT[i] = buy_amount - ret[1]
                            success = True
                        elif ret[0] == 2:
                            msg += u"-交易被取消, 取消原因: {}!".format(ret[2])
                        elif ret[0] == 3:
                            msg += u"-交易失败, 失败原因: {}！".format(ret[2])
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
                        msg = u"挂单卖出{}: 挂单价格={}, 挂单个数={}个, 实际价格={}, 实际挂单卖出个数={}个.".format(symbol,
                                sell_price, sell_amount, price, ret[1])
                        success = False
                        if ret[0] == 1:
                            msg += u"-交易成功！"
                            config.WAIT_SELL_ACCOUNT[i] = sell_amount - ret[1]
                            success = True
                        elif ret[0] == 2:
                            u"-交易被取消, 取消原因: {}!".format(ret[2])
                        elif ret[0] == 3:
                            msg += u"-交易失败, 失败原因: {}！".format(ret[2])
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
                if total_dollar_value>0:
                    position = (coin_trade + coin_frozen)*price / total_dollar_value
                else:
                    position = 0
                self.coin_text.set("{}/{}/{}%".format(round(total_coin_value, 4), round(total_dollar_value, 2), round(position*100, 2)))
                if not process.ORG_COIN_TOTAL:
                    process.START_TIME = datetime.datetime.now()
                    if total_dollar_value>0:
                        process.ORG_CHICANG = (coin_trade+coin_frozen)*price/total_dollar_value
                    else:
                        process.ORG_CHICANG = 0
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
                if process.ORG_DOLLAR_TOTAL>0:
                    account_zhang = round((total_dollar_value - process.ORG_DOLLAR_TOTAL)*100 / process.ORG_DOLLAR_TOTAL, 3)
                else:
                    account_zhang = 0

                self.now_text.set("{}% / {}%".format(round((price-process.ORG_PRICE)*100/process.ORG_PRICE, 2), account_zhang))
        except Exception as e:
            logger.exception("update_coin e={}".format(e))

    def update_ui(self):
        # # 每1000毫秒触发自己，形成递归，相当于死循环
        # self.root.after(1000, self.process_msg)
        logger.info("Welcome to Huobi Trade Tool")
        log_config.output2ui(u"-----------------欢迎使用火币量化交易系统！----------------- ---\n　 本系统由资深量化交易专家和算法团队倾力打造，对接火币官方接口，经过长达两年的不断测试与优化，"
                             u"本地化运行，更加安全可控，策略可定制，使用更方便!　\n   系统结合历史与实时数据进行分析，加上内置的多套专业策略组合算法，根据您的仓位、策略定制因"
                             u"子和风险接受能力等的不同，智能发现属于您的最佳交易时机进行自动化交易，并可以设置邮件和微信提醒，"
                             u"真正帮您实现24小时实时盯盘，专业可靠，稳定盈利！", 8)
        log_config.output2ui(
            u"免责声明:\n  1. 使用本系统时，系统将会根据程序判断帮您进行自动化交易，因此产生的盈利或亏损均由您个人负责，与系统开发团队无关\n  2. 本系统需要您提供您在火币官网申请的API密钥，获取火币官方授权后方能正常运行，本系统承诺不会上传您的密钥到火币平台以外的地址，请您妥善保管好自己的密钥，发生丢失造成的财产损失与本系统无关\n  3. 因操作失误，断网，断电，程序异常等因素造成的经济损失与系统开发团队无关\n  4.如需商业合作，充值或使用过程中如有任何问题可与售后团队联系，联系方式:15691820861",
            8)
        log_config.output2ui(u"使用步骤如下:", 8)
        log_config.output2ui(u"第一步，请点击 [身份验证] 输入您在火币官网申请的API KEY，选择您想自动化交易的币种，进行授权认证！", 8)



        def update_price(price_text):
            while self.verify:
                try:
                    time.sleep(1)
                    msg = process.REALTIME_PRICE    #.get(block=True)
                    if msg:
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
            while self.verify:
                try:
                    time.sleep(5)
                    msg = process.REALTIME_BALANCE #.get(block=True)
                    bal_text.set(str(msg))
                except Exception as e:
                    logger.exception("update_balance exception....")
                    log_config.output2ui("update_balance exception....", 3)
                    continue

        def update_ui_log(log_text, trade_text):
            while 1:
                try:
                    if not log_config.REALTIME_LOG.empty():
                        try:
                            msg_dict = log_config.REALTIME_LOG.get(block=False)
                        except:
                            time.sleep(1)
                        if msg_dict:
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
                    else:
                        time.sleep(1)
                except Exception as e:
                    logger.exception("update_ui_log exception....")
                    log_config.output2ui("update_ui_log exception....", 3)
                    continue

        def update_kdj(kdj_text):

            while self.verify:
                try:
                    time.sleep(5)
                    kdj_15min = process.REALTIME_KDJ_15MIN #.get(block=True)
                    # kdj_5min = process.REALTIME_KDJ_5MIN.get(block=True)
                    kdj_text.set("{}/{}/{}".format(round(kdj_15min[0], 2), round(kdj_15min[1], 2), round(kdj_15min[2], 2)))
                except Exception as e:
                    logger.exception("update_kdj exception....")
                    log_config.output2ui("update_kdj exception....", 3)

        def update_uml(uml_text):
            while self.verify:
                try:
                    time.sleep(5)
                    global CURRENT_PRICE
                    uml = process.REALTIME_UML#.get(block=True)
                    diff1 = uml[0] - uml[1]
                    diff2 = uml[1] - uml[2]
                    # uml_text.set("{}/{}/{}-{}/{}-{}/{}".format(round(uml[0], 6), round(uml[1], 6), round(uml[2], 6), round(diff1, 6), round(diff2, 6), round(diff1 / CURRENT_PRICE, 5), round(diff2 / CURRENT_PRICE, 5)))
                    uml_text.set("{}/{}/{}".format(round(uml[0], 6), round(uml[1], 6), round(uml[2], 6)))

                    if process.LAST_VERIFY_TIME:
                        if (datetime.datetime.now() - process.LAST_VERIFY_TIME).total_seconds() > 3600*24:
                            ret = self.verify_huobi(config.ACCESS_KEY)
                            if not ret[0]:
                                self.clean_strategy()
                                self.stop_check_strategy()
                                self.stop_work()
                                time.sleep(2)
                                log_config.output2ui(ret[1], 5)
                                messagebox.showwarning("Error", ret[1])
                            else:
                                process.LAST_VERIFY_TIME = datetime.datetime.now()

                    else:
                        process.LAST_VERIFY_TIME = datetime.datetime.now()
                except Exception as e:
                    logger.exception("update_uml exception....")
                    log_config.output2ui("update_uml exception....", 3)

        def notify_profit_info():
            hour_report_start_time = None
            daily_report_start_time = None
            while self.verify:
                time.sleep(60)
                if self.working:
                    try:
                        now_time = datetime.datetime.now()
                        if not daily_report_start_time:
                            daily_report_start_time = now_time
                        else:
                            run_total_seconds = (now_time-daily_report_start_time).total_seconds()
                            logger.info("system run total seconds={}, trade_notify_interval={}".format(run_total_seconds, config.TRADE_HISTORY_REPORT_INTERVAL))
                            if (run_total_seconds > config.TRADE_HISTORY_REPORT_INTERVAL*3600) or config.SEND_HISTORY_NOW > 0:
                                if config.SEND_HISTORY_NOW > 0:
                                    # 立即发送，　不影响周期发送逻辑
                                    beg = now_time-datetime.timedelta(hours=config.SEND_HISTORY_NOW)
                                    interval = int(config.SEND_HISTORY_NOW)
                                else:
                                    beg = daily_report_start_time
                                    interval = int(config.TRADE_HISTORY_REPORT_INTERVAL)

                                # 只要发送过，就把起始时间重新置成当前时间　
                                config.SEND_HISTORY_NOW = 0
                                daily_report_start_time = now_time
                                recent_trade_logs = [y for x, y in config.TRADE_ALL_LOG.items() if x > beg]
                                if recent_trade_logs:
                                    recent_trade_logs.sort()
                                    daily_msg = u"火币量化交易系统运行中:\n用户昵称:{}\n币种:{}\n最近{}小时共交易{}次, 记录如下:\n".format(config.NICK_NAME, config.NEED_TOBE_SUB_SYMBOL[0].upper(), interval, len(recent_trade_logs))+"\n\n".join(recent_trade_logs)
                                else:
                                    daily_msg = u"火币量化交易系统运行中:\n用户昵称:{}\n币种:{}\n最近{}小时无交易记录！\n".format(config.NICK_NAME, config.NEED_TOBE_SUB_SYMBOL[0].upper(), interval)

                                log_config.output2ui(daily_msg, 8)
                                logger.warning(daily_msg)
                                log_config.notify_user(daily_msg, own=True)
                        if not hour_report_start_time:
                            hour_report_start_time = now_time
                        else:
                            if (now_time-hour_report_start_time).total_seconds() > config.ACCOUNT_REPORT_INTERVAL*3600 or config.SEND_ACCOUNT_NOW:
                                hour_report_start_time = now_time
                                config.SEND_ACCOUNT_NOW = 0

                                global CURRENT_PRICE
                                bal0, bal0_f, bal1, bal1_f = strategies.update_balance()
                                total = (bal0+bal0_f)*CURRENT_PRICE+bal1+bal1_f
                                chicang = ((bal0 + bal0_f) * CURRENT_PRICE) / total
                                dapan_profit = round((CURRENT_PRICE - process.ORG_PRICE) * 100 / process.ORG_PRICE, 3)
                                account_profit = round((total - process.ORG_DOLLAR_TOTAL) * 100 / process.ORG_DOLLAR_TOTAL, 3)
                                is_win = u"是" if account_profit >= dapan_profit else u"否"
                                msg_own = u"""火币量化交易系统运行中:\n用户昵称:{}\n币种:{}\n用户风险承受力:{}\n启动时间:{}\n当前时间:{}\n初始价格:{}\n当前价格:{}\n初始持币量:可用{},冻结{},仓位{}%\n当前持币量:可用{},冻结{},仓位{}%\n初始时持金量:可用{},冻结{}\n初始持金量:可用{},冻结{}\n初始账户总价值:${}\n当前账户总价值:${}\n大盘涨跌幅:{}%\n当前账户涨跌幅:{}%\n当前盈利：{}$\n是否跑羸大盘:{}""".format(
                                    config.NICK_NAME, config.NEED_TOBE_SUB_SYMBOL[0].upper(), config.RISK,
                                    process.START_TIME.strftime("%Y/%m/%d, %H:%M:%S"),
                                    now_time.strftime("%Y/%m/%d, %H:%M:%S"), round(process.ORG_PRICE, 6),
                                    round(CURRENT_PRICE, 6),
                                    round(process.ORG_COIN_TRADE, 4), round(process.ORG_COIN_FROZEN, 4),
                                    round(process.ORG_CHICANG * 100, 2), round(bal0, 4), round(bal0_f, 4), round(chicang * 100, 2),
                                    round(process.ORG_DOLLAR_TRADE, 2), round(process.ORG_DOLLAR_FROZEN, 2), round(bal1, 2), round(bal1_f, 2),
                                    round(process.ORG_DOLLAR_TOTAL, 2), round(total, 2), dapan_profit, account_profit, round(total - process.ORG_DOLLAR_TOTAL, 2), is_win)

                                msg_other = u"火币量化交易系统运行中:\n用户昵称:{}\n币种:{}\n用户风险承受力:{}\n启动时间:{}\n当前时间:{}\n初始价格:{}\n当前价格:{}\n初始持币量:可用{},冻结{},仓位{}%\n当前持币量:可用{},冻结{},仓位{}%\n初始持金量:可用{},冻结{}\n当前持金量:可用{},冻结{}\n初始账户总资产:{}$\n当前账户总资产:${}\n大盘涨跌幅:{}%\n当前账户涨跌幅:{}%\n当前盈利：{}$\n是否跑羸大盘:{}"\
                                    .format(config.NICK_NAME, config.NEED_TOBE_SUB_SYMBOL[0].upper(), config.RISK,
                                        process.START_TIME.strftime("%Y/%m/%d, %H:%M:%S"),
                                        now_time.strftime("%Y/%m/%d, %H:%M:%S"),
                                        round(process.ORG_PRICE, 6), round(CURRENT_PRICE, 6),
                                        "***", "***", round(process.ORG_CHICANG * 100, 2), "***", "***", round(chicang * 100, 2),
                                        "***", "***", "***", "***",
                                        "***", "***",
                                        dapan_profit,
                                        account_profit,"***",
                                        is_win)
                                log_config.output2ui(msg_own, level=8)
                                logger.warning(msg_own)
                                ret1 = log_config.notify_user(msg_own, own=True)
                                ret2 = log_config.notify_user(msg_other)
                    except Exception as e:
                        logger.warning("notify_profit_info exception.e={}".format(e))

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
                config.SUB_LEFT = self._user_info.get("trade_left", None)
                config.SUB_RIGHT = self._user_info.get("trade_right", None)

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
            self._user_info.get("trade_left", None),
            self._user_info.get("access_key", None),
            self._user_info.get("secret_key", None),
            self._user_info.get("ws_site", "BR"),
            self._user_info.get("rest_site", "BR"),
            3,))
        th.setDaemon(True)
        th.start()
        self.gress_bar_verify_user.start(text="Verifying user identity, please wait a moment...")

    def verify_huobi(self, access_key):
        retry = 3
        status_code = 0
        error_info = ""
        try:
            while retry >= 0:
                time.sleep(1)
                host = "47.75.10.215"
                ret = requests.get("http://{}:5000/huobi/{}".format(host, access_key))
                if ret.status_code == 200:
                    self.verify = True
                    logger.info(u"系统授权认证成功！ 过期时间: {}".format(ret.text))
                    return True, u"系统授权认证成功！ 过期时间: {}".format(ret.text)
                else:
                    #201-invalid, 202-does not exist, 203-expired, 204-exception
                    if ret.status_code == 204:
                        retry -= 1
                        status_code = 204
                        error_info = ret.text
                        logger.error("verify_huobi, server exception 204")
                        continue
                    elif ret.status_code == 203:
                        logger.error("verify_huobi expired. status code={}, text={}".format(ret.status_code, ret.text))
                        msg = u"您的系统授权截止: {} 已过期, 无法继续使用本系统, 如需继续授权使用, 请提供您的AccessKey:\n{}\n给系统管理员进行续费！ \n联系方式:15691820861(可加微信)!".format(ret.text, access_key)
                        self.verify = False
                        return False, msg
                    else:
                        logger.error("verify_huobi failed. status code={}, text={}".format(ret.status_code, ret.text))
                        msg = u"系统授权认证失败, 错误码: {}.\n无法继续使用本系统, 请确认您输入的账户信息正确无误! 如需授权使用, 请提供您的AccessKey:\n{}\n给系统管理员以开通使用权限！ \n联系方式:15691820861(可加微信)!".format(ret.status_code, access_key)
                        self.verify = False
                        return False, msg
        except Exception as e:
            status_code = -1
            error_info = str(e)
            error_info = error_info.replace(host, "47.77.13.207")
            error_info = error_info.replace("5000", "1009")
            logger.error("verify_huobi e={}".format(error_info))

        self.verify = False
        return False, u"系统授权认证检查失败, 暂时无法使用本系统, 错误码：{},错误信息:{}.\n请检查您的网络情况, 稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!".format(status_code, error_info)

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
        self.nick_name_text.set(config.NICK_NAME)

        access_key = self._user_info.get("access_key", "")
        log_config.output2ui(u"正在进行权限验证, 请稍等...", 8)
        ret = self.verify_huobi(access_key)
        if ret[0]:
            logger.info(u"认证成功, key={}".format(access_key))
            log_config.output2ui(ret[1], 8)
        else:
            logger.error(u"授权认证失败, key={}".format(access_key))
            log_config.output2ui(ret[1], 5)
            messagebox.showerror("Error", ret[1])  # 提出警告对话窗
            return

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
            print("需要扫码登录微信网页版或在你的手机上确认登录！")
            wechat_helper.login_wechat()

        from popup_system import PopupSystem
        value_dict = {"is_email": config.EMAIL_NOTIFY, "is_wechat": config.WECHAT_NOTIFY, "is_alarm": config.ALARM_NOTIFY, "is_alarm_trade": config.ALARM_TRADE_DEFAULT,
                      "trade_min": config.TRADE_MIN_LIMIT_VALUE, "alarm_time": config.ALARM_TIME,
                      "trade_max": config.TRADE_MAX_LIMIT_VALUE, "wait_buy_price": config.WAIT_BUY_PRICE,
                      "wait_buy_account": config.WAIT_BUY_ACCOUNT, "wait_sell_price":config.WAIT_SELL_PRICE, "wait_sell_account":config.WAIT_SELL_ACCOUNT,
                      "risk": config.RISK, "emails": config.EMAILS, "wechats": config.WECHATS, "position_low": config.LIMIT_MIN_POSITION,
                      "force_position_low": config.FORCE_POSITION_MIN, "position_high": config.LIMIT_MAX_POSITION,
                      "force_position_high": config.FORCE_POSITION_MAX,"trade_history_report_interval": config.TRADE_HISTORY_REPORT_INTERVAL,
                      "account_report_interval": config.ACCOUNT_REPORT_INTERVAL, "emails_vip": config.EMAILS_VIP, "wechats_vip": config.WECHATS_VIP,
                      "nick_name": config.NICK_NAME}

        pop = PopupSystem(value_dict)
        self.root.wait_window(pop)
        if pop.is_ok:
            config.EMAIL_NOTIFY = value_dict["is_email"]
            config.WECHAT_NOTIFY = value_dict["is_wechat"]
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

            config.LIMIT_MIN_POSITION = value_dict["position_low"]
            config.FORCE_POSITION_MIN = value_dict["force_position_low"]

            config.LIMIT_MAX_POSITION = value_dict["position_high"]
            config.FORCE_POSITION_MAX = value_dict["force_position_high"]

            config.TRADE_HISTORY_REPORT_INTERVAL = value_dict["trade_history_report_interval"]
            config.ACCOUNT_REPORT_INTERVAL = value_dict["account_report_interval"]
            config.NICK_NAME = value_dict["nick_name"]
            self.nick_name_text.set(config.NICK_NAME)

            emails = value_dict.get("emails", "").strip().split("\n")
            wechats = value_dict.get("wechats", "").strip().split("\n")

            emails_vip = value_dict.get("emails_vip", "").strip().split("\n")
            wechats_vip = value_dict.get("wechats_vip", "").strip().split("\n")

            log_config.output2ui("system config:\n{}！".format(value_dict))
            login_wechat_now = value_dict.get("login_wechat_now", 0)
            config.EMAILS = []
            for email in emails:
                if email and len(email) > 5 and "@" in email:
                    config.EMAILS.append(email)

            config.WECHATS = []
            for wechat in wechats:
                if wechat and len(wechat) > 2:
                    config.WECHATS.append(wechat)

            config.EMAILS_VIP = []
            for email in emails_vip:
                if email and len(email) > 5 and "@" in email:
                    config.EMAILS_VIP.append(email)

            config.WECHATS_VIP = []
            for wechat in wechats_vip:
                if wechat and len(wechat) > 2:
                    config.WECHATS_VIP.append(wechat)

            # if (config.EMAIL_NOTIFY and (config.WECHATS or config.WECHATS_VIP)) or login_wechat_now:
            if login_wechat_now or config.EMAIL_NOTIFY:
                log_config.output2ui(u"请用您的手机微信扫码登录微信网页版或在您的手机上确认登录！否则您可能无法收到实时交易信息", 8)
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
    my_gui.center_window(1350, 620)
    root.maxsize(1350, 620)
    # root.minsize(320, 240)
    # root.iconbitmap('spider_128px_1169260_easyicon.net.ico')
    my_gui.update_ui()
    # my_gui.init_history_asyn()
    root.mainloop()
    logger.info("==========over================")
