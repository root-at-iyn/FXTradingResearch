import time
import pandas as pd
from ib.client import IBClient
from ibapi.client import Contract
from pandas import DataFrame


BASE = "GBP"
QUOTE = "USD"
SYMBOL = BASE + QUOTE

mycontract = Contract()
mycontract.symbol = BASE
mycontract.secType = "CASH"
mycontract.exchange = "IDEALPRO"
mycontract.currency = QUOTE

app = IBClient()
app.ibapiConnect(HOST="127.0.0.1", PORT=7496, CLIENT_ID=1)

try:
    while True:
        app.reqRealTimeBars(3002, mycontract, 5, "MIDPOINT", 0, [])
        app.run()
except:
    print(f"Exiting RealTime {SYMBOL} Price Stream")
    app.cancelRealTimeBars(3002)