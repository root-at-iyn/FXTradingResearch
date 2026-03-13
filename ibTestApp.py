from ibapi.client import *
from ibapi.wrapper import *
import datetime
import time
import threading

port = 4002


class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: OrderId):
        self.orderId = orderId
    
    def nextId(self):
        self.orderId += 1
        return self.orderId
    
    def error(self, reqId, errorTime, errorCode, errorString, advancedOrderReject=""):
        print(f"reqId: {reqId}, errorTime: {errorTime}, errorCode: {errorCode}, errorString: {errorString}, orderReject: {advancedOrderReject}")
    
    def headTimestamp(self, reqId, headTimeStamp):
        print(headTimeStamp)
        print(datetime.datetime.fromtimestamp(int(headTimeStamp)))
        self.cancelHeadTimeStamp(reqId)


app = TestApp()
app.connect("127.0.0.1", port, 0)
threading.Thread(target=app.run).start()
time.sleep(1)

mycontract = Contract()
mycontract.symbol = "GBP"
mycontract.secType = "CASH"
mycontract.exchange = "IDEALPRO"
mycontract.currency = "USD"

app.reqHeadTimeStamp(app.nextId(), mycontract, "MIDPOINT", 1, 2)