import pandas as pd
import time
from signals.trend_momentum import apply_trend_momentum
from ib.client import IBClient
from ibapi.client import Contract

def ibapiHistoricalDataReq(app: IBClient, contract: Contract):
    app.reqHistoricalData(
        app.nextId(),
        contract,
        "", # empty str to get most recent data / test data 20260715 16:45:00 US/Eastern
        "14 D",
        "15 mins",
        "MIDPOINT",
        0, # get data out of RTH
        2, # Epoch timestamp
        False,
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
    # get data
    base = "GBP"
    quote = "USD"
    tp = 1.5 # 1 for TM / 2 for BBR
    sl = 1
    df = getRecentHistoricalData(base, quote)
    #clean IBKR data
    df.drop(columns=["Volume", "WAP", "BarCount"], inplace=True)
    # apply features to dataframe
    pip = 0
    if quote == "JPY":
        pip = 0.01
    else:
        pip = 0.0001
    data = apply_trend_momentum(df, pipsize=pip)
    data["Symbol"] = base + quote
    data["Entry"] = data.apply(lambda x: x["Close"], axis=1)
    data["SL"] = data.apply(lambda x: x["ATR4"] * sl, axis=1)
    data["TP"] = data.apply(lambda x: x["ATR4"] * tp, axis=1)
     
    # show data
    pd.options.display.max_rows = 100
    pd.options.display.precision = 6
    cols = ["Symbol","ATR4", "Range","Body","ADR",
            "D_IB","SLB","SBO","SBO_Level","SBO_TS",
            "SBO_Signal","SLB_Signal","SFBO_Reversal"
            ]


    print(data[cols].tail(100),"\n")
    # data.to_csv(f"./research/price_data/FE_latest.csv")
