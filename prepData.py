import pandas as pd
from data.features import Candle, Intraday, Indicator

if __name__ == '__main__':
    #get data
    data = pd.read_csv("./output/GBPUSD_15mins_1yr_End_20260311.csv")
    
    #clean data
    data.drop(columns=["Volume", "WAP", "BarCount"], inplace=True)
    
    #set date to datetimeindex
    data["Date"] = pd.DatetimeIndex(data["Date"],tz="Europe/London")
    data.set_index("Date", inplace=True)
    data = data.tz_convert("US/Eastern")

    #set row index
    data["Idx"] = data.apply(lambda x: data.index.get_loc(x.name), axis=1)
    
    #add candle properties
    candle = Candle()
    data["CBody"] = data.apply(candle.body, axis=1)
    data["CRange"] = data.apply(candle.range, axis=1)
    data["CUWick"] = data.apply(candle.upper_wick, axis=1)
    data["CLWick"] = data.apply(candle.lower_wick, axis=1)
    
    #add intraday properties
    intraday = Intraday()
    data["Iday_Idx"] = data.apply(intraday.index, axis=1)
    data["Iday_High"] = data.apply(intraday.high, axis=1)
    data["Iday_Low"] = data.apply(intraday.low, axis=1)
    data["Iday_Range"] = data.apply(intraday.range, axis=1)

    #add indicators
    indicator = Indicator()
    data["Yday_High"] = data.apply(indicator.yesterday_high, axis=1)
    data["Yday_Low"] = data.apply(indicator.yesterday_low, axis=1)
    
    # show data
    #print(data['2026-03-08 17:15':'2026-03-09 17:45'])
    print(data.iloc[93:192])
