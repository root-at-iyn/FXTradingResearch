import pandas as pd
from data.features import Candle, Intraday, Indicator, Pattern

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
    data["Body"] = data.apply(candle.body, axis=1)
    data["Range"] = data.apply(candle.range, axis=1)
    data["UWick"] = data.apply(candle.upper_wick, axis=1)
    data["LWick"] = data.apply(candle.lower_wick, axis=1)
    data["Close_%High"] = data.apply(candle.close_pct_high, axis=1)
    data["Open_%High"] = data.apply(candle.open_pct_high, axis=1)
    
    #add intraday properties
    intraday = Intraday()
    data["Iday_Idx"] = data.apply(intraday.index, axis=1)
    data["Iday_High"] = data.apply(intraday.high, axis=1)
    data["Iday_Low"] = data.apply(intraday.low, axis=1)
    data["Iday_Range"] = data.apply(intraday.range, axis=1)
    data["Close_%DHigh"] = data.apply(intraday.close_pct_iday_high, axis=1)
    data["Open_%DHigh"] = data.apply(intraday.open_pct_iday_high, axis=1)

    #add indicators
    indicator = Indicator()
    data["Yday_High"] = data.apply(indicator.yesterday_high, axis=1)
    data["Yday_Low"] = data.apply(indicator.yesterday_low, axis=1)
    data["Day_Idx"] = data.apply(indicator.day_index, axis=1)
    data["ADR"] = data.apply(indicator.ADR, axis=1, args=[30])
    data["ATR"] = data.apply(indicator.ATR, axis=1, args=[data["Close"],12])    
    
    data["SMA4"] = data.apply(indicator.SMA, axis=1, args=[4])
    data["SMA16"] = data.apply(indicator.SMA, axis=1, args=[16])
    data["SMA32"] = data.apply(indicator.SMA, axis=1, args=[32])
    data["BB_Upper_16_2"] = data.apply(
        indicator.bollinger_band_upper, 
        axis=1, 
        args=[2, "SMA16"]
        )
    data["BB_Lower_16_2"] = data.apply(
        indicator.bollinger_band_lower, 
        axis=1, 
        args=[2, "SMA16"]
        )
    data["RSI"] = data.apply((indicator.rsi), axis=1)
    data["Sig_High"] = data.apply(
        indicator.significant_high, 
        axis=1, 
        args=[data["Iday_High"], data["Day_Idx"]]
        )
    data["Sig_Low"] = data.apply(
        indicator.significant_low, 
        axis=1, 
        args=[data["Iday_Low"], data["Day_Idx"]]
        )
    data["SMA_Trend"] = data.apply(
        indicator.sma_trend, 
        axis=1, 
        args=["SMA4","SMA16","SMA32"]
        )
    data["SMA16_Slope"] = data.apply(
        indicator.sma_slope, axis=1, 
        args=[data["SMA16"]]
        )
    data["SMA32_Slope"] = data.apply(
        indicator.sma_slope, axis=1, 
        args=[data["SMA32"]]
        )
    
    # Patterns
    pattern = Pattern()
    data["Hammer"] = data.apply(pattern.hammer, axis=1)

    # show data
    #print(data)
    pd.options.display.max_rows = 100
    print(data['2026-03-09 17:15':'2026-03-10 16:45'])
    # print(data[[
    #     "Open", "High", "Close", "Low", "Range",
    #     "Close_%High","Open_%High",
    #     "Iday_High","Iday_Low","Iday_Range", 
    #     "Close_%DHigh", "Open_%DHigh"
    #     ]])
    
