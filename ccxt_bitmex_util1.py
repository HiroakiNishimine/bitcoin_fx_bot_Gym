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

        # Markets情報
        turnover24h = obj_Markets[43]['info']['turnover24h']
        impactBidPrice = obj_Markets[43]['info']['impactBidPrice']
        impactAskPrice = obj_Markets[43]['info']['impactAskPrice']
        volume24h = obj_Markets[43]['info']['volume24h']

        #ポジション情報取得
        BuyCount, SellCount, PositionCount, PendingCount, BUY_LotAmount, SELL_LotAmount = AccountPositions(
            obj_Position, obj_Pending)
        if PendingCount >= 1:
            PendingPrice = obj_Pending[0]['price']

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

        Ask_price, Ask_amount, Bid_price, Bid_amount, Orderbook_asks_mean, Orderbook_asks_variance, Orderbook_asks_std, Orderbook_bids_mean, Orderbook_bids_variance, Orderbook_bids_std = get_order_info(
            obj_Orderbook)
    
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
        turnover24h, impactBidPrice, impactAskPrice, volume24h = 0,0,0,0
        PendingPrice = 0

    # time情報
    date = datetime.datetime.now()

    state = (free_XBT, used_XBT, total_XBT, Ask_price, Ask_amount, Bid_price, Bid_amount, date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond, date.weekday(), open, high, low, close, trades, volume, vwap, lastSize,
             turnover, homeNotional, timestamp, last, change, percentage, average, Orderbook_asks_mean, Orderbook_asks_variance, Orderbook_asks_std, Orderbook_bids_mean, Orderbook_bids_variance, Orderbook_bids_std, BuyCount, SellCount, PendingCount, BUY_LotAmount, SELL_LotAmount, flg_getJsonError, turnover24h, impactBidPrice, impactAskPrice, volume24h, PendingPrice, 0)
    
    print("state : free_XBT:{0}, used_XBT:{1}, total_XBT:{2}, Ask_price:{3}, Ask_amount:{4}, Bid_price:{5}, Bid_amount:{6}, date.year:{7}, date.month:{8}, date.day:{9}, date.hour:{10}, date.minute:{11}, date.second:{12}, date.microsecond:{13}, date.weekday():{14}, open:{15}, high:{16}, low:{17}, close:{18}, trades:{19}, volume:{20}, vwap:{21}, lastSize:{22}, turnover: {23}, homeNotional: {24}, timestamp: {25}, last: {26}, change: {27}, percentage: {28}, average: {29}, Orderbook_asks_mean: {30}, Orderbook_asks_variance: {31}, Orderbook_asks_std: {32}, Orderbook_bids_mean: {33}, Orderbook_bids_variance: {34}, Orderbook_bids_std: {35}, BuyCount: {36}, SellCount: {37}, PendingCount: {38}, BUY_LotAmount: {39}, SELL_LotAmount: {40}, flg_getJsonError: {41}, turnover24h: {42}, impactBidPrice: {43}, impactAskPrice: {44}, volume24h: {45}, PendingPrice: {46}, NONE: {47}".format(
        state[0], state[1], state[2], state[3], state[4], state[5], state[6], state[7], state[8], state[9], state[10], state[11], state[12], state[13], state[14], state[15], state[16], state[17], state[18], state[19], state[20], state[21], state[22], state[23], state[24], state[25], state[26], state[27], state[28], state[29], state[30], state[31], state[32], state[33], state[34], state[35], state[36], state[37], state[38], state[39], state[40], state[41], state[42], state[43], state[44], state[45], state[46], state[47]))

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
