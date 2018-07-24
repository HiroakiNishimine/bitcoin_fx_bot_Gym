# coding=utf-8
import os, subprocess, time, signal
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding
import numpy as np
import math
from ccxt_bitmex_util1 import get_State, get_State_forAction, order_Buy, order_Sell, cancel_Orders
from ccxt_bitmex_util2 import withdrawXBT
import datetime
from time import sleep
import logging
import csv
logger = logging.getLogger(__name__)

# global variables
start_total_XBT = 0.0
start_free_XBT = 0.0
prev_reward = 0.0
step = 0
total_step = 0
flg_BuyFinishedError = 0
flg_SellFinishedError = 0
WithdrawCnt = 0                 # withdrawを行った回数

class CcxtBitmexEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': ['human']}

    def __init__(self):

        self.action_space = spaces.Discrete(12)
        self.observation_space = spaces.Box(low=-float('inf'), high=float('inf'), shape=(63,))
        self.reward_range = [0., 1000.]
        self.status = None
        self.seed()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        global start_total_XBT, start_free_XBT, step, total_step, WithdrawCnt
        global flg_BuyFinishedError, flg_SellFinishedError

        step = step + 1
        total_step = total_step + 1
        Bid_price, Ask_price, BuyCount, SellCount, BUY_LotAmount, SELL_LotAmount, flg_getJsonError, PendingCount = get_State_forAction()

        if flg_getJsonError == 0:
            self._take_action(action, Bid_price, Ask_price, BuyCount,
                            SellCount, BUY_LotAmount, SELL_LotAmount, PendingCount)
                 
        self.status = 1
        observation = get_State(flg_BuyFinishedError, flg_SellFinishedError, WithdrawCnt, start_total_XBT, start_free_XBT)
        flg_getJsonError = observation[41]
        reward = self._get_reward(observation, step, flg_getJsonError)

        # if observation[0] <= (start_total_XBT / 1.4):
        #     episode_over = True
        # else:
        #     episode_over = False
        episode_over = False

        return observation, reward, episode_over, {}

    def _take_action(self, action, Bid_price, Ask_price, BuyCount, SellCount, BUY_LotAmount, SELL_LotAmount, PendingCount):
        global flg_BuyFinishedError, flg_SellFinishedError

        print("")
        if action == 0:
            print("action == buy")
            if flg_BuyFinishedError == 0:
                flg_BuyFinishedError = order_Buy(
                    symbol='BTC/USD', type='limit', side='buy', amount=23.0, price=Bid_price)
                flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))

        elif action == 1:
            print("action == stay")

        elif action == 2:
            print("action == sell")
            if flg_SellFinishedError == 0:
                flg_SellFinishedError = order_Sell(
                    symbol='BTC/USD', type='limit', side='sell', amount=23.0, price=Ask_price)
                flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))
        
        elif action == 3:
            print("action == buy +")
            if flg_BuyFinishedError == 0:
                flg_BuyFinishedError = order_Buy(
                    symbol='BTC/USD', type='limit', side='buy', amount=23.0, price=Bid_price+0.5)
                flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))
        
        elif action == 4:
            print("action == buy market")
            if flg_BuyFinishedError == 0:
                flg_BuyFinishedError = order_Buy(
                    symbol='BTC/USD', type='market', side='buy', amount=23.0, price=None)
                flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))

        elif action == 5:
            print("action == sell market")
            if flg_SellFinishedError == 0:
                flg_SellFinishedError = order_Sell(
                    symbol='BTC/USD', type='market', side='sell', amount=23.0, price=None)
                flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))

        elif action == 6:
            print("action == sell -")
            if flg_SellFinishedError == 0:
                flg_SellFinishedError = order_Sell(
                    symbol='BTC/USD', type='limit', side='sell', amount=23.0, price=Ask_price-0.5)
                flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))
        
        elif action == 7:
            if PendingCount > 0:
                print("action == cancel orders")
                cancel_Orders()
            else:
                print("no cancel orders.")
       
        elif action == 8:
            print("action == sell all -")
            if flg_SellFinishedError == 0:
                if BuyCount:
                    flg_SellFinishedError = order_Sell(symbol='BTC/USD', type='limit', side='sell',
                            amount=BUY_LotAmount, price=Ask_price-0.5)
                    flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))
        
        elif action == 9:
            print("action == buy all +")
            if flg_BuyFinishedError == 0:
                if SellCount:
                    flg_BuyFinishedError = order_Buy(symbol='BTC/USD', type='limit', side='buy',
                            amount=SELL_LotAmount, price=Bid_price+0.5)
                    flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))

        elif action == 10:
            print("action == sell all market price")
            if flg_SellFinishedError == 0:
                if BuyCount:
                    flg_SellFinishedError = order_Sell(symbol='BTC/USD', type='market', side='sell',
                            amount=BUY_LotAmount, price=None)
                    flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))
        
        elif action == 11:
            print("action == buy all market price")
            if flg_BuyFinishedError == 0:
                if SellCount:
                    flg_BuyFinishedError = order_Buy(symbol='BTC/USD', type='market', side='buy',
                            amount=SELL_LotAmount, price=None)
                    flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))


    def _get_reward(self, observation, step, flg_getJsonError):
        global start_total_XBT, start_free_XBT, prev_reward, WithdrawCnt
        global flg_BuyFinishedError, flg_SellFinishedError

        free_XBT = observation[0] # observation[0] : free XBT
        total_XBT = observation[2] # observation[2] : total XBT
        liquidationPrice = observation[45] # observation[45] : liquidationPrice
        avgEntryPrice = observation[23] # observation[23] : avgEntryPrice
        # total XBTがstart時点より増えると報酬、減ると罰

        if total_XBT > start_total_XBT:
            reward = (total_XBT - start_total_XBT) * 700000

        if reward >= 1000:
            reward = 1000.0 # 上限は1000

        if flg_getJsonError >= 1:
            reward = prev_reward
        else:
            prev_reward = reward
        print("【{0}step, {1}total_step, total XBT : {2}, reward : {3}(円), {4} XBT】".format(
            step, total_step, observation[2], reward, (observation[2] - start_total_XBT)))

        date = datetime.datetime.now()
        with open('csv/ccxt_bitmex_log_2018_07_25.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time', date, 'total XBT', observation[2], 'reward',reward])
        
        return reward

    def reset(self):
        global start_total_XBT, start_free_XBT, step, WithdrawCnt
        global flg_BuyFinishedError, flg_SellFinishedError

        step = 0
        # 状況確認
        Bid_price, Ask_price, BuyCount, SellCount, BUY_LotAmount, SELL_LotAmount, flg_getJsonError, PendingCount = get_State_forAction()
        #一旦精算
        print("reset : 精算します")
        # まずオーダーキャンセル
        if PendingCount > 0:
                print("action == cancel orders")
                cancel_Orders()
        else:
            print("no cancel orders.")

        if flg_BuyFinishedError == 0:
            if SellCount:
                print("action == buy all +")
                flg_BuyFinishedError = order_Buy(symbol='BTC/USD', type='market', side='buy',
                        amount=SELL_LotAmount, price=None)
                flg_SellFinishedError = 0
                sleep(10) # 一時待機
        else:
            print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))

        if flg_SellFinishedError == 0:
            if BuyCount:
                print("action == sell all -")
                flg_SellFinishedError = order_Sell(symbol='BTC/USD', type='market', side='sell',
                        amount=BUY_LotAmount, price=None)
                flg_BuyFinishedError = 0
                sleep(10) # 一時待機
        else:
            print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))

        # 状況確認
        observation = get_State(flg_BuyFinishedError, flg_SellFinishedError, WithdrawCnt, start_total_XBT, start_free_XBT)
        free_XBT = observation[0] # observation[0] : free XBT
        total_XBT = observation[2] # observation[2] : total XBT

        # 利益が0.0002XBT以上でていたら、その利益分だけ出金する
        if total_XBT > 0.0095:
            if free_XBT > 0.0022:
                # 出金
                withdrawXBT()
                WithdrawCnt = WithdrawCnt + 1
                print("出金申請しました。")


        self.state = get_State(flg_BuyFinishedError, flg_SellFinishedError, WithdrawCnt, start_total_XBT, start_free_XBT)
        start_free_XBT = self.state[0]
        start_total_XBT = self.state[2]
        print("start_total_XBT : {}".format(start_total_XBT))
        print("start_free_XBT : {}".format(start_free_XBT))

        with open('csv/ccxt_bitmex_log_2018_07_25.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['start_total_XBT', start_total_XBT, 'start_free_XBT', start_free_XBT])

        return np.array(self.state)

    def render(self, mode='human', close=False):
        pass

    def close(self):
        pass
