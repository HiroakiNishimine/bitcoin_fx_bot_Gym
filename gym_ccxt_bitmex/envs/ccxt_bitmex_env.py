# coding=utf-8
import os, subprocess, time, signal
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding
import numpy as np
import math
from ccxt_bitmex_util1 import get_State, order_Buy, order_Sell
import datetime

import logging
import csv
logger = logging.getLogger(__name__)

# global variables
start_total_XBT = 0.0
step = 0

class CcxtBitmexEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': ['human']}

    def __init__(self):

        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(low=-float('inf'), high=float('inf'), shape=(39,))

        self.status = None
        self.seed()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        global start_total_XBT
        global step

        step = step + 1
        observation = get_State()
        Bid_price, Ask_price = observation[5], observation[3]
        self._take_action(action, Bid_price, Ask_price)
        self.status = 1
        observation = get_State()
        reward = self._get_reward(observation, step)

        if observation[0] <= (start_total_XBT / 1.1):
            episode_over = True
        else:
            episode_over = False

        return observation, reward, episode_over, {}

    def _take_action(self, action, Bid_price, Ask_price):
        if action == 0:
            print("action == buy")
            order_Buy(symbol='BTC/USD', type='limit', side='buy', amount=5.0, price= Bid_price)

        elif action == 1:
            print("action == stay")

        elif action == 2:
            print("action == sell")
            order_Sell(symbol='BTC/USD', type='limit', side='sell', amount=5.0, price=Ask_price)
        
        elif action == 3:
            print("action == buy +")
            order_Buy(symbol='BTC/USD', type='limit', side='buy', amount=5.0, price=Bid_price+0.5)
        
        elif action == 4:
            print("action == buy -")
            order_Buy(symbol='BTC/USD', type='limit', side='buy', amount=5.0, price=Bid_price-0.5)

        elif action == 5:
            print("action == sell +")
            order_Buy(symbol='BTC/USD', type='limit', side='sell', amount=5.0, price=Ask_price+0.5)

        elif action == 6:
            print("action == sell -")
            order_Buy(symbol='BTC/USD', type='limit', side='sell', amount=5.0, price=Ask_price-0.5)


    def _get_reward(self, observation, step):
        global start_total_XBT
        # free XBTがstart時点より増えると報酬、減ると罰
        reward = (observation[2] - start_total_XBT)* 1000000 # observation[2] : total XBT
        print("{0}step, free XBT : {1}, reward : {2}".format(step, observation[2], reward))

        date = datetime.datetime.now()
        with open('ccxt_bitmex_log_2018_07_06.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time', date, 'free XBT', observation[0], 'reward',reward])

        return reward

    def reset(self):
        # self.state = self.np_random.uniform(low=-0.05, high=0.05, size=(39,))
        global start_total_XBT
        self.state = get_State()
        start_total_XBT = self.state[0]
        print("start_total_XBT : {}".format(start_total_XBT))

        with open('ccxt_bitmex_log_2018_07_07.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['start_total_XBT', start_total_XBT])

        return np.array(self.state)

    def render(self, mode='human', close=False):
        pass

    def close(self):
        pass
