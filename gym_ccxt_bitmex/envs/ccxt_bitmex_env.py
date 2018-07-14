# coding=utf-8
import os, subprocess, time, signal
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding
import numpy as np
import math
from ccxt_bitmex_util1 import get_State, get_State_forAction, order_Buy, order_Sell, cancel_Orders
import datetime

import logging
import csv
logger = logging.getLogger(__name__)

# global variables
start_total_XBT = 0.0
prev_reward = 0.0
step = 0
total_step = 0

class CcxtBitmexEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': ['human']}

    def __init__(self):

        self.action_space = spaces.Discrete(14)
        self.observation_space = spaces.Box(low=-float('inf'), high=float('inf'), shape=(58,))

        self.status = None
        self.seed()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        global start_total_XBT
        global step, total_step

        step = step + 1
        total_step = total_step + 1
        Bid_price, Ask_price, BuyCount, SellCount, BUY_LotAmount, SELL_LotAmount, flg_getJsonError = get_State_forAction()

        if flg_getJsonError == 0:
            self._take_action(action, Bid_price, Ask_price, BuyCount,
                            SellCount, BUY_LotAmount, SELL_LotAmount)
                 
        self.status = 1
        observation = get_State()
        flg_getJsonError = observation[41]
        reward = self._get_reward(observation, step, flg_getJsonError)

        # if observation[0] <= (start_total_XBT / 1.4):
        #     episode_over = True
        # else:
        #     episode_over = False
        episode_over = False

        return observation, reward, episode_over, {}

    def _take_action(self, action, Bid_price, Ask_price, BuyCount, SellCount, BUY_LotAmount, SELL_LotAmount):
        print("")
        if action == 0:
            print("action == buy")
            flg_getJsonError = order_Buy(
                symbol='BTC/USD', type='limit', side='buy', amount=20.0, price=Bid_price)

        elif action == 1:
            print("action == stay")

        elif action == 2:
            print("action == sell")
            flg_getJsonError = order_Sell(
                symbol='BTC/USD', type='limit', side='sell', amount=20.0, price=Ask_price)
        
        elif action == 3:
            print("action == buy +")
            flg_getJsonError = order_Buy(
                symbol='BTC/USD', type='limit', side='buy', amount=20.0, price=Bid_price+0.5)
        
        elif action == 4:
            print("action == buy -")
            flg_getJsonError = order_Buy(
                symbol='BTC/USD', type='limit', side='buy', amount=20.0, price=Bid_price-0.5)

        elif action == 5:
            print("action == sell +")
            flg_getJsonError = order_Sell(
                symbol='BTC/USD', type='limit', side='sell', amount=20.0, price=Ask_price+0.5)

        elif action == 6:
            print("action == sell -")
            flg_getJsonError = order_Sell(
                symbol='BTC/USD', type='limit', side='sell', amount=20.0, price=Ask_price-0.5)
        
        elif action == 7:
            print("action == cancel orders")
            cancel_Orders()
       
        elif action == 8:
            print("action == sell all")
            if BuyCount:
                flg_getJsonError = order_Sell(symbol='BTC/USD', type='limit', side='sell',
                           amount=BUY_LotAmount, price=Ask_price)
        
        elif action == 9:
            print("action == sell all +")
            if BuyCount:
                flg_getJsonError = order_Sell(symbol='BTC/USD', type='limit', side='sell',
                           amount=BUY_LotAmount, price=Ask_price+0.5)

        elif action == 10:
            print("action == sell all -")
            if BuyCount:
                flg_getJsonError = order_Sell(symbol='BTC/USD', type='limit', side='sell',
                           amount=BUY_LotAmount, price=Ask_price-0.5)
        
        elif action == 11:
            print("action == buy all")
            if SellCount:
                flg_getJsonError = order_Buy(symbol='BTC/USD', type='limit', side='buy',
                          amount=SELL_LotAmount, price=Bid_price)

        elif action == 12:
            print("action == buy all +")
            if SellCount:
                flg_getJsonError = order_Buy(symbol='BTC/USD', type='limit', side='buy',
                          amount=SELL_LotAmount, price=Bid_price+0.5)

        elif action == 13:
            print("action == buy all -")
            if SellCount:
                flg_getJsonError = order_Buy(symbol='BTC/USD', type='limit', side='buy',
                          amount=SELL_LotAmount, price=Bid_price-0.5)

    def _get_reward(self, observation, step, flg_getJsonError):
        global start_total_XBT, prev_reward
        # free XBTがstart時点より増えると報酬、減ると罰
        reward = (observation[2] - start_total_XBT)* 700000 # observation[2] : total XBT, rewardが円とほぼ同じになる。
        if flg_getJsonError >= 1:
            reward = prev_reward
        else:
            prev_reward = reward
        print("【{0}step, {1}total_step, total XBT : {2}, reward : {3}(円), {4} XBT】".format(
            step, total_step, observation[2], reward, (observation[2] - start_total_XBT)))

        date = datetime.datetime.now()
        with open('csv/ccxt_bitmex_log_2018_07_15.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time', date, 'total XBT', observation[2], 'reward',reward])
        
        return reward

    def reset(self):
        global start_total_XBT
        global step

        step = 0
        self.state = get_State()
        start_total_XBT = self.state[2]
        print("start_total_XBT : {}".format(start_total_XBT))

        with open('csv/ccxt_bitmex_log_2018_07_15.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['start_total_XBT', start_total_XBT])

        return np.array(self.state)

    def render(self, mode='human', close=False):
        pass

    def close(self):
        pass
