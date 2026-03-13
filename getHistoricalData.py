import time
import pandas as pd
from ib.client import IBClient
from ibapi.client import Contract
from pandas import DataFrame

def waitForHistoricalData(app: IBClient):
    print("Waiting for data ...")
    t = time.time()
    s = 0
    while app.isHistoricalDataEnded is False:
        if s > 60:
            print(f"Time exceeded!: {s}")
            break
        elif app.error_codes[-1] == 162:
            print("Error 162: Check error msg for details...")
            break
        else:
            time.sleep(1)
            s = time.time() - t
            print(f"Time elapsed: {s}s")
    print(f"Received {len(app.data)} rows")
    return len(app.data)

def getFXHistoricalData(app: IBClient, fx_contract: Contract):
    """
    Request historical data from IBKR for the specified contract.
    Return a pandas data frame indexed by date.
    """
    time.sleep(1)
    app.reqHistoricalData(
        app.nextId(), 
        mycontract, 
        "20260312 17:00:00 US/Eastern", 
        "1 D", 
        "15 mins", 
        "MIDPOINT", 
        1, # Use RTH
        2, # Epoch time
        False, 
        [])
    dataLen = waitForHistoricalData(app)
    if dataLen > 0:
        df = pd.DataFrame(app.data)
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close','Volume','WAP','BarCount']
        df.set_index('Date', inplace=True)
        print(df)
        app.disconnect()
        return df
    else:
        print("No historical data returned!")
        app.disconnect()

def getEarliestDataTimestamp(app: IBClient, contract: Contract):
    return app.reqHeadTimeStamp(app.nextId(), contract, "MIDPOINT", 1, 2)


if __name__ == '__main__':
    mycontract = Contract()
    mycontract.symbol = "GBP"
    mycontract.secType = "CASH"
    mycontract.exchange = "IDEALPRO"
    mycontract.currency = "USD"
    
    app = IBClient()
    app.ibapiConnect()
    getFXHistoricalData(app, mycontract)
