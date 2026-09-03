import pandas as pd
from data.features import Intraday, Indicator, Pattern
from data.candle import Candle


def apply_features(data: pd.DataFrame, pipsize: float = 0.0001):
    """Apply features and indicators to OHLC dataframe"""

    # set date to datetimeindex
    data["Date"] = pd.DatetimeIndex(data["Date"],tz="Europe/London")
    data.set_index("Date", inplace=True)
    data = data.tz_convert("US/Eastern")

    # set row index
    data["Idx"] = df.index.argsort()
    
    # candle properties
    data = Candle().vectorised_apply(data)
    
    # intraday properties
    intraday = Intraday()
    data["Iday_Idx"] = data.apply(intraday.index, axis=1, args=[data.index])
    data["Iday_High"] = data.apply(intraday.high, axis=1)
    data["Iday_HClose"] = data.apply(intraday.highest_close, axis=1)
    data["Iday_LClose"] = data.apply(intraday.lowest_close, axis=1)
    data["Iday_Low"] = data.apply(intraday.low, axis=1)
    data["Iday_Range"] = data.apply(intraday.range, axis=1)
    data["Close_Pct_DHigh"] = data.apply(intraday.close_pct_iday_high, axis=1)
    data["Open_Pct_DHigh"] = data.apply(intraday.open_pct_iday_high, axis=1)

    #add indicators
    indicator = Indicator()
    # Daily References
    data["Yday_High"] = data.apply(indicator.yesterday_high, axis=1)
    data["Yday_Low"] = data.apply(indicator.yesterday_low, axis=1)
    data["Yday_Range"] = data.apply(indicator.yesterday_range, axis=1)
    data["Day_Idx"] = data.apply(indicator.day_index, axis=1)
    data["Yday_Open"] = data.apply(indicator.yesterday_open, axis=1, args=[data["Open"]])
    data["Yday_Close"] = data.apply(indicator.yesterday_close, axis=1, args=[data["Close"]])
    data["Yday_HClose"] = data.apply(
        indicator.yesterday_highest_close, 
        axis=1, 
        args=[data["Iday_HClose"]]
        )
    data["Yday_LClose"] = data.apply(
        indicator.yesterday_lowest_close, 
        axis=1, 
        args=[data["Iday_LClose"]]
        )
    # Yday Body Pct Range
    data["Yday_BPR"] = data.apply(
        indicator.yesterday_body_pct_range, axis=1
        )
    # Yday Close Pct High
    data["Yday_CPH"] = data.apply(indicator.yesterday_close_pct_high, axis=1)
    # Yday Open Pct High
    data["Yday_OPH"] = data.apply(indicator.yesterday_open_pct_high, axis=1)
    # Average Daily Range
    data["ADR"] = data.apply(indicator.ADR, axis=1, args=[12])
    # Average True Range
    data["ATR"] = data.apply(indicator.ATR, axis=1, args=[data["Close"],12])
    data["ATR4"] = data.apply(indicator.ATR, axis=1, args=[data["Close"],4])
    data["ATR16"] = data.apply(indicator.ATR, axis=1, args=[data["Close"],16])
    # Simple Moving Averages
    data["SMA4"] = data.apply(indicator.SMA, axis=1, args=[4, data["Close"]])
    data["SMA8"] = data.apply(indicator.SMA, axis=1, args=[8, data["Close"]])
    data["SMA16"] = data.apply(indicator.SMA, axis=1, args=[16, data["Close"]])
    data["SMA32"] = data.apply(indicator.SMA, axis=1, args=[32, data["Close"]])
    data["SMA96"] = data.apply(indicator.SMA, axis=1, args=[96, data["Close"]])
    data["SMA192"] = data.apply(indicator.SMA, axis=1, args=[200, data["Close"]])
    # Bollinger Bands
    data["BB_Upper_16_2"] = data.apply(
        indicator.bollinger_band_upper, 
        axis=1, 
        args=[2, "SMA16", data["Close"]]
        )
    data["BB_Lower_16_2"] = data.apply(
        indicator.bollinger_band_lower, 
        axis=1, 
        args=[2, "SMA16", data["Close"]]
        )
    # Price to SMA Percentage
    data["Close_Pct_SMA"] = data.apply(
        indicator.pct_sma, axis=1, args=["SMA16", "Close"])
    data["High_Pct_SMA"] = data.apply(
        indicator.pct_sma, axis=1, args=["SMA16", "High"])
    data["Low_Pct_SMA"] = data.apply(
        indicator.pct_sma, axis=1, args=["SMA16", "Low"])
    # RSI
    data["RSI"] = data.apply((indicator.rsi), axis=1, args=[data["Close"]])
    data["RSI_DVG"] = data.apply(
        indicator.rsi_divergence, 
        axis=1, 
        args=[data["RSI"], data["High"], data["Low"]]
        )
    # Significant Levels
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
    data["Sig_HClose"] = data.apply(
        indicator.significant_hclose,
        axis=1,
        args=[data["Iday_HClose"],data["Day_Idx"]]        
    )
    data["Sig_LClose"] = data.apply(
        indicator.significant_lclose,
        axis=1,
        args=[data["Iday_LClose"],data["Day_Idx"]]        
    )
    # SMA Trend
    data["SMA_Trend"] = data.apply(
        indicator.sma_trend, 
        axis=1, 
        args=["SMA4","SMA16","SMA32"]
        )
    # SMA Slope
    data["SMA4_Slope"] = data.apply(
        indicator.sma_slope, axis=1, 
        args=[data["SMA4"]],
        pipsize=pipsize
        )
    data["SMA16_Slope"] = data.apply(
        indicator.sma_slope, axis=1, 
        args=[data["SMA16"]],
        pipsize=pipsize
        )
    data["SMA32_Slope"] = data.apply(
        indicator.sma_slope, axis=1, 
        args=[data["SMA32"]],
        pipsize=pipsize
        )
    data["SMA4_Slope_SMA"] = data.apply(indicator.SMA, axis=1, 
                                         args=[4, data["SMA4_Slope"]])
    data["SMA16_Slope_SMA"] = data.apply(indicator.SMA, axis=1, 
                                         args=[16, data["SMA16_Slope"]])
    data["SMA32_Slope_SMA"] = data.apply(indicator.SMA, axis=1, 
                                         args=[16, data["SMA32_Slope"]])
    # Nbr Closes Above/Below SMA
    data["Close_GT_SMA4"] = data.apply(
        indicator.closes_gt_sma, axis=1, args=["SMA4"])
    data["Close_LT_SMA4"] = data.apply(
        indicator.closes_lt_sma, axis=1, args=["SMA4"])
        # Volatility Spike
    data["Vol_Spike"] = data.apply(
        indicator.volatility_spike, 
        axis=1, 
        args=[data["ATR4"]],
        atr_multiplier = 2
        )
    # Bars Since SMA Crossed
    data["BS_SMA_16_32_X"] = data.apply(
        indicator.bars_since_sma_cross, 
        axis=1, 
        args=[data["SMA16"],data["SMA32"]]
        )
    # Beginning of Day (BOD) Slope 
    data["BOD_Slope_16"] = data.apply(
        indicator.sma_slope_v2,
        axis=1,
        args=[data["SMA16"],data["Iday_Idx"]],
        pipsize = pipsize
    )
    # Slope Trend
    data["Trend_16_32"] = data.apply(
        indicator.slope_trend,
        axis=1,
        args=["SMA16_Slope_SMA", 22.5, 
              "SMA32_Slope_SMA", 11.25, 
              "BS_SMA_16_32_X"],
        period = 16
    )
    # Price Levels
    data["Levels"] = data.apply(
        indicator.levels, 
        axis=1, 
        args=[["Iday_HClose","Iday_LClose"]])

    # level tested
    data[["S_Test","S_Level","ST_Count","R_Test","R_Level","RT_Count","Min_Dist"]] = data.apply(
        indicator.level_tested,
        axis=1,
        args=[
            data["Levels"], data["Open"], data["High"],
            data["Low"], data["Close"]
        ],
        result_type='expand'
    )

    # Patterns
    pattern = Pattern(
        data["Open"],
        data["High"],
        data["Low"],
        data["Close"], 
        data["Range"],
        data["Body"]
        )
    # Candlestick Patterns
    data["Hammer"] = data.apply(pattern.hammer, axis=1)
    data["Bull_Pinbar"] = data.apply(pattern.bullish_pinbar, axis=1)
    data["Shooting_Star"] = data.apply(pattern.shooting_star, axis=1)
    data["Bear_Pinbar"] = data.apply(pattern.bearish_pinbar, axis=1)
    data["Bull_Engulf"] = data.apply(pattern.bullish_engulfing, axis=1)
    data["Bear_Engulf"] = data.apply(pattern.bearish_engulfing, axis=1)
    data["Dark_Cloud"] = data.apply(pattern.dark_cloud_cover, axis=1)
    data["Piercing"] = data.apply(pattern.piercing, axis=1)
    # Intraday Range Reversals
    data["ILR"] = data.apply(
        pattern.intraday_low_reversal, 
        axis=1
        )
    data["IHR"] = data.apply(
        pattern.intraday_high_reversal, 
        axis=1
        )
    # Support / Resistance
    data[["S_R", "S_R_Level"]] = data.apply(
        pattern.support_resistance, 
        axis=1,
        args=[data["Sig_High"], data["Sig_Low"]],
        result_type='expand'
        )
    # Breakouts
    data[["BBU_BO","BBL_BO"]] = data.apply(
        pattern.bb_breakout, 
        axis=1, 
        result_type='expand',
        pipsize=pipsize
        )
    data["Bull_SMA_BO"] = data.apply(pattern.bullish_sma_breakout, axis=1)
    data["Bear_SMA_BO"] = data.apply(pattern.bearish_sma_breakout, axis=1)

    # Bearish Bollinger Band Reversals
    data["Bear_BBR_C1"] = data.apply(
        pattern.bearish_bb_reversal_c1,
        axis=1,
        args=[data["BB_Upper_16_2"]]
    )
    data["Bear_BBR_C2"] = data.apply(pattern.bearish_bb_reversal_c2, axis=1)
    data["Bear_BBR_C3"] = data.apply(pattern.bearish_bb_reversal_c3, axis=1)
    data["Bear_BBR_C4"] = data.apply(pattern.bearish_bb_reversal_c4, axis=1)
    data["Bear_BBR_V2"] = data.apply(pattern.bearish_bb_reversal_v2, axis=1)
    # Bullish Bollinger Band Reversals
    data["Bull_BBR_C1"] = data.apply(
        pattern.bullish_bb_reversal_c1,
        axis=1,
        args=[data["BB_Lower_16_2"]]
    )
    data["Bull_BBR_C2"] = data.apply(pattern.bullish_bb_reversal_c2, axis=1)
    data["Bull_BBR_C3"] = data.apply(pattern.bullish_bb_reversal_c3, axis=1)
    data["Bull_BBR_C4"] = data.apply(pattern.bullish_bb_reversal_c4, axis=1)
    data["Bull_BBR_V2"] = data.apply(pattern.bullish_bb_reversal_v2, axis=1)
    # Trend
    data[["Bull_TC", "Bear_TC"]] = data.apply(
        pattern.trend_continuation, 
        axis=1,
        result_type='expand'
        )
    data[["Bull_PB_Fail", "Bear_PB_Fail"]] = data.apply(
        pattern.pinbar_fail, 
        axis=1,
        args=[data["Bull_Pinbar"], data["Bear_Pinbar"]],
        result_type='expand'
        )
    # Bar Overlap
    data["Overlap"] = data.apply(
        pattern.bar_overlap, 
        axis=1
        )
    data["Overlap_SMA"] = data["Overlap"].rolling(4).mean()

    # Extreme Momentum
    data[["Bull_XM_V2", "Bear_XM_V2"]] = data.apply(
        pattern.extreme_momentum_v2,
        axis=1,
        result_type='expand'
    )
    # Pullback
    data["Bull_Pullback"] = data.apply(
        pattern.bullish_pullback, 
        axis=1,
        args=[data["SMA16"],"SMA16_Slope",
              data["SMA32"],"SMA32_Slope"]
        )
    data["Bear_Pullback"] = data.apply(
        pattern.bearish_pullback, 
        axis=1,
        args=[data["SMA16"],"SMA16_Slope",
              data["SMA32"],"SMA32_Slope"]
        )
    # Inside Bar
    data[["IB","MB_Idx","MB_High","MB_Low"]] = data.apply(
        pattern.inside_bar,
        axis=1,
        result_type='expand'
        )

    # Return all features
    return data


if __name__ == '__main__':
    #get data
    PATH = "./output"
    OUT_PATH = "./research/price_data"
    SYMBOL = "GBPUSD"
    FILE = f"{SYMBOL}_15mins_1yr_End_20260311.csv"
    df = pd.read_csv(f"{PATH}/{FILE}")
    #clean IBKR data
    df.drop(columns=["Volume", "WAP", "BarCount"], inplace=True)
    # apply features to dataframe
    data = apply_features(df, pipsize=0.0001)
    data["Symbol"] = SYMBOL
     
    # show data
    pd.options.display.max_rows = 150

    base_cols = [
        "Iday_Range","Yday_Range", "ADR", "Range", "ATR", "Body", "RSI_DVG", "RSI", "Close_Pct_SMA", 
        "BOD_Slope_16", "S_Test", "S_Level","ST_Count","R_Test", "R_Level", "RT_Count"]

    # Print patterns
    # print(data['2025-03-11 17:15':'2025-03-12 16:45'][base_cols])
    # print(data[base_cols].tail(100))
    print(data[base_cols].query("RSI_DVG == True and ((S_Test == True and ST_Count > 2) or (R_Test == True and RT_Count > 2))"))

    # WRITE TO CSV
    # output feature enhanced price data to csv
    data.to_csv(f"{OUT_PATH}/FE_{FILE}")