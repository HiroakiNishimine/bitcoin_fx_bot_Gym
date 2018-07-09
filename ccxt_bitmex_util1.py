# coding=utf-8
import simplejson as json
from statistics import stdev
from pprint import pprint
from ccxt_bitmex_util2 import *
import numpy as np
import datetime
from time import sleep

# global variables
start_total_XBT = 0.0
step = 0

#Tickerの取得
#ticker = bitmex().fetch_ticker('BTC/USD')

#口座情報の取得
#balance = bitmex().fetch_balance()

#ポジションの取得
# position = bitmex().private_get_position()

#注文の取得
#open_orders = bitmex().fetch_open_orders()

#注文のキャンセル
# cancel = bitmex().cancel_order('orderID')

def cancel_Orders():
    # getJsonErrorフラグの初期化
    flg_getJsonError = 0
    obj_Pending, flg_getJsonError = getJson(
        'pending', flg_getJsonError)
    sleep(1)
    if flg_getJsonError == 0:
        CancelPendingOrders(obj_Pending, Symbol='BTC/USD')

def order_Buy(symbol='BTC/USD', type='limit', side='buy', amount=6.0, price=10000):
    order_info = NewOrder(symbol, type, side, amount, price)
    print("order info 【buy】: {}".format(order_info))

def order_Sell(symbol='BTC/USD', type='limit', side='sell', amount=6.0, price=10000):
    order_info = NewOrder(symbol, type, side, amount, price)
    print("order info 【sell】: {}".format(order_info))

def get_State():
    global start_total_XBT
    timestamp = 0

    # getJsonErrorフラグの初期化
    flg_getJsonError = 0

    # #JSON取得
    obj_Ticker, flg_getJsonError = getJson(
        'ticker', flg_getJsonError)
    sleep(1)
    obj_Markets, flg_getJsonError = getJson(
        'markets', flg_getJsonError)
    sleep(1)
    obj_Balance, flg_getJsonError = getJson(
        'balance', flg_getJsonError)
    sleep(1)
    obj_Position, flg_getJsonError = getJson(
        'position', flg_getJsonError)
    sleep(1)
    obj_Pending, flg_getJsonError = getJson(
        'pending', flg_getJsonError)
    sleep(1)
    obj_Orderbook, flg_getJsonError = getJson(
        'orderbook', flg_getJsonError)
    sleep(1)

    if flg_getJsonError == 0:
        # ポジション情報の取得
        # BuyCount = getPositions(obj_Position, 'XBTUSD', "BUY")
        # sleep(1)
        # SellCount = getPositions(obj_Position, 'XBTUSD', "SELL")
        # sleep(1)
        #ポジション情報取得
        BuyCount, SellCount, PositionCount, PendingCount, BUY_LotAmount, SELL_LotAmount = AccountPositions(
            obj_Position, obj_Pending)

        # obj_Balanceからとれる情報取得
        free_XBT = obj_Balance['BTC']['free'] # free XBT
        used_XBT = obj_Balance['BTC']['used'] # used XBT
        total_XBT = obj_Balance['BTC']['total'] # total XBT

        # obj_Tickerからとれる情報取得
        open = obj_Ticker['info']['open']
        high = obj_Ticker['info']['high']
        low = obj_Ticker['info']['low']
        close = obj_Ticker['info']['close']
        trades = obj_Ticker['info']['trades']
        volume = obj_Ticker['info']['volume']
        vwap = obj_Ticker['info']['vwap']
        lastSize = obj_Ticker['info']['lastSize']
        turnover = obj_Ticker['info']['turnover']
        homeNotional = obj_Ticker['info']['homeNotional']
        timestamp = obj_Ticker['timestamp']
        last = obj_Ticker['last']
        change = obj_Ticker['change']
        percentage = obj_Ticker['percentage']
        average = obj_Ticker['average']

        # obj_Orderbookからとれる情報
        # Ask # Bid
        Ask_price = obj_Orderbook['asks'][0][0]
        Ask_amount = obj_Orderbook['asks'][0][1]
        Bid_price = obj_Orderbook['bids'][0][0]
        Bid_amount = obj_Orderbook['bids'][0][1]

        # http://www.geisya.or.jp/~mwm48961/electro/histogram2.htm
        # 板情報のaskの平均
        asks2d = np.array(obj_Orderbook['asks'])
        f = asks2d[:, 1:]
        f = np.reshape(f, (-1,))
        Orderbook_asks_mean = np.sum(np.prod(asks2d, axis=1)) / np.sum(f)
        # 板情報のaskの分散
        n = np.sum(f)
        m = asks2d[:,0]
        m = np.reshape(m, (-1,))
        m2 = np.square(m)
        Orderbook_asks_variance = ( sum(m2*f) / n ) - np.square(Orderbook_asks_mean)
        # 板情報のaskの標準偏差
        Orderbook_asks_std = np.sqrt(Orderbook_asks_variance)

        # 板情報のbidsの平均
        bids2d = np.array(obj_Orderbook['bids'])
        f = bids2d[:, 1:]
        f = np.reshape(f, (-1,))
        Orderbook_bids_mean = np.sum(np.prod(bids2d, axis=1)) / np.sum(f)
        # 板情報のaskの分散
        n = np.sum(f)
        m = bids2d[:,0]
        m = np.reshape(m, (-1,))
        m2 = np.square(m)
        Orderbook_bids_variance = ( sum(m2*f) / n ) - np.square(Orderbook_bids_mean)
        # 板情報のaskの標準偏差
        Orderbook_bids_std = np.sqrt(Orderbook_bids_variance)
    
    else:
        free_XBT = 0
        used_XBT = 0
        total_XBT = start_total_XBT
        Ask_price = 0
        Ask_amount = 0
        Bid_price = 0
        Bid_amount = 0
        open, high, low, close, trades, volume, vwap, lastSize = 0, 0, 0, 0, 0, 0, 0, 0
        turnover, homeNotional, timestamp, last, change, percentage, average = 0, 0, 0, 0, 0, 0, 0
        Orderbook_asks_mean, Orderbook_asks_variance, Orderbook_asks_std, Orderbook_bids_mean, Orderbook_bids_variance, Orderbook_bids_std = 0, 0, 0, 0, 0, 0
        BuyCount, SellCount = 0, 0
        PendingCount, BUY_LotAmount, SELL_LotAmount = 0, 0, 0

    # time情報
    date = datetime.datetime.now()

    state = (free_XBT, used_XBT, total_XBT, Ask_price, Ask_amount, Bid_price, Bid_amount, date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond, date.weekday(), open, high, low, close, trades, volume, vwap, lastSize,
             turnover, homeNotional, timestamp, last, change, percentage, average, Orderbook_asks_mean, Orderbook_asks_variance, Orderbook_asks_std, Orderbook_bids_mean, Orderbook_bids_variance, Orderbook_bids_std, BuyCount, SellCount, PendingCount, BUY_LotAmount, SELL_LotAmount,flg_getJsonError, 0,0,0,0,0,0)
    
    print("state : {}".format(state))

    return state


#    #Buy Order
#    if(tickCounts == 3):

#        if(BuyCount==0 and SellCount==0 and PendingCount==0):

#            orderPrice = Bid

#            #Buy Execution
#            res = NewOrder(Symbol,'limit','buy', Lot, orderPrice)

#            print(TimeCurrent(), " IN => Order Request: Buy Order")
#            time.sleep(15)

#            result = OrderResponse(res) #発注結果の取得

#            if(result == True):
#                print(TimeCurrent(), " IN / BUY: True") #発注成功

#            else:
#                print(TimeCurrent(), " IN / BUY: Flse") #発注失敗


#    #Sell Order
#    if(tickCounts == 10):

#        if(BuyCount==0 and SellCount==0 and PendingCount==0):

#            orderPrice = Ask

#            #Sell Execution
#            res = NewOrder(Symbol,'limit','sell', Lot, orderPrice)

#            print(TimeCurrent(), " IN => Order Request: Buy Order")
#            time.sleep(15)

#            result = OrderResponse(res) #発注結果の取得

#            if(result == True):
#                print(TimeCurrent(), " IN / SELL: True") #発注成功

#            else:
#                print(TimeCurrent(), " IN / SELL: Flse") #発注失敗


#    #Cancel Order
#    if(tickCounts == 8 or tickCounts == 15):

#        if(PendingCount > 0):
#            CancelPendingOrders(obj_Pending, symbol)


if __name__ == '__main__':

    obs = get_State()
    # cancel_Orders()

    print(obs)
