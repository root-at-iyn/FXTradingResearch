import pandas as pd
from data.features import Candle, Intraday, Indicator, Pattern


def apply_features(data: pd.DataFrame):
    """Apply features and indicators to OHLC dataframe"""

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
    data["Iday_Idx"] = data.apply(intraday.index, axis=1, args=[data.index])
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
    data["RSI_DVG"] = data.apply(
        indicator.rsi_divergence, 
        axis=1, 
        args=[data["RSI"], data["High"], data["Low"]]
        )
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
    pattern = Pattern(
        data["Open"],
        data["High"],
        data["Low"],
        data["Close"], 
        data["Range"]
        )
    data["Hammer"] = data.apply(pattern.hammer, axis=1)
    data["Shooting_Star"] = data.apply(pattern.shooting_star, axis=1)
    data["Bull_Engulf"] = data.apply(pattern.bullish_engulfing, axis=1)
    data["Bear_Engulf"] = data.apply(pattern.bearish_engulfing, axis=1)
    data["Dark_Cloud"] = data.apply(pattern.dark_cloud_cover, axis=1)
    data["Piercing"] = data.apply(pattern.piercing, axis=1)
    data["ILR"] = data.apply(pattern.intraday_low_reversal, axis=1)
    data["IHR"] = data.apply(pattern.intraday_high_reversal, axis=1)
    data["S_R"] = data.apply(pattern.support_resistance, axis=1)
    data["BBU_BO"] = data.apply(pattern.bb_upper_breakout, axis=1, args=[8])
    data["BBL_BO"] = data.apply(pattern.bb_lower_breakout, axis=1, args=[8])
    data["Bull_BBR"] = data.apply(
        pattern.bullish_bb_reversal, axis=1, 
        args=[
            data["BB_Lower_16_2"], data["RSI"], data["RSI_DVG"], 
            data["SMA32_Slope"], data["BBL_BO"]
            ]
        ) 
    data["Bear_BBR"] = data.apply(
        pattern.bearish_bb_reversal, axis=1, 
        args=[
            data["BB_Upper_16_2"], data["RSI"], data["RSI_DVG"],
            data["SMA32_Slope"], data["BBU_BO"]
            ]
        )
    return data


if __name__ == '__main__':
    #get data
    PATH = "./output"
    FILE = "GBPUSD_15mins_1yr_End_20260311.csv"
    df = pd.read_csv(f"{PATH}/{FILE}")
    #clean IBKR data
    df.drop(columns=["Volume", "WAP", "BarCount"], inplace=True)
    # apply features to dataframe
    data = apply_features(df)
     
    # show data
    pd.options.display.max_rows = 100

    # Print patterns
    print(data['2025-04-18 16:30':'2025-04-20 21:00'][[ 
    "Iday_Idx","Hammer", "Shooting_Star", "Bull_Engulf", "Bear_Engulf",
    "Dark_Cloud", "Piercing", "Bull_BBR", "Bear_BBR",
    "Sig_Low", "ILR", "Sig_High", "IHR", "S_R",
    "BBU_BO", "BBL_BO", "RSI_DVG", "RSI"
    ]])

    # output feature enhanced price data to csv
    data.to_csv(f"{PATH}/FE_v2_{FILE}")