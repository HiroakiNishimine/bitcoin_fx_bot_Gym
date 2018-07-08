# coding=utf-8
import ccxt, time, datetime

Symbol = 'BTC/USD'
symbol = 'XBTUSD'

Lot = 10000
Bid = 0.0
Ask = 0.0
PositionCount = 0
BuyCount = 0
SellCount = 0
PendingCount = 0
BUY_LotAmount = 0.0
SELL_LotAmount = 0.0
Balance = 0.0
Profit = 0.0
Equity = 0.0
Balance_BTC = 0.0
Profit_BTC = 0.0
Equity_BTC = 0.0

def bitmex():
  
  bitmex = ccxt.bitmex({

      #APIキーをご自分のものに差し替えてください
       'apiKey': 'RsJtux8sro3BloRYnrFYSK5G',
       'secret': 'jL4J5PUeGt99xMMuXD0VWwZ9LMVjm0-FfUMRb_mX6HLaR32E',

      })
  
#   bitmex.urls['api'] = bitmex.urls['test'] #テスト用 本番口座の場合は不要
  
  return bitmex

#API
def getJson(label, flg_getJsonError):
   
   try:
       if label == 'ticker':
           return bitmex().fetch_ticker(Symbol), flg_getJsonError

       elif label == 'markets':
           return bitmex().fetch_markets(), flg_getJsonError

       elif label == 'balance':
           return bitmex().fetch_balance(), flg_getJsonError

       elif label == "position":
           return bitmex().private_get_position(), flg_getJsonError

       elif label == "pending":
           return bitmex().fetch_open_orders(Symbol), flg_getJsonError
       
       elif label == "orderbook":
           return bitmex().fetch_order_book(Symbol, limit=10000), flg_getJsonError

       else:
           return None
           
   except Exception as e:
       print(str(TimeCurrent()), " Exception => Get Json: ", label, str(e))
       flg_getJsonError = flg_getJsonError + 1
       return None, flg_getJsonError

#Price
def getPrice(json_obj, label):
   
   try:
       if(json_obj != None):
           
           if   label == 'symbol':
               return json_obj['symbol']

           elif label == 'timestamp':
               return json_obj['timestamp']
           
           elif label == 'bid':
               return json_obj['bid']
           
           elif label == 'ask':
               return json_obj['ask']

           elif label == 'last':
               return json_obj['last']

           elif label == 'open':
               return json_obj['open']

           elif label == 'close':
               return json_obj['close']
           
           else:
               return float(0.0)

       else:
           return float(0.0)

   except Exception as e:
       print(str(TimeCurrent()), " Exception => Get Price: ", label, str(e))

#Balance
def getBalance(json_obj, label):
   
   try:
       if(json_obj != None):
           
           if label == "walletBalance":
               return json_obj['info'][0]['walletBalance']

           elif label == "marginBalance":
               return json_obj['info'][0]['marginBalance']

           elif label == "unrealisedPnl":
               return json_obj['info'][0]['unrealisedPnl']

           else:
               return float(0.0)

       else:
           return float(0.0)

   except  Exception as e:
       print(str(TimeCurrent()), " Exception => Get Balance: ", label, str(e))

   else:
       return 0

#ポジショ数取得   
def getPositions(json_obj, Symbol, label):
    
   try:
       position = json_obj
       pLen = []

       if(label == "BUY"):
       
           for i , p in enumerate(position):
               if(position[i]['symbol'] == Symbol and position[i]['currentQty'] > 0):
                   pLen.append(i)

       elif (label == "SELL"):
       
           for i , p in enumerate(position):
               if(position[i]['symbol'] == Symbol and position[i]['currentQty'] < 0):
                   pLen.append(i)
   
       Len = len(pLen)
       pLen.clear()
       return Len

   except Exception as e:
       print(str(TimeCurrent()), " Exception => getPositions: ", label, str(e))
       return 0

#ポジションのロット数取得     
def getPositionQuantity(json_obj, Symbol, label):
    
   try:
       position = json_obj
       Buy_amount = []
       Sell_amount = []

       if(label == "BUY"):
       
           for i , p in enumerate(position):
               if(position[i]['symbol'] == Symbol and position[i]['currentQty'] > 0):
                   lotamount = position[i]['currentQty']
                   Buy_amount.append(lotamount)

       elif (label == "SELL"):
       
           for i , p in enumerate(position):
               if(position[i]['symbol'] == Symbol and position[i]['currentQty'] < 0):
                   temp_amount = position[i]['currentQty']
                   if(temp_amount < 0):
                       lotamount = temp_amount*-1
                       Sell_amount.append(lotamount)
                       
                   
       if (len(Buy_amount) > 0):
           BUY_Lot = sum(Buy_amount)
           Buy_amount.clear()
           return BUY_Lot

       elif (len(Sell_amount) > 0):
           SELL_Lot = sum(Sell_amount)
           Sell_amount.clear()
           return SELL_Lot
       
       return 0

   except Exception as e:
       print(str(TimeCurrent()), " Exception => Get Position Quantity: ", label, str(e))
       return 0

#注文の数を取得
def getPendingOrdersCount(json_obj, Symbol):
     
   try:
       orders = json_obj
       oLen = []
       Len=0

       for i , o in enumerate(orders):
           if(orders[i]['info']['symbol'] == Symbol):
               oLen.append(i)

       Len = len(oLen)
       oLen.clear()
       return Len

   except Exception as e:
       print(str(TimeCurrent()), " Exception => Get Pending Orders Count: ", str(e))
       return 0
       

#ポジション情報
def AccountPositions(obj_Posi, obj_Pending):
   
   global BuyCount, SellCount, PositionCount, PendingCount, BUY_LotAmount, SELL_LotAmount

   BuyCount = getPositions(obj_Posi, symbol, "BUY")
   SellCount = getPositions(obj_Posi, symbol, "SELL")
   PendingCount = getPendingOrdersCount(obj_Pending, symbol)
   BUY_LotAmount = getPositionQuantity(obj_Posi, symbol, "BUY")
   SELL_LotAmount = getPositionQuantity(obj_Posi, symbol, "SELL")
   
   PositionCount = BuyCount + SellCount

#口座情報取得
def AccountInfo(obj_balance, bid):
   
   global Balance_BTC, Profit_BTC, Equity_BTC, Profit, Balance, Equity

   walletBalance = getBalance(obj_balance, 'walletBalance')
   marginBalance = getBalance(obj_balance, 'marginBalance')
   unrealisedPnl = getBalance(obj_balance, 'unrealisedPnl')

   f_walletBalance = float(walletBalance)
   Balance_BTC = f_walletBalance*0.00000001

   f_marginBalance = float(marginBalance)
   Equity_BTC = f_marginBalance*0.00000001

   f_unrealisedPnl = float(unrealisedPnl)
   Profit_BTC = f_unrealisedPnl*0.00000001

   Balance = Balance_BTC*bid
   Equity = Equity_BTC*bid
   Profit = Profit_BTC*bid

#発注
def NewOrder(Order_Symbol, Order_Type, Order_Side, Amount, Price):
    try:
        print("amount : {}".format(Amount))
        # Amount USD分、Price USDで購入 or 売却 
        res = bitmex().create_order(Order_Symbol, type=Order_Type, side=Order_Side, amount=Amount, price=Price)
        return res

    except Exception as e:
        print(TimeCurrent(), " Exception => NewOrder: ", str(e))
        return 0


#オーダーのキャンセル
def CancelPendingOrders(obj_Pending, Symbol):
     
   try:
        
       if(len(obj_Pending) > 0):
           
           for i , o in enumerate(obj_Pending):
               
               if(obj_Pending[i]['info']['symbol'] == Symbol):
                   
                   getid = obj_Pending[i]['info']['orderID']
                   
                   res = bitmex().cancel_order(getid)
                   
                   print(TimeCurrent(), " Cancel Pending Orders => Expired: id ", getid)

                   if(res != None):
                       status = res['status']
                       cId = res['id']
                       
                       print(TimeCurrent(), " Cancel Pending Orders => Success | Status: ", status, " Id: ", cId)
                           
                   else:
                       pass
                   
   except Exception as e:
       print(TimeCurrent(), " Exception => CancelPendingOrders: ", str(e))

  

#Order Response
def OrderResponse(Response):
   
   if(Response != None):
       res = Response
       timestamp = res['info']['timestamp']
       symbol = res['info']['symbol']
       side = res['info']['side']
       ordType = res['info']['ordType']
       orderQty = res['info']['orderQty']
       price = res['info']['price']
       orderID = res['info']['orderID']

       Info = "{0} | {1} | Side: {2} | OrdType: {3} | Size: {4} | Price: {5} | Id: {6}".format(
       timestamp, symbol, side, ordType, str(orderQty), str(price), str(orderID)
       )
       print(str(TimeCurrent()) + " Success " + side + " Order => " + Info)
       return True

   else:
       print(str(TimeCurrent()) + " Can not Get Order Response")
       return False
       

#NowTime
def TimeCurrent():
   now = datetime.datetime.now()
   return now


if __name__ == '__main__':
    date = datetime.datetime.now()
    openOrder = bitmex().fetch_orders(
        symbol='BTC/USD', since='2014/01/02 03:04:05', limit=500)
    closeOrder = bitmex().fetch_closed_orders(
        symbol='BTC/USD', since=None, limit=500)
    print(openOrder)
