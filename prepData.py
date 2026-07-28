import pandas as pd
from data.features import Candle, Intraday, Indicator, Pattern


def apply_features(data: pd.DataFrame, pipsize: float = 0.0001):
    """Apply features and indicators to OHLC dataframe"""

    # set date to datetimeindex
    data["Date"] = pd.DatetimeIndex(data["Date"],tz="Europe/London")
    data.set_index("Date", inplace=True)
    data = data.tz_convert("US/Eastern")

    # set row index
    data["Idx"] = data.apply(lambda x: data.index.get_loc(x.name), axis=1)
    
    # candle properties
    candle = Candle()
    data["Body"] = data.apply(candle.body, axis=1)
    data["Range"] = data.apply(candle.range, axis=1)
    data["UWick"] = data.apply(candle.upper_wick, axis=1)
    data["LWick"] = data.apply(candle.lower_wick, axis=1)
    data["Close_Pct_High"] = data.apply(candle.close_pct_high, axis=1)
    data["Open_Pct_High"] = data.apply(candle.open_pct_high, axis=1)
    
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
    data["ADR"] = data.apply(indicator.ADR, axis=1, args=[30])
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
    data[["Bull_IB", "Bear_IB"]] = data.apply(
        pattern.inside_bar, 
        axis=1,
        args=[data["Close_Pct_High"],
              data["BB_Upper_16_2"], data["BB_Lower_16_2"]],
        result_type='expand'
        )
    # Momentum
    data[["Bull_BM", "Bear_BM"]] = data.apply(
    pattern.breakout_momentum, 
    axis=1, 
    args=[data["SMA4"], data["BBU_BO"], data["Bull_SMA_BO"],
          data["BBL_BO"], data["Bear_SMA_BO"]],
    result_type='expand'
    )
    data["Bull_TM"] = data.apply(
        pattern.bullish_trend_momentum, axis=1
        )
    data["Bear_TM"] = data.apply(
        pattern.bearish_trend_momentum, axis=1
        )
    # Support Resistance Signals (for backtesting)
    data[["S_R_Signal", "S_R_Entry"]] = data.apply(
        pattern.s_r_signal,
        axis=1,
        args=[data["S_R"], data["Close_Pct_High"], data["S_R_Level"]],
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

    # Yesterday High Retest
    data["Yday_High_RT"] = data.apply(
        pattern.yday_high_retest,
        args=[data["Close_Pct_High"]], 
        axis=1
        )
    data["Yday_Low_RT"] = data.apply(
        pattern.yday_low_retest,
        args=[data["Close_Pct_High"]], 
        axis=1
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
    pd.options.display.max_rows = 100

    base_cols = [
        "Iday_Range", "ADR", "Range", "ATR", "Body", "RSI_DVG", "RSI", 
        "Overlap_SMA", "IHR", "ILR"]

    # Print patterns
    # print(data['2025-03-11 17:15':'2025-03-12 16:45'][base_cols])
    print(data[base_cols].query("ILR.notna() or IHR.notna()").tail(30))

    # WRITE TO CSV
    # output feature enhanced price data to csv
    data.to_csv(f"{OUT_PATH}/FE_{FILE}")