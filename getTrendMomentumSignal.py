import pandas as pd
import time
from signals.trend_momentum import apply_trend_momentum
from ib.client import IBClient
from ibapi.client import Contract
from datetime import datetime, tzinfo

def ibapiHistoricalDataReq(app: IBClient, contract: Contract):
    app.reqHistoricalData(
        app.nextId(),
        contract,
        "", # empty str to get most recent data
        "32 D",
        "15 mins",
        "MIDPOINT",
        0, # get data out of RTH
        2, # Epoch timestamp
        True,
        []
    )

def getRecentHistoricalData(
        base: str,
        quote: str,
        host: str = "127.0.0.1",
        port: int = 7496
):
    app = IBClient()
    app.ibapiConnect(HOST=host, PORT=port, CLIENT_ID=1)

    if app.isConnected():
        contract = Contract()
        contract.symbol = base
        contract.secType = "CASH"
        contract.exchange = "IDEALPRO"
        contract.currency = quote

        counter = 0
        timeout_threshold = 60
        ibapiHistoricalDataReq(app, contract)
        while len(app.data) == 0:
            time.sleep(1)
            timeout_threshold -= 1
            if timeout_threshold == 0:
                break
            
        # close socket
        app.disconnect()
        # build data frame
        if len(app.data) > 0:
            df = pd.DataFrame(app.data)
            df.columns = ['Date', 'Open', 'High', 'Low', 'Close','Volume','WAP','BarCount']
            # return dataframe
            return df
        else:
            exit()
    else:
        print(f"Connection to socket {host}:{port} failed!")
        exit()


if __name__ == '__main__':
    #get data
    base = "GBP"
    quote = "USD"
    df = getRecentHistoricalData(base, quote)
    #clean IBKR data
    df.drop(columns=["Volume", "WAP", "BarCount"], inplace=True)
    # apply features to dataframe
    data = apply_trend_momentum(df, pipsize=0.0001)
    data["Symbol"] = base + quote
     
    # show data
    pd.options.display.max_rows = 100
    cols = ["Open", "High", "Low", "Close", "Range", "SMA4_Slope", "Bull_TM", "Bear_TM", "ATR4", "ADR"]
    print(data[cols].tail(100))