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
prev_reward = 0.0
step = 0
total_step = 0
flg_BuyFinishedError = 0
flg_SellFinishedError = 0
WithdrawCnt = 0                 # withdrawを行った回数

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
        global start_total_XBT, step, total_step, WithdrawCnt
        global flg_BuyFinishedError, flg_SellFinishedError

        step = step + 1
        total_step = total_step + 1
        Bid_price, Ask_price, BuyCount, SellCount, BUY_LotAmount, SELL_LotAmount, flg_getJsonError, PendingCount = get_State_forAction()

        if flg_getJsonError == 0:
            self._take_action(action, Bid_price, Ask_price, BuyCount,
                            SellCount, BUY_LotAmount, SELL_LotAmount, PendingCount)
                 
        self.status = 1
        observation = get_State(flg_BuyFinishedError, flg_SellFinishedError, WithdrawCnt)
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
                    symbol='BTC/USD', type='limit', side='buy', amount=20.0, price=Bid_price)
                flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))

        elif action == 1:
            print("action == stay")

        elif action == 2:
            print("action == sell")
            if flg_SellFinishedError == 0:
                flg_SellFinishedError = order_Sell(
                    symbol='BTC/USD', type='limit', side='sell', amount=20.0, price=Ask_price)
                flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))
        
        elif action == 3:
            print("action == buy +")
            if flg_BuyFinishedError == 0:
                flg_BuyFinishedError = order_Buy(
                    symbol='BTC/USD', type='limit', side='buy', amount=20.0, price=Bid_price+0.5)
                flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))
        
        elif action == 4:
            print("action == buy -")
            if flg_BuyFinishedError == 0:
                flg_BuyFinishedError = order_Buy(
                    symbol='BTC/USD', type='limit', side='buy', amount=20.0, price=Bid_price-0.5)
                flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))

        elif action == 5:
            print("action == sell +")
            if flg_SellFinishedError == 0:
                flg_SellFinishedError = order_Sell(
                    symbol='BTC/USD', type='limit', side='sell', amount=20.0, price=Ask_price+0.5)
                flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))

        elif action == 6:
            print("action == sell -")
            if flg_SellFinishedError == 0:
                flg_SellFinishedError = order_Sell(
                    symbol='BTC/USD', type='limit', side='sell', amount=20.0, price=Ask_price-0.5)
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
            print("action == sell all")
            if flg_SellFinishedError == 0:
                if BuyCount:
                    flg_SellFinishedError = order_Sell(symbol='BTC/USD', type='limit', side='sell',
                            amount=BUY_LotAmount, price=Ask_price)
                    flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))
            
        elif action == 9:
            print("action == sell all +")
            if flg_SellFinishedError == 0:
                if BuyCount:
                    flg_SellFinishedError = order_Sell(symbol='BTC/USD', type='limit', side='sell',
                            amount=BUY_LotAmount, price=Ask_price+0.5)
                    flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))

        elif action == 10:
            print("action == sell all -")
            if flg_SellFinishedError == 0:
                if BuyCount:
                    flg_SellFinishedError = order_Sell(symbol='BTC/USD', type='limit', side='sell',
                            amount=BUY_LotAmount, price=Ask_price-0.5)
                    flg_BuyFinishedError = 0
            else:
                print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))
        
        elif action == 11:
            print("action == buy all")
            if flg_BuyFinishedError == 0:
                if SellCount:
                    flg_BuyFinishedError = order_Buy(symbol='BTC/USD', type='limit', side='buy',
                            amount=SELL_LotAmount, price=Bid_price)
                    flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))

        elif action == 12:
            print("action == buy all +")
            if flg_BuyFinishedError == 0:
                if SellCount:
                    flg_BuyFinishedError = order_Buy(symbol='BTC/USD', type='limit', side='buy',
                            amount=SELL_LotAmount, price=Bid_price+0.5)
                    flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))

        elif action == 13:
            print("action == buy all -")
            if flg_BuyFinishedError == 0:
                if SellCount:
                    flg_BuyFinishedError = order_Buy(symbol='BTC/USD', type='limit', side='buy',
                            amount=SELL_LotAmount, price=Bid_price-0.5)
                    flg_SellFinishedError = 0
            else:
                print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))
    

    def _get_reward(self, observation, step, flg_getJsonError):
        global start_total_XBT, prev_reward, WithdrawCnt
        global flg_BuyFinishedError, flg_SellFinishedError

        free_XBT = observation[0] # observation[0] : free XBT
        total_XBT = observation[2] # observation[2] : total XBT
        # total XBTがstart時点より増えると報酬、減ると罰
        reward = (total_XBT - start_total_XBT)* 700000 # rewardが円とほぼ同じになる。
        if reward < 0: # マイナス方向には6倍の罰を与える
            reward = 6 * reward
        if WithdrawCnt > 1:
            reward = reward + (WithdrawCnt * 3000)  # 引き出した回数分のある程度の報酬（3000円分くらい？）を与える

        if flg_getJsonError >= 1:
            reward = prev_reward
        else:
            prev_reward = reward
        print("【{0}step, {1}total_step, total XBT : {2}, reward : {3}(円), {4} XBT】".format(
            step, total_step, observation[2], reward, (observation[2] - start_total_XBT)))

        date = datetime.datetime.now()
        with open('csv/ccxt_bitmex_log_2018_07_20.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time', date, 'total XBT', observation[2], 'reward',reward])
        
        
        # 状況確認
        Bid_price, Ask_price, BuyCount, SellCount, BUY_LotAmount, SELL_LotAmount, flg_getJsonError, PendingCount = get_State_forAction()
        # オーダーが50件を超えていたら一旦全部のオーダーをキャンセルする
        if PendingCount > 40:
            print("オーダーが４０件を超えているので一旦全部のオーダーをキャンセルします。")
            cancel_Orders()

        # 利益が0.0002XBT以上でていたら、その利益分だけ出金する
        if total_XBT > 0.0095:
            if free_XBT < 0.002:
                #一旦精算
                print("free XBTは0.002以下なので一旦精算します。")
                if flg_BuyFinishedError == 0:
                    if SellCount:
                        print("action == buy all +")
                        flg_BuyFinishedError = order_Buy(symbol='BTC/USD', type='limit', side='buy',
                                amount=SELL_LotAmount, price=Bid_price+0.5)
                        flg_SellFinishedError = 0
                else:
                    print("flg_BuyFinishedError is {}. We can't buy anymore!".format(flg_BuyFinishedError))

                if flg_SellFinishedError == 0:
                    if BuyCount:
                        print("action == sell all -")
                        flg_SellFinishedError = order_Sell(symbol='BTC/USD', type='limit', side='sell',
                                amount=BUY_LotAmount, price=Ask_price-0.5)
                        flg_BuyFinishedError = 0
                else:
                    print("flg_SellFinishedError is {}. We can't sell anymore!".format(flg_SellFinishedError))
            else:
                print("free XBTは0.002以上あるので精算はせずに出金します。")

            # 一時待機
            sleep(15)
            # 精算状態を確認
            observation = get_State(flg_BuyFinishedError, flg_SellFinishedError, WithdrawCnt)
            free_XBT = observation[0] # observation[0] : free XBT
            if free_XBT > 0.002:
                # 出金
                withdrawXBT()
                reward = reward + 3000 # 1400円ほど引き出すので、ある程度の報酬（3000円分くらい？）を与える
                WithdrawCnt = WithdrawCnt + 1
                print("出金申請しました。")
            else:
                print("精算状態を確認しましたが、free XBTが0.002以下なので出金を中止します。")
                print("BuyCount:{0}, SellCount:{1}, BUY_LotAmount:{2}, SELL_LotAmount:{3}, flg_getJsonError:{4}, PendingCount:{5}".format(BuyCount, SellCount, BUY_LotAmount, SELL_LotAmount, flg_getJsonError, PendingCount))

        return reward

    def reset(self):
        global start_total_XBT, step, WithdrawCnt
        global flg_BuyFinishedError, flg_SellFinishedError

        step = 0
        self.state = get_State(flg_BuyFinishedError, flg_SellFinishedError, WithdrawCnt)
        start_total_XBT = self.state[2]
        print("start_total_XBT : {}".format(start_total_XBT))

        with open('csv/ccxt_bitmex_log_2018_07_20.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['start_total_XBT', start_total_XBT])

        return np.array(self.state)

    def render(self, mode='human', close=False):
        pass

    def close(self):
        pass
