#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Charles on 2018/6/18
# Function:
import time
from datetime import datetime, timedelta
from tkinter import Tk, Label, Button, StringVar, END, messagebox
from tkinter.scrolledtext import ScrolledText
from queue import Queue
import logging
from threading import Thread
from requests import get
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
import webbrowser
logger = logging.getLogger(__name__)
CURRENT_PRICE = 1


class MainUI():
    def __init__(self, root):
        self.verify = True
        self.coin_trade = 0
        self.dollar_trade = 0
        self.notify_queue = Queue()
        self.gress_bar_init_history = GressBar()
        self.gress_bar_verify_user = GressBar()
        self.root = root
        self.top = None
        self._is_user_valid = False
        self._user_info = {}
        self._strategy_dict = {}
        root.title("火币量化交易系统v1.6.81　(官方微信交流群：火币量化交易官方交流群, QQ群:761222621, 管理员:15691820861)")
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
        self.notify_text = ScrolledText(root, width=20, height=15)
        self.notify_text.insert(END, u"欢迎使用火币量化交易系统, 程序开始工作后这里将显示实时操盘建议, 请您关注！ 如对本系统有任何意见或建议可加\n官方交流QQ群：\n761222621, \n联系管理员:\n15691820861 \n建议一经采纳将赠送30天的免费试用期.", "MSG")

        self.start_button = Button(root, text=u"开始工作", command=self.start_work, width=20)
        # self.start_button.pack()

        self.stop_button = Button(root, text=u"停止工作", command=self.stop_work, width=20)
        self.login_wechat_btn = Button(root, text=u"登录微信", command=self.login_wechat, width=20)
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
        self.label_origin = Label(root, text=u"初始价格/币对1/币对2/总价值: ", width=25)
        self.origin_text = StringVar()
        self.origin_text.set("")
        self.origin_label = Label(root, textvariable=self.origin_text, foreground='blue', background="gray",
                               font=("", 12, 'bold'), width=30)

        self.nick_name_text = StringVar()
        self.nick_name_text.set(config.NICK_NAME)
        self.nick_name_text_label = Label(root, textvariable=self.nick_name_text, foreground='blue', background="gray",
                               font=("", 12, 'bold'), width=10)

        self.run_status_text = StringVar()
        self.run_status_text.set(u"待验证")
        self.run_status_text_label = Label(root, textvariable=self.run_status_text, foreground='red', background="gray",
                               font=("", 10, 'bold'), width=15)


        self.label_now = Label(root, text=u"大盘涨跌幅/账户涨跌幅: ", width=22)
        self.now_text = StringVar()
        self.now_text.set("")
        self.now_label = Label(root, textvariable=self.now_text, foreground='blue', background="gray",
                               font=("", 12, 'bold'), width=30)

        self.label_run_log = Label(root, text=u"运行日志: ", width=10)
        self.log_text = ScrolledText(root, width=62, height=28)
        self.label_trade_log = Label(root, text=u"交易日志: ", width=10)
        self.trade_text = ScrolledText(root, width=62, height=28)
        # self.log_text.pack()
        # 创建一个TAG，其前景色为红色
        self.log_text.tag_config('BUY', foreground='green', background="#C1CDC1", font=("", 11, 'bold'))
        self.log_text.tag_config('SELL', foreground='red', background="#BC8F8F", font=("", 11, 'bold'))
        self.log_text.tag_config('WARNING', foreground='orange')
        self.log_text.tag_config('ERROR', foreground='red')
        self.log_text.tag_config('EXCEPTION', foreground='red')
        self.log_text.tag_config('CRITICAL', background="red")
        self.log_text.tag_config('SHOW', foreground='green', font=("", 11, 'bold'))
        self.log_text.tag_config('link', foreground='blue', underline=True, font=("", 10, 'bold'))
        self.log_text.see(END)

        self.trade_text.tag_config('BUY', foreground='green', background="orange", font=("", 11, 'bold'))
        self.trade_text.tag_config('SELL', foreground='red', background="orange", font=("", 11, 'bold'))
        self.log_text.see(END)

        self.notify_text.tag_config('MSG', foreground='blue', background="white", font=("", 11, 'normal'))

        self.verify_identity_button.grid(row=0, column=0)
        self.init_history_button.grid(row=1, column=0)
        self.system_setting_button.grid(row=2, column=0)
        self.strategy_setting_button.grid(row=3, column=0)
        self.start_button.grid(row=4, column=0)


        # self.register_button.grid(row=5, column=0)
        # self.start_check_strategy_button.grid(row=6, column=0)
        # self.clean_st_button.grid(row=7, column=0)
        # self.stop_check_strategy_button.grid(row=8, column=0)
        self.stop_button.grid(row=6, column=0)
        self.login_wechat_btn.grid(row=5, column=0)
        self.notify_text.grid(row=7, column=0, rowspan=3, columnspan=1)

        self.label_pop.grid(row=0, column=1)
        self.price_label.grid(row=0, column=2)

        self.label_origin.grid(row=0, column=3)
        self.origin_label.grid(row=0, column=4)
        self.nick_name_text_label.grid(row=1, column=5)
        self.run_status_text_label.grid(row=0, column=5)

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

        self.system_setting_button.config(state="disabled")
        self.strategy_setting_button.config(state="disabled")

        self.register_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        self.clean_st_button.config(state="disabled")
        self.stop_check_strategy_button.config(state="disabled")
        self.start_check_strategy_button.config(state="disabled")
        self.init_history_button.config(state="disabled")
        self.login_wechat_btn.config(state="disabled")

        self.working = False

    def show_hand_cursor(self, event):
        self.log_text.config(cursor='arrow')

    def show_arrow_cursor(self, event):
        self.log_text.config(cursor='xterm')

    def click(self, event, x):
        print(x)
        webbrowser.open(x)

    def handlerAdaptor(self, fun, **kwds):
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)


    def init_history_asyn(self):
        def init_history(hb):
            ret = self._hb.init()  # 这一步是必须的，先同步处理
            ret2 = hb.init_history()
            self.gress_bar_init_history.quit()
            if not (ret and ret2):
                logger.error("init service failed.")
                log_config.output2ui(u"系统初始化失败! 请检查网络状况并重试!", 3)
                messagebox.showwarning("Error", u"系统初始化失败! 请检查网络状况并重试!")
                self.run_status_text.set(u"初始化失败")
                return False
            log_config.output2ui(u"系统初始化成功!", 8)
            log_config.output2ui(u"第三步, 请点击[开始工作], 程序将开启自动化交易. 如需进行系统配置, 如风险偏好设置, 交易额度限制, 微信通知, 挂单买卖等, 请点击[系统设置]按钮, 如果需要自定义交易策略请点击[策略设置]按钮, 非专业人士不建议您对策略进行修改. 系统设置和策略设置的修改在程序运行过程当中立即生效, 不需要重新启动工作. ", 8)
            self.start_button.config(state="normal")
            self.register_button.config(state="normal")
            self.init_history_button.config(state="disabled")
            self.run_status_text.set(u"初始化成功")

        huobi.save_history_trade_vol(config.NEED_TOBE_SUB_SYMBOL)
        if not self._hb:
            self._hb = Huobi()
        th = Thread(target=init_history, args=(self._hb,))
        th.setDaemon(True)
        th.start()
        self.gress_bar_init_history.start()
        return True

    def start_work(self):
        def start(hb):
            logger.info("start work!!")
            # log_config.output2ui(u"系统启动中...", 1)
            log_config.output2ui(u"系统开始工作，将为您智能发现最佳交易时机并进行自动交易!", 8)
            log_config.output2ui(u"点击 [停止工作] 可停止程序自动交易．", 8)
            self.run_status_text.set(u"工作中")
            hb.run()
            logger.info("work over!!")

        if not self.verify:
            log_config.output2ui(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!", 5)
            messagebox.showerror(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!")
            self.run_status_text.set(u"待授权")
            return

        strategies.trade_advise_update()

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

        self.register_strategy()
        self.start_check_strategy()

        th = Thread(target=start, args=(self._hb,))
        th.setDaemon(True)
        th.start()
        self.stop_button.config(state="normal")
        self.start_button.config(state="disabled")
        self.start_check_strategy_button.config(state="normal")
        self.verify_identity_button.config(state="disabled")
        self.working = True

    def login_wechat_aycn(self):
        ret = wechat_helper.login_wechat()
        log_config.output2ui(u"登录微信成功, 实时交易信息和账号周期统计信息将通过微信发送给您的[文件传输助手]．", 8)

    def login_wechat(self):
        log_config.output2ui(u"\n稍后可能需要您使用手机微信扫码登录或者需要您在手机上确认登录！否则您可能无法收到实时交易信息, 不过您也可以在火币APP中查看历史交易记录．", 8)
        self.first_login = False
        th = Thread(target=self.login_wechat_aycn)
        th.setDaemon(True)
        th.start()


    def stop_work(self):
        logger.info("stop_work!")
        if self._hb:
            self._hb.exit()

        self.clean_strategy()
        self.stop_check_strategy()

        self.stop_button.config(state="disabled")
        self.start_button.config(state="normal")
        self.register_button.config(state="normal")
        self.start_check_strategy_button.config(state="disabled")
        # self.strategy_setting_button.config(state="disabled")
        # self.verify_identity_button.config(state="normal")
        # self.init_history_button.config(state="normal")
        self.verify_identity_button.config(state="normal")
        # self.login_wechat_btn.config(state="disabled")

        # log_config.output2ui("Stop work successfully!", 8)

        log_config.output2ui(u"系统已停止工作!", 8)
        self.run_status_text.set(u"已停止")
        self.working = False

    def start_check_strategy(self):
        if not self.verify:
            log_config.output2ui(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!", 5)
            return

        # 策略检测线程启动
        logger.info("start_check_strategy...")
        log_config.output2ui(u"正在加载策略...")
        self._strategy_pool.start_work()
        self.start_check_strategy_button.config(state="disabled")
        self.stop_check_strategy_button.config(state="normal")
        log_config.output2ui(u"加载策略成功", 8)

    def stop_check_strategy(self):
        logger.info("stop_check_strategy...")
        log_config.output2ui(u"正在停止执行策略...", 8)
        self._strategy_pool.stop_work()
        self.start_check_strategy_button.config(state="normal")
        self.stop_check_strategy_button.config(state="disabled")
        log_config.output2ui(u"停止执行策略成功!", 8)

    def register_strategy(self):
        if not self.verify:
            log_config.output2ui(u"授权认证检查失败, 系统暂时无法使用, 请稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!", 5)
            return

        logger.info("register_strategy.")
        log_config.output2ui(u"正在注册策略...")
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
        log_config.output2ui(u"正在清空所有策略...", 8)
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
            # logger.info("wait_buy_sell not be trigger!, price={}, working={}".format(price, self.working))
            return False

        buy_prices = config.WAIT_BUY_PRICE
        buy_amounts = config.WAIT_BUY_ACCOUNT
        sell_prices = config.WAIT_SELL_PRICE
        sell_amounts = config.WAIT_SELL_ACCOUNT

        symbol = config.NEED_TOBE_SUB_SYMBOL[0]
        for i, buy_price in enumerate(buy_prices):
            # 循环遍历挂单买
            buy_amount = buy_amounts[i]
            if buy_price > 0 and buy_amount > config.TRADE_MIN_LIMIT_VALUE*1.02 and self.dollar_trade>config.TRADE_MIN_LIMIT_VALUE*1.02:
                if price <= buy_price:
                    if buy_amounts > self.dollar_trade:
                        buy_amount = self.dollar_trade

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
            if sell_price > 0 and sell_amount > 0.0001 and self.coin_trade>0.0001 and sell_amount*price>config.TRADE_MIN_LIMIT_VALUE*1.02 and self.coin_trade*price>config.TRADE_MIN_LIMIT_VALUE*1.02:
                if price >= sell_price:
                    if sell_amount > self.coin_trade:
                        sell_amount = self.coin_trade

                    ret = strategies.sell_market(symbol, amount=sell_amount, record=False, current_price=price)
                    if ret[0]:
                        msg = u"挂单卖出{}: 挂单价格={}, 挂单个数={}个, 实际价格={}, 实际挂单卖出个数={}个.".format(symbol,
                                sell_price, sell_amount, price, ret[1])
                        success = False
                        if ret[0] == 1:
                            msg += u"-交易成功！"
                            config.WAIT_SELL_ACCOUNT[i] = sell_amount - ret[1]
                            success = True
                        elif ret[0] == 2:
                            msg += u"-交易被取消, 取消原因: {}!".format(ret[2])
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
                self.coin_trade = coin_trade

                dollar_trade = float(dollar_str[0])
                self.dollar_trade = dollar_trade
                dollar_frozen = float(dollar_str[1])
                total_coin_value = coin_trade + coin_frozen + (dollar_trade + dollar_frozen) / price

                total_dollar_value = (coin_trade + coin_frozen) * price + dollar_trade + dollar_frozen
                if total_dollar_value>0:
                    position = (coin_trade + coin_frozen)*price / total_dollar_value
                else:
                    position = 0
                self.coin_text.set("{}/{}/{}%".format(round(total_coin_value, 4), round(total_dollar_value, 2), round(position*100, 2)))
                if not process.ORG_COIN_TOTAL:
                    process.START_TIME = datetime.now()
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
                process.CURRENT_TOTAL_DOLLAR_VALUE = total_dollar_value
                process.CURRENT_TOTAL_COIN_VALUE = total_coin_value
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
        logger.info("Welcome to Huobi Trade System")
        log_config.output2ui(u"------------欢迎使用火币量化交易系统！------------\n　 本系统由资深量化交易专家和算法团队倾力打造，对接火币官方接口，经过长达两年的不断测试与优化，"
                             u"本地化运行，更加安全可控，策略可定制，使用更方便!　\n   系统结合历史与实时数据进行分析，加上内置的多套专业策略组合算法，根据您的仓位、策略定制因"
                             u"子和风险接受能力等的不同，智能发现属于您的最佳交易时机进行自动化交易，并可以设置邮件和微信提醒，"
                             u"真正帮您实现24小时实时盯盘，专业可靠，稳定盈利！\n", 8)
        log_config.output2ui(
            u"免责声明:\n  1. 使用本系统时，系统将会根据程序判断自动帮您进行交易，因此产生的盈利或亏损均由您个人负责，与系统开发团队无关\n  2. 本系统需要您提供您在火币官网申请的API密钥，获取火币官方授权后方能正常运行，本系统承诺不会上传您的密钥到火币平台以外的地址，请您妥善保管好自己的密钥，发生丢失造成的财产损失与本系统无关\n  3. 因操作失误，断网，断电，程序异常等因素造成的经济损失与系统开发团队无关\n  4.如需商业合作，充值或使用过程中如有任何问题可加QQ群：761222621 进行交流，或与售后团队联系，联系方式: 15691820861\n",
            8)
        log_config.output2ui(u"------------使用步骤如下:", 8)
        log_config.output2ui(u"第一步，请点击 [身份验证] 然后在弹出框中输入您在火币官网申请的API密钥，选择您想自动化交易的币种，进行授权认证！", 8)


        def update_price(price_text):
            while 1:
                try:
                    time.sleep(1)
                    if not self.verify:
                        continue
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
            while 1:
                try:
                    time.sleep(5)
                    if not self.verify:
                        continue
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
                                # log_text.configure(state='disabled')
                    else:
                        time.sleep(1)
                except Exception as e:
                    logger.exception("update_ui_log exception....")
                    log_config.output2ui("update_ui_log exception....", 3)
                    continue

        def update_kdj(kdj_text):
            while 1:
                try:
                    time.sleep(5)
                    if not self.verify:
                        continue
                    kdj_15min = process.REALTIME_KDJ_15MIN #.get(block=True)
                    if not kdj_15min:
                        kdj_text.set("")
                    else:
                        # kdj_5min = process.REALTIME_KDJ_5MIN.get(block=True)
                        kdj_text.set("{}/{}/{}".format(round(kdj_15min[0], 2), round(kdj_15min[1], 2), round(kdj_15min[2], 2)))
                except Exception as e:
                    logger.exception("update_kdj exception....")
                    log_config.output2ui("update_kdj exception....", 3)

        def update_advise():
            while 1:
                try:
                    time.sleep(15)
                    if not self.verify:
                        continue
                    if process.REALTIME_ADVISE:
                        # self.notify_text.set(u"[操盘建议]:\n"+process.REALTIME_ADVISE[0]+"\n"+process.REALTIME_ADVISE[1])
                        # self.notify_text.
                        msg = u"[操盘建议]:\n" + process.REALTIME_ADVISE[0] + "\n" + process.REALTIME_ADVISE[1] + u"\n程序将为您持续选择最佳交易时机！"
                        self.notify_text.delete(1.0, END)
                        self.notify_text.insert(END, msg, "MSG")
                        # self.notify_text.insert(END, u"[操盘建议]:\n" + process.REALTIME_ADVISE[0] + "\n" + process.REALTIME_ADVISE[1], "MSG")

                        # log_config.output2ui(u"[操盘建议]:", 8)
                        # log_config.output2ui(process.REALTIME_ADVISE[0], 8)
                        # log_config.output2ui(process.REALTIME_ADVISE[1], 8)

                    if process.REALTIME_SYSTEM_NOTIFY:
                        msg = u"------------[管理员通知]----------\n{}".format(process.REALTIME_SYSTEM_NOTIFY)
                        log_config.output2ui(msg, 6)
                        log_config.notify_user(msg, own=True)
                except Exception as e:
                    logger.exception("update_advise exception....")

        def update_uml(uml_text):
            while 1:
                try:
                    time.sleep(5)
                    if not self.verify:
                        continue
                    global CURRENT_PRICE
                    uml = process.REALTIME_UML#.get(block=True)
                    if not uml:
                        uml_text.set("")
                        continue
                    diff1 = uml[0] - uml[1]
                    diff2 = uml[1] - uml[2]
                    # uml_text.set("{}/{}/{}-{}/{}-{}/{}".format(round(uml[0], 6), round(uml[1], 6), round(uml[2], 6), round(diff1, 6), round(diff2, 6), round(diff1 / CURRENT_PRICE, 5), round(diff2 / CURRENT_PRICE, 5)))
                    uml_text.set("{}/{}/{}".format(round(uml[0], 6), round(uml[1], 6), round(uml[2], 6)))

                    if process.LAST_VERIFY_TIME:
                        if (datetime.now() - process.LAST_VERIFY_TIME).total_seconds() > 3600*24:
                            ret = self.verify_huobi(config.ACCESS_KEY)
                            if not ret[0]:
                                self.clean_strategy()
                                self.stop_check_strategy()
                                self.stop_work()
                                time.sleep(2)
                                log_config.output2ui(ret[1], 5)
                                messagebox.showwarning("Error", ret[1])
                            else:
                                process.LAST_VERIFY_TIME = datetime.now()

                    else:
                        process.LAST_VERIFY_TIME = datetime.now()
                except Exception as e:
                    logger.exception("update_uml exception....")
                    log_config.output2ui("update_uml exception....", 3)

        def notify_profit_info():
            hour_report_start_time = None
            daily_report_start_time = None
            while 1:
                time.sleep(60)
                if self.working:
                    try:
                        if not self.verify:
                            continue
                        now_time = datetime.now()
                        if not daily_report_start_time:
                            daily_report_start_time = now_time
                        else:
                            run_total_seconds = (now_time-daily_report_start_time).total_seconds()
                            logger.info("system run total seconds={}, trade_notify_interval={}".format(run_total_seconds, config.TRADE_HISTORY_REPORT_INTERVAL))
                            if (run_total_seconds > config.TRADE_HISTORY_REPORT_INTERVAL*3600) or config.SEND_HISTORY_NOW > 0:
                                logger.info("send history now...")
                                if config.SEND_HISTORY_NOW > 0:
                                    # 立即发送，　不影响周期发送逻辑
                                    beg = now_time-timedelta(hours=config.SEND_HISTORY_NOW)
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
                                logger.info("send account info now...")
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

        th = Thread(target=update_price, args=(self.price_text,))
        th.setDaemon(True)
        th.start()
        th = Thread(target=update_ui_log, args=(self.log_text, self.trade_text, ))
        th.setDaemon(True)
        th.start()
        th = Thread(target=update_balance, args=(self.bal_text,))
        th.setDaemon(True)
        th.start()

        th = Thread(target=update_uml, args=(self.uml_text,))
        th.setDaemon(True)
        th.start()

        th = Thread(target=update_kdj, args=(self.kdj_text,))
        th.setDaemon(True)
        th.start()

        th = Thread(target=update_advise)
        th.setDaemon(True)
        th.start()

        th = Thread(target=notify_profit_info)
        th.setDaemon(True)
        th.start()

        return True

    def close_window(self):
        # ans = askyesno("Warning", message="Are you sure to quit？")
        ans = askyesno("Warning", message=u"确认退出？")
        if ans:
            self.gress_bar_init_history.quit()
            self.gress_bar_verify_user.quit()
            self.clean_strategy()
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
                self.login_wechat_btn.config(state="normal")
                self.init_history_button.config(state="normal")
                self.start_button.config(state="normal")
                self.strategy_setting_button.config(state="normal")
                self.system_setting_button.config(state="normal")
                strategies.update_balance(is_first=True)
                self.nick_name_text.set(config.NICK_NAME)
                log_config.output2ui(u"火币API授权认证成功! 您选择的交易币种为: {}{}\n".format(config.SUB_LEFT.upper(), config.SUB_RIGHT.upper()), 8)
                log_config.output2ui(u"第二步，请点击 [系统初始化] 按钮，系统将开始初始化历史数据，以便进行更加精确的数据分析．", 8)
                self.run_status_text.set(u"验证成功, 待初始化")
            else:
                messagebox.showwarning("Error", u"火币API授权认证失败，请检查您的KEY是否在有效期，或者您申请API KEY时绑定了IP地址，但您当前电脑的公网IP发生了变化!")
                log_config.output2ui(u"火币API授权认证失败，请检查您的KEY是否在有效期，或者您申请API KEY时绑定了IP地址，但您当前电脑的公网IP发生了变化!", 3)

        th = Thread(target=verify_user_by_get_balance, args=(
            self._user_info.get("trade_left", None),
            self._user_info.get("access_key", None),
            self._user_info.get("secret_key", None),
            self._user_info.get("ws_site", "BR"),
            self._user_info.get("rest_site", "BR"),
            3,))
        th.setDaemon(True)
        th.start()
        # self.gress_bar_verify_user.start(text=u"Verifying user identity, please wait a moment...")
        self.gress_bar_verify_user.start(text=u"火币API授权认证中, 请稍等...")

    def verify_huobi(self, access_key):
        retry = 3
        status_code = 0
        error_info = ""
        try:
            while retry >= 0:
                host = "47.75.10.215"
                ret = get("http://{}:5000/huobi/{}".format(host, access_key), timeout=3)
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
                time.sleep(1)
        except Exception as e:
            status_code = -1
            error_info = str(e)
            error_info = error_info.replace(host, "47.77.13.207")
            error_info = error_info.replace("5000", "1009")
            logger.error("verify_huobi e={}".format(error_info))

        self.verify = False
        return False, u"系统授权认证检查失败, 暂时无法使用本系统, 错误码：{},错误信息:{}.\n请检查您的网络情况, 稍后重试或联系管理员处理!\n联系方式:15691820861(可加微信)!".format(status_code, error_info)

    def set_up_account(self):
        self.log_text.insert(
            END, u"  温馨提示：在身份验证弹出窗口中输入您的密钥后, 您可以点击[保存密钥]保存自己的密钥至本地文件中，以后进行身份验证时只需点击[导入密钥]即可．", "INFO")

        self.log_text.insert(END, u"\n\n  如果您还没有火币平台账号，请参考[火币平台用户指导书]，简单几步带您完成从注册到交易．\n\n  注册时使用我们的 [邀请注册链接] (邀请码 8jbg4)可免费获得本系统100天的试用时长.\n\n", "INFO")

        # self.log_text.insert(END, u"\n  https://www.huobi.de.com/topic/invited/?invite_code=8jbg4&from=groupmessage", "link")
        # self.log_text.insert(END, "\n   http://github.com/PythonAwesome/HuobiUserGuide/blob/master/README.md", "link")
        #
        # self.log_text.insert(END, "\n   如果您还没有API密钥，请登录火币官方网站，点击个人头像，进入API管理页面进行申请．官网地址: ", "INFO")
        # self.log_text.insert(END, "\n   https://www.huobi.co/zh-cn/", "link")

        self.log_text.see(END)

        url = ['https://www.huobi.de.com/topic/invited/?invite_code=8jbg4&from=groupmessage',
               'https://www.huobi.co/zh-cn/',
               'https://www.huobi.co/zh-cn/apikey/',
               'http://github.com/PythonAwesome/HuobiUserGuide/blob/master/README.md',
               'https://www.jianshu.com/p/c4c4e3325a28',
               'https://www.jianshu.com/p/de6b120cf8d7'
            ]
        name = [u'邀请注册链接', u'火币全球官方网站(火币APP下载也在这里)', u'火币API Key申请(开通授权和身份验证必需)', u'火币平台用户指导书', u"如何提高被动收入", u"本系统使用手册"]
        m = 0
        for each in name:
            self.log_text.tag_config(m, foreground='blue', underline=True)
            self.log_text.tag_bind(m, '<Enter>', self.show_hand_cursor)
            self.log_text.tag_bind(m, '<Leave>', self.show_arrow_cursor)
            self.log_text.insert(END, each + '\n\n', m)
            self.log_text.tag_bind(m, '<Button-1>', self.handlerAdaptor(self.click, x=url[m]))
            m += 1

        self.log_text.see(END)
        from popup_account import PopupAccountConfig
        pop = PopupAccountConfig(self._user_info, u"身份验证")
        self.root.wait_window(pop)
        if not self._user_info.get("ok", False):
            return

        logger.info("{}".format(self._user_info))
        # log_config.output2ui("{}".format(self._user_info))

        self.price_text.set("")
        self.bal_text.set("")
        self.coin_text.set("")

        access_key = self._user_info.get("access_key", "")
        # log_config.output2ui(u"正在进行权限验证, 请稍等...", 8)
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
        self.init_history_button.config(state="normal")

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
                            u"策略配置")
        self.root.wait_window(pop)
        print(strategies.kdj_buy_params)


    def set_up_system(self):
        def login_wechat():
            # log_config.output2ui(u"需要扫码登录微信网页版或在你的手机上确认登录！", 8)
            ret = wechat_helper.login_wechat()
            log_config.output2ui(u"登录微信成功, 实时交易信息和账号周期统计信息将通过微信发送给您的[文件传输助手]．", 8)


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

        pop = PopupSystem(value_dict, u"系统配置")
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
                log_config.output2ui(u"稍后可能需要您使用手机微信扫码登录或者需要您在手机上确认登录！否则您可能无法收到实时交易信息. 当然, 您也可以在火币APP中查看历史交易记录!", 8)
                self.first_login = False
                th = Thread(target=login_wechat)
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
