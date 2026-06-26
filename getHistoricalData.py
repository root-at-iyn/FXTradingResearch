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
        if s > 180:
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

def getFXHistoricalData(
        app: IBClient, 
        fx_contract: Contract, 
        end_date_ts: str = "20260312 17:00:00 US/Eastern", 
        freq: str = "1 Y"
        ):
    """
    Request historical data from IBKR for the specified contract.
    Return a pandas data frame indexed by date.
    """
    time.sleep(1)
    app.reqHistoricalData(
        app.nextId(), 
        fx_contract, 
        end_date_ts, 
        freq, 
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
    app.reqHeadTimeStamp(app.nextId(), contract, "MIDPOINT", 1, 2)
    return app.earliest_timestamp


if __name__ == '__main__':

    PATH = "./output"
    BASE = "NZD"
    QUOTE = "USD"
    SYMBOL = BASE + QUOTE
    YEAR = "2026"
    FILE = f"{SYMBOL}_15mins_1yr_End_{YEAR}0311.csv"

    mycontract = Contract()
    mycontract.symbol = BASE
    mycontract.secType = "CASH"
    mycontract.exchange = "IDEALPRO"
    mycontract.currency = QUOTE
    
    app = IBClient()
    app.ibapiConnect(PORT=7496)
    price_df: DataFrame = getFXHistoricalData(
        app, 
        mycontract, 
        end_date_ts=f"{YEAR}0312 17:00:00 US/Eastern"
        )
    
    price_df.to_csv(f"{PATH}/{FILE}")