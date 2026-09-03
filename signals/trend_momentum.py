import pandas as pd
from data.features import Candle, Intraday, Indicator, Pattern

def apply_trend_momentum(data: pd.DataFrame, pipsize: float = 0.0001) -> pd.DataFrame:
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
    data[["Iday_High","Iday_H_Idx"]] = data.apply(
        intraday.high, axis=1, result_type='expand')
    data[["Iday_Low", "Iday_L_Idx"]] = data.apply(
        intraday.low, axis=1, result_type='expand')
    data[["Iday_HClose", "Iday_HC_Idx"]] = data.apply(
        intraday.highest_close, axis=1, result_type='expand')
    data[["Iday_LClose", "Iday_LC_Idx"]] = data.apply(
        intraday.lowest_close, axis=1, result_type='expand')
    data["Iday_Range"] = data.apply(intraday.range, axis=1)
    data["Close_Pct_DHigh"] = data.apply(intraday.close_pct_iday_high, axis=1)
    data["Open_Pct_DHigh"] = data.apply(intraday.open_pct_iday_high, axis=1)
    # indicators
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
    data["SMA16"] = data.apply(indicator.SMA, axis=1, args=[16, data["Close"]])
    data["SMA32"] = data.apply(indicator.SMA, axis=1, args=[32, data["Close"]])
    data["SMA192"] = data.apply(indicator.SMA, axis=1, args=[192, data["Close"]])
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
    data["SMA192_Slope"] = data.apply(
        indicator.sma_slope, axis=1, 
        args=[data["SMA192"]],
        pipsize=pipsize
        )
    data["SMA4_Slope_SMA"] = data.apply(indicator.SMA, axis=1, 
                                         args=[4, data["SMA4_Slope"]])
    data["SMA16_Slope_SMA"] = data.apply(indicator.SMA, axis=1, 
                                         args=[16, data["SMA16_Slope"]])
    data["SMA32_Slope_SMA"] = data.apply(indicator.SMA, axis=1, 
                                         args=[32, data["SMA32_Slope"]])
    data["SMA192_Slope_SMA"] = data.apply(indicator.SMA, axis=1, 
                                         args=[192, data["SMA192_Slope"]])
    # Significant Levels
    data["Sig_High"] = data.apply(
        indicator.significant_high, 
        axis=1, 
        args=[data["Iday_High"], data["Day_Idx"]]
        )
    data["Sig_Low"] = data.apply(
        indicator.significant_low, 
        axis=1, 
        args=[data["Iday_Low"], data["Day_Idx"]],
        period = 8
        )
    # SMA Trend
    data["SMA_Trend"] = data.apply(
        indicator.sma_trend, 
        axis=1, 
        args=["SMA4","SMA16","SMA32"]
        )
    # Nbr Closes Above/Below SMA
    data["Close_GT_SMA4"] = data.apply(
        indicator.closes_gt_sma, axis=1, args=["SMA4"])
    data["Close_LT_SMA4"] = data.apply(
        indicator.closes_lt_sma, axis=1, args=["SMA4"])
    # Volocity
    data["Velocity"] = data.apply(
        indicator.velocity,
        axis=1,
        args=[data["Close"],1, pipsize]
    )
    data["Velocity_H"] = data.apply(
        indicator.velocity,
        axis=1,
        args=[data["High"],1, pipsize]
    )
    data["Velocity_L"] = data.apply(
        indicator.velocity,
        axis=1,
        args=[data["Low"],1, pipsize]
    )

    # Momentum
    data["Momentum"] = data.apply(
        indicator.momentum,
        axis=1,
        args=["SMA4", "SMA4_Slope", 45, data["ATR4"],
              data["Velocity"], data["High"],data["Low"]]
    )
    # Slope CHG
    data["Slope_CHG"] = data.apply(indicator.slope_diff, axis=1, args=[data["SMA4_Slope"]])
    # Slope DVG
    data["Slope_DVG"] = data.apply(indicator.slope_dvg, axis=1, args=[data["SMA4_Slope"], data["SMA4_Slope_SMA"]])
    # Slope Sync
    data["Slope_Sync"] = data.apply(indicator.slope_sync, axis=1, args=[data["SMA4_Slope"], data["SMA4_Slope_SMA"]])
    
    # Daily Inside Bar
    data[["D_IB","DMB_H_Idx","DMB_H", "DMB_L_Idx","DMB_L"]] = data.apply(
        indicator.daily_inside_bar,
        axis=1,
        args=[
            data["Yday_High"], data["Yday_Low"],
            data["Yday_Open"], data["Yday_Close"],
            data["Yday_HClose"], data["Yday_LClose"],
            data["Iday_Idx"], data["Iday_High"], data["Iday_Low"]
        ],
        result_type='expand'
    )
    # FX Session
    data["Session"] = data.apply(
        indicator.fx_sessions_today,
        axis=1,
    )
    # FX Session High / Low
    data[["TYO_High", "TYO_Low", 
          "LDN_High", "LDN_Low", 
          "NY_High", "NY_Low"]] = data.apply(
        indicator.fx_session_high_low,
        axis=1,
        args=[data["High"],data["Low"]],
        result_type='expand'
    )
    # FX Session Range
    data["Session_Range"] = data.apply(
        indicator.fx_session_range,
        axis=1
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
    # Bullish Bollinger Band Reversals
    data["Bull_BBR_C1"] = data.apply(
        pattern.bullish_bb_reversal_c1,
        axis=1,
        args=[data["BB_Lower_16_2"]]
    )
    # Bearish Bollinger Band Reversals
    data["Bear_BBR_C1"] = data.apply(
        pattern.bearish_bb_reversal_c1,
        axis=1,
        args=[data["BB_Upper_16_2"]]
    )

    data[["Bull_TC", "Bear_TC"]] = data.apply(
        pattern.trend_continuation, 
        axis=1,
        result_type='expand'
        )


    # Extreme Momentum
    data[["Bull_XM_V2", "Bear_XM_V2"]] = data.apply(
        pattern.extreme_momentum_v2,
        axis=1,
        result_type='expand'
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
    data[["IB","MB_Idx","MB_High","MB_Low"]] = data.apply(
        pattern.inside_bar,
        axis=1,
        result_type='expand'
        )
        # Volatility Spike
    data["Vol_Spike"] = data.apply(
        indicator.volatility_spike, 
        axis=1, 
        args=[data["ATR4"]],
        atr_multiplier = 2
        )
    data["Dev_Spike"] = data.apply(
        indicator.deviation_spike,
        axis=1,
        args=[data["ATR4"],data["High_Pct_SMA"],
              data["Low_Pct_SMA"],data["Range"]]
    )
    # Bars Since SMA Crossed
    data["BS_SMA_16_32_X"] = data.apply(
        indicator.bars_since_sma_cross, 
        axis=1, 
        args=[data["SMA16"],data["SMA32"]]
        )
    data["BOD_Slope_16"] = data.apply(
        indicator.sma_slope_v2,
        axis=1,
        args=[data["SMA16"],data["Iday_Idx"]],
        pipsize = pipsize
    )
    # Intraday SMA Cross Count
    data["Iday_SMA_X"] = data.apply(
        indicator.intraday_sma_cross_count, 
        axis=1, 
        args=[data["BS_SMA_16_32_X"]]
        )
    # Consolidation
    data["Consolidation"] = data.apply(
        indicator.consolidation,
        axis=1,
        args=[11.25, "SMA32_Slope_SMA","BOD_Slope_16"]
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
        args=[["Sig_High","Sig_Low"]])
    # Session Levels
    data["Session_Levels"] = data.apply(
        indicator.levels, 
        axis=1, 
        args=[["NY_High","NY_Low","LDN_High","LDN_Low","TYO_High","TYO_Low"]])

    # level tested
    data[["S_Test","S_Level","ST_Count","R_Test","R_Level","RT_Count","Min_Dist"]] = data.apply(
        indicator.level_tested,
        axis=1,
        args=[
            data["Levels"], data["Open"], data["High"],
            data["Low"], data["Close"]
        ],
        result_type='expand',
        pct = 0
    )

    # # Max Retracement
    data[["Max_H_Rtm","H_Rtm", "Max_L_Rtm", "L_Rtm"]] = data.apply(
        indicator.level_retracement,
        axis=1,
        args=[data["High"], data["Low"], data["Iday_H_Idx"], data["Iday_L_Idx"]],
        result_type='expand'
    )
    data[["DMB_H_Max_Rtm","DMB_H_Rtm", "DMB_L_Max_Rtm", "DMB_L_Rtm"]] = data.apply(
        indicator.level_retracement,
        axis=1,
        args=[data["High"], data["Low"], data["DMB_H_Idx"], data["DMB_L_Idx"]],
        result_type='expand'
    )
    # Session Break
    data[["SLB","SBO","SBO_Level","SBO_TS",
          "SBO_Confirmed","SBO_Failed"]] = data.apply(
        indicator.fx_session_breakout,
        axis=1,
        args=[data["Open"],data["High"],data["Low"],data["Close"],data["Body"]],
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
    # Bullish Momentum
    data["Bull_M"] = data.apply(
        pattern.bullish_momentum, axis=1,
        args=[data["ATR4"],"Close_GT_SMA4",4 ]
        )
    # Bearish Momentum
    data["Bear_M"] = data.apply(
        pattern.bearish_momentum, axis=1,
        args=[data["ATR4"], "Close_LT_SMA4",4]
        )
    # Range Breakout
    data[["Bull_Range_BO", "Bear_Range_BO"]] = data.apply(
        pattern.iday_range_breakout,
        axis=1,
        args=[data["IB"], data["MB_High"], data["MB_Low"]],
        result_type='expand'
    )
    # Session Level Break Signal
    data["SLB_Signal"] = data.apply(
        pattern.session_level_break_signal,
        axis=1,
        args=[data["SLB"]]
    )
    # Session Breakout Signal
    data["SBO_Signal"] = data.apply(
        pattern.session_breakout_signal, 
        axis=1, 
        args=[data["SBO_TS"]]
        )
    # Session Breakout Failed Signal
    data["SBO_Fail_Signal"] = data.apply(
        pattern.session_breakout_failed_signal,
        axis=1,
        args=[data["SBO_Failed"]]
    )
    # Session False Breakout Reversal
    data["SFBO_Reversal"] = data.apply(
        pattern.session_false_breakout_reversal,
        axis=1,
        args=[data["SLB_Signal"]]
    )

    # return data
    return data