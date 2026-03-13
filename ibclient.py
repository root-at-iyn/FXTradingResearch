from ibapi.client import EClient, Contract ,ClientException
from ibapi.wrapper import EWrapper, OrderId
import threading
import datetime
import time
import pandas as pd

class IBClient(EClient, EWrapper):
    """
    Implements the EClient and EWrapper interface.
    Defines methods to handle data received back from IBKR.
    """
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
        self.earliest_timestamp = None
        self.isHistoricalDataEnded = False

    def nextValidId(self, orderId: OrderId):
        self.orderId = orderId
    
    def nextId(self):
        self.orderId += 1
        return self.orderId
    
    def error(self, reqId, errorTime, errorCode, errorString, advancedOrderReject=""):
        print(reqId, errorTime, errorCode, errorString, advancedOrderReject)
    
    def historicalData(self, reqId, bar):
        date = datetime.datetime.fromtimestamp(int(bar.date)).isoformat()
        self.data.append([
            date, 
            bar.open, 
            bar.high, 
            bar.low, 
            bar.close,
            bar.volume, 
            bar.wap, 
            bar.barCount
        ])
    
    def historicalDataEnd(self, reqId, start, end):
        print(f"Historical Data Ended for {reqId}. Started at {start}, ending at {end}")
        self.isHistoricalDataEnded = True
        self.cancelHistoricalData(reqId)

    def headTimestamp(self, reqId, headTimeStamp):
        self.earliest_timestamp = int(headTimeStamp)
        self.cancelHeadTimeStamp(reqId)
      

app = IBClient()
HOST = "127.0.0.1"
PORT = 4002
CLIENT_ID = 0
try:
    print("Connecting to IBKR ...")
    app.connect(HOST, PORT, CLIENT_ID)
    print(f"Connected: {HOST}:{PORT}:{CLIENT_ID}")
    threading.Thread(target=app.run).start()
    time.sleep(1)
except ClientException as e:
    print(e)

mycontract = Contract()
mycontract.symbol = "GBP"
mycontract.secType = "CASH"
mycontract.exchange = "IDEALPRO"
mycontract.currency = "USD"

app.reqHeadTimeStamp(app.nextId(), mycontract, "MIDPOINT", 1, 2)
time.sleep(1)
app.reqHistoricalData(
    app.nextId(), 
    mycontract, 
    "20260311 17:00:00 US/Eastern", 
    "1 Y", 
    "15 mins", 
    "MIDPOINT", 
    1, 
    2, 
    False, 
    [])
sleep = 0
while app.isHistoricalDataEnded is False:
    sleep += 1
    if sleep == 60:
        print(f"Time exceeded!: {sleep}")
        break
    time.sleep(sleep)

df = pd.DataFrame(app.data)
df.columns = ['Date', 'Open', 'High', 'Low', 'Close','Volume','WAP','BarCount']
df.set_index('Date', inplace=True)
print(df)
df.to_csv('GBPUSD_15mins_1yr_End_20260311.csv')