from pandas import Series, DataFrame, DatetimeIndex, to_datetime, Timedelta, Timestamp, NaT
from datetime import time
from math import sqrt, atan, pi
import numpy as np



class Indicator():
    def __init__(self) -> None:
        self.h = None
        self.yday_high = None
        self.l = None 
        self.yday_low = None
        self.yday_open = []
        self.yday_close = None
        self.yday_hclose = None
        self.yday_lclose = None
        self.daily_range = []
        self.adr = None
        self.day_idx = 0
        self.gain = []
        self.loss = []
        self.average_gain = []
        self.average_loss = []
        self.rs = None
        self.sig_high = set()
        self.sig_low = set()
        self.true_range = []
        self.close_gt_sma = 0
        self.close_lt_sma = 0
        self.sma_not_crossed = 0
        # daily mother bar
        self.dmb_range_high = None 
        self.dmb_range_low = None
        self.dmb_range_open = None 
        self.dmb_range_close = None
        self.dmb_range_hclose = None
        self.dmb_range_lclose = None
        self.h_idx = None
        self.l_idx = None
        # level test
        self.support_tested = {}
        self.resistance_tested = {}
        # momentum
        self.bullish_momentum_count = 0
        self.bearish_momentum_count = 0
        # fx sessions
        self.today_fx_open = None
        self.tokyo_high = 0
        self.tokyo_low = 0
        self.london_high = 0
        self.london_low = 0
        self.new_york_high = 0
        self.new_york_low = 0
        # Session Breakout
        self.session_level_break = NaT
        self.session_level_break_h = 0
        self.session_level_break_l = 0
        self.session_breakout = 0
        self.session_level = 0
        self.session_breakout_timestamp = None 
        self.session_breakout_confirmed = False
        self.session_breakout_failed = False

    def yesterday_high(self, df: Series):
        """Return the high of yesterday's session"""
        
        if int(df["Iday_Idx"]) == 0 and int(df["Idx"]) > 0:
            self.yday_high = self.h
        self.h = df["Iday_High"]

        return self.yday_high

    def yesterday_low(self, df: Series):
        """Return the low of yesterday's session"""
        
        if int(df["Iday_Idx"]) == 0 and int(df["Idx"]) > 0:
            self.yday_low = self.l
        self.l = df["Iday_Low"]

        return self.yday_low
    
    def yesterday_range(self, df: Series):
        """Return the range of yesterday's session"""
        if df["Yday_High"] is not None:
            return df["Yday_High"] - df["Yday_Low"]
    
    def yesterday_open(self, df: Series, open_price: Series):
        """Returns the previous day's opening price"""
        idx = int(df["Idx"])
        if df["Iday_Idx"] == 0:
            self.yday_open.append(df["Open"])
        if len(self.yday_open) > 1:
            return self.yday_open[-2]

    def yesterday_close(self, df: Series, close_price: Series):
        """Returns the previous day's closing price"""
        idx = int(df["Idx"])
        if df["Day_Idx"] > 0 and df["Iday_Idx"] == 0:
            self.yday_close = close_price.iloc[idx-1]
        return self.yday_close

    def yesterday_highest_close(self, df: Series, iday_hclose: Series):
        """Returns the previous day's highest close"""
        idx = int(df["Idx"])
        if df["Day_Idx"] > 0 and df["Iday_Idx"] == 0:
            self.yday_hclose = iday_hclose.iloc[idx-1]
        return self.yday_hclose

    def yesterday_lowest_close(self, df: Series, iday_lclose: Series):
        """Returns the previous day's lowest close"""
        idx = int(df["Idx"])
        if df["Day_Idx"] > 0 and df["Iday_Idx"] == 0:
            self.yday_lclose = iday_lclose.iloc[idx-1]
        return self.yday_lclose

    def yesterday_close_pct_high(self, df: Series):
        """Returns percentage of yesterday's close from yesterday's high"""
        if df["Day_Idx"] > 0:
            return (df["Yday_High"] - df["Yday_Close"]) / df["Yday_Range"]

    def yesterday_open_pct_high(self, df: Series):
        """Returns percentage of yesterday's open from yesterday's high"""
        if df["Day_Idx"] > 0:
            return (df["Yday_High"] - df["Yday_Open"]) / df["Yday_Range"]
        
    def yesterday_body_pct_range(self, df: Series):
        """Returns percentage of yesterday's body (open-close) of yesterday's range"""
        if df["Day_Idx"] > 0:
            return abs((df["Yday_Close"]-df["Yday_Open"])/df["Yday_Range"])
    
    def ADR(self, df: Series, period: int):
        """Returns the average daily range for `period` trading sessions"""

        if int(df["Iday_Idx"]) == 0 and int(df["Idx"]) > 0:
            self.daily_range.append(df["Yday_High"] - df["Yday_Low"])
            if len(self.daily_range) >= period:
                avg = Series(self.daily_range).rolling(period).mean().round(6)
                self.adr = avg.iloc[-1]        
        return self.adr
    
    def day_index(self, df: Series, roll: time = time(hour=17,minute=00)):
        """Return the day count based on days starting at the FX rollover"""
        
        if int(df["Iday_Idx"]) == 0 and int(df["Idx"]) > 0:
            self.day_idx += 1
        return self.day_idx
    
    def SMA(self, df: Series, n: int, price_data: Series):
        "Return the Simple Moving Average of Close prices over `n` periods"
        
        idx = int(df["Idx"])
        if len(price_data) > n:
            return sum(price_data.iloc[idx-n+1:idx+1])/n
        
    def sma_standard_deviation(self, df: Series, avg_col_name: str, n: int, price_data: Series):
        """Return the Standard Deviation of the last `n` SMA periods"""

        idx = int(df["Idx"])
        if idx > n:
            square_dev = [(x - df[avg_col_name])**2 for x in price_data.iloc[idx-n+1:idx+1]]
            variance = sum(square_dev)/n
            standard_dev = sqrt(variance)
            return standard_dev
    
    def bollinger_band_upper(
            self, df: Series, k: int, sma_col_name: str, price_data: Series, n: int = 16
            ):
        """
        Return the Bollinger Upper-Band value to `k` standard 
        deviations for the last `n` SMA periods
        """
        std = self.sma_standard_deviation(df, sma_col_name, n, price_data)
        if std is not None:
            return df[sma_col_name] + (std * k)

    def bollinger_band_lower(
            self, df: Series, k: int, sma_col_name: str, price_data: Series, n: int = 16
            ):
        """
        Return the Bollinger Lower-Band value to `k` standard 
        deviations for the last `n` SMA periods
        """

        std = self.sma_standard_deviation(df, sma_col_name, n, price_data)
        if std is not None:
            return df[sma_col_name] - std * k
    
    def close_pct_sma(
            self,
            df,   
            sma_col_name: str = "SMA16"
            ):
        """Return percentage distance of the Close price from the SMA"""
        pct_sma = (df["Close"] - df[sma_col_name]) / df[sma_col_name] * 100
        return pct_sma

    def pct_sma(
            self,
            df,   
            sma_col_name: str = "SMA16",
            price_point: str = "Close"
            ):
        """Return percentage distance of the Close price from the SMA"""
        if df[sma_col_name] > 0:
            pct_sma = abs(df[price_point] - df[sma_col_name]) / df[sma_col_name] * 100
            return pct_sma

    def rsi(self, df: Series, close: Series, period: int = 16):
        """
        Returns the Relative Strength Index (RSI)
        """

        idx = int(df["Idx"])
        if idx > 0:
            change = df["Close"] - close.iloc[idx-1]
            self.gain.append(change if change > 0 else 0)
            self.loss.append(abs(change) if change < 0 else 0)
            # Calc Initial Average Gain/Loss
            if len(self.gain) == period:
                self.average_gain.append(sum(self.gain[-period:]) / period)
                self.average_loss.append(sum(self.loss[-period:]) / period)
            # Calc Smoothed Average (Gain|Loss)
            elif len(self.average_gain) > 0:
                # (Prev AG * (N-1) + Current Gain) / N
                self.average_gain.append(
                    (self.average_gain[-1] * (period-1) + self.gain[-1]) / period
                )
                # (Prev AL * (N-1) + Current Loss) / N
                self.average_loss.append(
                    (self.average_loss[-1] * (period-1) + self.loss[-1]) / period
                )
            # RSI value
            if len(self.average_gain) > 0:
                self.rs = self.average_gain[-1] / self.average_loss[-1]
                rsi = 100 - (100/(1+self.rs))
                return rsi
    
    def rsi_divergence(
            self, 
            df: Series, 
            rsi: Series, 
            high: Series, 
            low: Series
            ):
        """Returns if Bullish or Bearish RSI Divergence occurred"""
        idx = int(df["Idx"])
        offset = int(df["Iday_Idx"])
        start = idx - offset
        # max rsi
        rsi_max_ts = rsi.iloc[start:idx].nlargest(1).index
        rsi_max = rsi.loc[rsi_max_ts] # Series
        rsi_max_high = high.loc[rsi_max_ts] # Series
        # min rsi
        rsi_min_ts = rsi.iloc[start:idx].nsmallest(1).index
        rsi_min = rsi.loc[rsi_min_ts] # Series
        rsi_min_low = low.loc[rsi_min_ts] # Series
        # bearish divergence
        if rsi_max.empty is False:
            # removed for wider match: and df["High"] == df["Iday_High"] \
            if rsi_max.iloc[0] > 70 \
                and df["High"] > rsi_max_high.iloc[0] \
                and df["RSI"] < rsi_max.iloc[0]:
                return True
        # bullish divergence
        if rsi_min.empty is False:
            # removed for wider match: and df["Low"] == df["Iday_Low"] \
            if rsi_min.iloc[0] < 30 \
                and df["Low"] < rsi_min_low.iloc[0] \
                and df["RSI"] > rsi_min.iloc[0]:
                return True        

    def significant_high(
            self, 
            df: Series, 
            iday_high: Series,
            day_idx: Series, 
            period: int = 8
            ):
        """
        Return if the Iday_High is significant in today's session
        """

        idx = int(df["Idx"])
        idh = iday_high
        
        # Reset significant intraday highs every trading day
        if df["Iday_Idx"] == 0:
            self.sig_high = set()
            self.highest_sig_high = None

        if idx >= period:
            if idh.iloc[idx] not in self.sig_high:
                # Check if the Iday High has been the same for `period`
                # Check if the High Low was created in this session
                if idh.iloc[idx] == idh.iloc[idx - period] \
                    and day_idx.iloc[idx - period] == day_idx.iloc[idx]:
                    self.sig_high.add(idh.iloc[idx])
                    self.highest_sig_high = idh.iloc[idx]

        return self.highest_sig_high

    def significant_low(
            self, 
            df: Series, 
            iday_low: Series,
            day_idx: Series, 
            period: int = 8
            ):
        """
        Return if the Iday_Low is significant in today's session
        """

        idx = int(df["Idx"])
        idl = iday_low
        
        # Reset significant intraday lows every trading day
        if int(df["Iday_Idx"]) == 0:
            self.sig_low = set()
            self.lowest_sig_low = None

        if idx >= period:
            if idl.iloc[idx] not in self.sig_low:
                # Check if the Iday Low has been the same for `period`
                # Check if the Iday Low was created in this session
                if idl.iloc[idx] == idl.iloc[idx - period] \
                    and day_idx.iloc[idx - period] == day_idx.iloc[idx]:
                    self.sig_low.add(idl.iloc[idx])
                    self.lowest_sig_low = idl.iloc[idx]
        
        return self.lowest_sig_low
    
    def significant_hclose(
            self, 
            df: Series, 
            iday_hclose: Series,
            day_idx: Series, 
            period: int = 8
            ):
        """Return highest intraday close 
        that was the highest for over `period` bars"""
        idx = int(df["Idx"])
        current_hclose = df["Iday_HClose"]
        if df['Iday_Idx'] > period:
            period_start_hclose = iday_hclose.iloc[idx-period]
            if current_hclose == period_start_hclose \
            and day_idx.iloc[idx - period] == day_idx.iloc[idx]:
                return current_hclose
            
    def significant_lclose(
            self, 
            df: Series, 
            iday_lclose: Series,
            day_idx: Series, 
            period: int = 8
            ):
        """Return lowest intraday close 
        that was the lowest for over `period` bars"""
        idx = int(df["Idx"])
        current_lclose = df["Iday_LClose"]
        if df['Iday_Idx'] > period:
            period_start_lclose = iday_lclose.iloc[idx-period]
            if current_lclose == period_start_lclose \
            and day_idx.iloc[idx - period] == day_idx.iloc[idx]:
                return current_lclose
    
    def ATR(self, df: Series, closes: Series, period: int = 12):
        """Return the Average True Range for the period"""

        idx = int(df["Idx"])
        if idx > 0:
            tr = [
                df["Range"], 
                (df["High"] - closes.iloc[idx-1]),
                (df["Low"] - closes.iloc[idx-1])
                ]
            tr.sort()
            self.true_range.append(tr.pop())
        if len(self.true_range) >= period:
            average_true_range = sum(self.true_range[-period:]) / period
            return average_true_range
        
    def sma_trend(
            self, 
            df: Series, 
            fast_sma_col_name: str, 
            slow_sma_col_name: str,
            xslow_sma_col_name: str  
            ):
        """Returns a value between -2 and 2 on the strength SMA trend
        
        The SMA Trend is categorised as:

        * -2 = Downtrend
        * -1 = Bearish Retracement
        *  0 = Consolidation
        *  1 = Bullish Retracement
        *  2 = Uptrend
        """
        if df[fast_sma_col_name] > df[slow_sma_col_name] \
        and df[slow_sma_col_name] > df[xslow_sma_col_name]:
            return 2
        elif df[slow_sma_col_name] < df[xslow_sma_col_name] \
        and df[fast_sma_col_name] > df[xslow_sma_col_name]:
            return 1
        elif df[slow_sma_col_name] > df[xslow_sma_col_name] \
        and df[fast_sma_col_name] < df[xslow_sma_col_name]:
            return -1
        elif df[xslow_sma_col_name] > df[slow_sma_col_name] \
        and df[fast_sma_col_name] < df[slow_sma_col_name]:
            return -2
        else:
            return 0
        
    def sma_slope(
            self, 
            df: Series, 
            sma: Series, 
            lookback: int = 1, 
            run: int = 2,
            pipsize: int = 0.0001
        ):
        """Return the angle of the SMA slope"""

        idx = int(df["Idx"])
        if idx >= lookback:
            # pipsize = 0.0001
            rise = (sma.iloc[idx] - sma.iloc[idx-lookback]) / pipsize
            slope = rise / (lookback + 1)
            return atan(slope) * (180/pi)
        
    def sma_slope_v2(
            self, 
            df: Series, 
            sma: Series, 
            dynamic_lookback: Series,
            pipsize: int = 0.0001
            ):
        """Return the angle of a slope since the dynamic_lookback period
        
        `dynamic_lookback`: A series of incrementing integers
        """
        idx = int(df["Idx"])
        slope = self.sma_slope(df, sma, dynamic_lookback.iat[idx] ,pipsize=pipsize)
        return slope
    
    def closes_gt_sma(self, df: Series, sma: str):
        """Return the number of bars since 
        the closing price has remained above the SMA"""
        if df["Close"] > df[sma]:
            self.close_gt_sma += 1
        else:
            self.close_gt_sma = 0
        return self.close_gt_sma

    def closes_lt_sma(self, df: Series, sma: str):
        """Return the number of bars since 
        the closing price has remained below the SMA"""
        if df["Close"] < df[sma]:
            self.close_lt_sma += 1
        else:
            self.close_lt_sma = 0
        return self.close_lt_sma

    def bars_since_sma_cross(self, df: Series, fast_sma: Series, slow_sma: Series):
        """Return the number of bars since 
        fast_sma and slow_sma crossed"""
        idx = int(df["Idx"])
        if fast_sma.iloc[idx-1] < slow_sma.iloc[idx-1] \
            and fast_sma.iloc[idx] > slow_sma.iloc[idx]:
            self.sma_not_crossed = 0
        elif fast_sma.iloc[idx-1] > slow_sma.iloc[idx-1] \
            and fast_sma.iloc[idx] < slow_sma.iloc[idx]:
            self.sma_not_crossed = 0
        else:
            self.sma_not_crossed +=1
        return self.sma_not_crossed

    def intraday_sma_cross_count(
            self, 
            df:Series, 
            bars_since_sma_cross: Series
            ):
        """Returns the number of times the SMA pairs 
        have crossed in the intraday session"""
        sma_cross_count = 0
        if df.name < df["Session"]["FX_Close"]:
            today_bs_sma_x = \
                bars_since_sma_cross.loc[df["Session"]["FX_Open"]:df.name]
            sma_cross_count = today_bs_sma_x[today_bs_sma_x == 0].count()
            return sma_cross_count


    def velocity(self, df: Series, price_point: Series, period: int, pipsize: float):
        """Returns the velocity of price movement over time"""
        idx = int(df["Idx"])
        return ((price_point.iat[idx] - price_point.iat[idx-period])/pipsize) / (period+1)
    
    def momentum(
            self, 
            df: Series,
            sma: str,
            sma_slope: str,
            slope_angle: int,
            atr: Series,
            velocity: Series,
            high: Series,
            low: Series
            ):
        """Indicates whether price has bullish momentum or bearish momentum
        
        Return Values:
        - 1 = Bullish Momentum
        - -1 = Bearish Momentum
        - 0 = No Momentum
        """
        idx = int(df["Idx"])
        m = 0
        # Bullish Momentum
        if velocity.iat[idx] > (velocity.iat[idx-1]) \
        and (velocity.iat[idx] + velocity.iat[idx-1]) > 0 \
        and df["Range"] > atr.iat[idx] \
        and df["Close"] > df[sma] \
        and df[sma_slope] > (slope_angle * 0.5) \
        and df["Close"] > high.iat[idx-1] \
        and df["Close_Pct_High"] < 0.34:
            self.bullish_momentum_count = 0
            m = 1
            self.bullish_momentum_count += 1
        elif df["Close"] > df[sma] \
        and df[sma_slope] > slope_angle \
        and self.bullish_momentum_count > 0:
            m = 1
            self.bullish_momentum_count += 1
        # Bearish Momentum
        elif (velocity.iat[idx] < velocity.iat[idx-1]) \
        and (velocity.iat[idx] + velocity.iat[idx-1]) < 0 \
        and df["Range"] > atr.iat[idx] \
        and df["Close"] < df[sma] \
        and df[sma_slope] < (-slope_angle * 0.5) \
        and df["Close"] < low.iat[idx-1] \
        and df["Close_Pct_High"] > 0.66:
            self.bearish_momentum_count = 0
            m = -1
            self.bearish_momentum_count += 1
        elif df["Close"] < df[sma] \
        and df[sma_slope] < -slope_angle \
        and self.bearish_momentum_count > 0:
            m = -1
            self.bearish_momentum_count += 1
        else:
            m = 0
            self.bullish_momentum_count = 0
            self.bearish_momentum_count = 0
        return m
    
    def volatility_spike(self, df: Series, atr: Series, atr_multiplier: int = 2):
        """Return whether price volatility has spiked"""
        idx = int(df["Idx"])
        if atr.iloc[idx] > (atr.iloc[idx-1] * atr_multiplier):
            return True
        else:
            return False
        
    def deviation_spike(
            self, 
            df: Series, 
            atr: Series, 
            high_pct_sma: Series, 
            low_pct_sma: Series,
            bar_range: Series
            ):
        """Return where the current bar's high or low 
        has a sudden extreme deviation away from the SMA"""
        idx = df["Idx"]
        deviation_spike = 0
        # Deviation Spike Up
        if high_pct_sma.iat[idx] > 0.09 \
        and df["Close_Pct_SMA"] > 0.075 \
        and df["Close_Pct_High"] < 0.34 \
        and df["Close"] > df["BB_Upper_16_2"] \
        and df["Range"] > atr.iat[idx] * 1.5:
            deviation_spike = 1
        # Deviation Spike Down
        elif low_pct_sma.iat[idx] > 0.09 \
        and df["Close_Pct_SMA"] > 0.075 \
        and df["Close_Pct_High"] > 0.66 \
        and df["Close"] < df["BB_Lower_16_2"] \
        and df["Range"] > atr.iat[idx] * 1.5:
            deviation_spike = -1
        else:
            deviation_spike = 0
        return deviation_spike

        
    def slope_trend(
            self, 
            df: Series, 
            fast_sma_slope: str,
            fast_slope_angle: int, 
            slow_sma_slope: str,
            slow_slope_angle: int,
            bs_sma_x: str, 
            period: int = 16
            ):
        """Returns if the fast and slow Simple Moving Averages are trending"""
        if df[fast_sma_slope] > fast_slope_angle \
            and df[slow_sma_slope] > slow_slope_angle:
            return 1
        elif df[fast_sma_slope] < -fast_slope_angle \
            and df[slow_sma_slope] < -slow_slope_angle:
            return -1
        else:
            return 0
    
    def slope_diff(self, df: Series, slope: Series):
        """Returns the SMA Slope change"""
        idx = df["Idx"]
        return (slope.iloc[idx] - slope.iloc[idx-1])
        
    def slope_dvg(self, df: Series, slope: Series, slope_sma: Series):
        "Returns whether the slope and slope_sma are diverging"
        idx = int(df["Idx"])
        if slope.iloc[idx-1] < -45 and slope_sma.iloc[idx-1] < -45 \
        and df["Slope_CHG"] > 22.5:
            return 1
        elif slope.iloc[idx-1] > 45 and slope_sma.iloc[idx-1] > 45 \
        and df["Slope_CHG"] < -22.5:
            return -1
        else:
            return 0
        
    def slope_sync(self, df: Series, slope: Series, slope_sma: Series):
        idx = int(df["Idx"])
        if slope.iloc[idx] > slope.iloc[idx-1] \
        and slope_sma.iloc[idx] > slope_sma.iloc[idx-1]:
            return 1
        if slope.iloc[idx] < slope.iloc[idx-1] \
        and slope_sma.iloc[idx] < slope_sma.iloc[idx-1]:
            return -1
    
    def levels(self, df: Series, col_names: list[str]):
        """Returns a list of price levels"""
        price_levels = [df[col] for col in col_names]
        return price_levels
    
    def level_retracement(
            self, 
            df: Series, 
            high: Series, 
            low: Series,
            reference_high_idx: Series,
            reference_low_idx: Series

            ):
        """Return the percentage price retraced from Iday_High and Iday_Low"""
        idx = int(df["Idx"])
        max_retrace_from_high = 0
        retrace_from_high = 0
        max_retrace_from_low = 0
        retrace_from_low = 0
        ref_high_idx = None
        ref_low_at_high_idx = None
        ref_low_idx = None
        ref_high_at_low_idx = None

        # Only set ref idx if value not NaN
        if reference_high_idx.iat[idx] > -1:
            ref_high_idx = int(reference_high_idx.iat[idx])
        if ref_high_idx and reference_low_idx.iat[ref_high_idx] > -1:
            ref_low_at_high_idx = int(reference_low_idx.iat[ref_high_idx])
        if reference_low_idx.iat[idx] > -1:
            ref_low_idx = int(reference_low_idx.iat[idx])
        if ref_low_idx and reference_high_idx.iat[ref_low_idx] > -1:
            ref_high_at_low_idx = int(reference_high_idx.iat[ref_low_idx])

        # Only calc if all idx refs are not NaN
        if ref_low_idx is not None and ref_high_idx is not None \
            and ref_high_at_low_idx is not None and ref_low_at_high_idx is not None:
            h_window =  high.iloc[ref_low_idx+1:idx+1]
            l_window =  low.iloc[ref_high_idx+1:idx+1]
            
            if h_window.max() > 0:
                max_retrace_from_low = (h_window.max() - low.iat[ref_low_idx]) / (high.iat[ref_high_at_low_idx] - low.iat[ref_low_idx])
                retrace_from_low = (high.iat[idx] - low.iat[ref_low_idx]) / (high.iat[ref_high_at_low_idx] - low.iat[ref_low_idx])

            if l_window.min() > 0:
                max_retrace_from_high = (high.iat[ref_high_idx] - l_window.min()) / (high.iat[ref_high_idx] - low.iat[ref_low_at_high_idx])
                retrace_from_high = (high.iat[ref_high_idx] - low.iat[idx]) / (high.iat[ref_high_idx] - low.iat[ref_low_at_high_idx])
        return max_retrace_from_high, retrace_from_high, max_retrace_from_low, retrace_from_low
    
    def level_tested(
            self, 
            df: Series, 
            levels: Series, 
            open: Series, 
            high: Series, 
            low: Series, 
            close: Series,
            pct: int = 0.05
            ):
        """Returns if a price `level` was tested

        Levels: a list of price levels to check
        """
        idx = int(df["Idx"])
        s_test = False
        s_level = 0
        s_test_count = 0
        r_test = False
        r_level = 0
        r_test_count = 0
        min_distance = df["Iday_Range"] * pct

        if df["Iday_Idx"] == 0:
            self.support_tested = {}
            self.resistance_tested = {}
        # Two-bar Bullish Rejection
        if idx > 0 and levels.empty is False:
            for level in levels.iat[idx]:
                if open.iat[idx-1] > level and close.iat[idx-1] < level \
                and open.iat[idx] < level and close.iat[idx] > level:
                    if level not in self.support_tested.keys():
                        self.support_tested[level] = 0
                    self.support_tested[level] += 1
                    s_test = True
                    s_level = level
                    s_test_count = self.support_tested[level]
                    break
            # Single-bar Bullish Rejection
                if open.iat[idx] > level and low.iat[idx] < (level + min_distance) \
                and close.iat[idx] > level:
                    if level not in self.support_tested.keys():
                        self.support_tested[level] = 0
                    self.support_tested[level] += 1
                    s_test = True
                    s_level = level
                    s_test_count = self.support_tested[level]
                    break
            # Two-bar Bearish Rejection
                if open.iat[idx-1] < level and close.iat[idx-1] > level \
                and open.iat[idx] > level and close.iat[idx] < level:
                    if level not in self.resistance_tested.keys():
                        self.resistance_tested[level] = 0
                    self.resistance_tested[level] +=1
                    r_test = True
                    r_level = level
                    r_test_count = self.resistance_tested[level]
                    break
            # Single-bar Bearish Rejection
                if open.iat[idx] < level and high.iat[idx] > (level - min_distance) \
                and close.iat[idx] < level:
                    if level not in self.resistance_tested.keys():
                        self.resistance_tested[level] = 0
                    self.resistance_tested[level] +=1
                    r_test = True
                    r_level = level
                    r_test_count = self.resistance_tested[level]
                    break

        # return data
        return s_test, s_level, s_test_count, r_test, r_level, r_test_count, min_distance
    
    def fx_session_breakout(
        self, 
        df: Series,
        open: Series, 
        high: Series,
        low: Series,
        close: Series,
        body: Series
        ):
        """Return if price broke out from a session level
        
        start: The string name of an FX Session key, e.g. `LDN_Open`
        end: The string name of an FX Session key, e.g. `NY_Close`
        """
        idx = df["Idx"]
        current_time = df.name
        session_start = None
        session_end = None
        session_high = None
        session_low = None
        td = Timedelta(minutes=15)
        # Session Window
        if current_time >= df["Session"]["TYO_Open"] \
        and current_time < df["Session"]["LDN_Open"]:
            session_start = df["Session"]["TYO_Open"]
            session_end = df["Session"]["LDN_Open"]
            session_high = df["NY_High"]
            session_low = df["NY_Low"]
        if current_time >= df["Session"]["LDN_Open"] \
        and current_time < df["Session"]["NY_Open"]:
            session_start = df["Session"]["LDN_Open"]
            session_end = df["Session"]["NY_Open"]
            session_high = df["TYO_High"]
            session_low = df["TYO_Low"]
        if current_time >= df["Session"]["NY_Open"] \
        and current_time < (df["Session"]["NY_Close"] + td):
            session_start = df["Session"]["NY_Open"]
            session_end = df["Session"]["NY_Close"] + td
            session_high = df["LDN_High"]
            session_low = df["LDN_Low"]
        # Current FX Session
        if session_start is not None:
            if current_time >= session_start \
            and current_time < session_end:
                if df.name == session_start:
                    self.session_level_break = NaT
                    self.session_level_break_h = 0
                    self.session_level_break_l = 0
                    self.session_breakout = 0
                    self.session_level = 0
                    self.session_breakout_timestamp = None 
                    self.session_breakout_confirmed = False
                    self.session_breakout_failed = False
                # Bullish BO
                if close.iat[idx-1] <= session_high \
                and close.iat[idx] > session_high:
                    if self.session_level_break_h != session_high:
                        self.session_level_break = current_time
                        self.session_level_break_h = session_high
                        self.session_level = self.session_level_break_h
                        self.session_breakout = 2
                    if body.iat[idx] > 2 * body.iat[idx-1] \
                    and df["Range"] > df["ATR4"] * 1.5:
                        if self.session_breakout != 1:
                            self.session_breakout = 1
                            self.session_level = session_high
                            self.session_breakout_timestamp = current_time
                            self.session_breakout_confirmed = False
                            self.session_breakout_failed = False
                if self.session_breakout == 1:
                    # Bullish BO Confirmed 
                    if self.session_breakout_confirmed is False \
                    and self.session_breakout_failed is False \
                    and df["Close"] > high.loc[self.session_breakout_timestamp]:
                        self.session_breakout_confirmed = True
                    # Bullish BO Failed
                    if self.session_breakout_failed is False \
                    and df["Close"] < session_high \
                    and df["Close"] < open.loc[self.session_breakout_timestamp]:
                        self.session_breakout_failed = True
                # Bearish BO
                if close.iat[idx-1] >= session_low \
                and close.iat[idx] < session_low:
                    if self.session_level_break_l != session_low:
                        self.session_level_break = current_time
                        self.session_level_break_l = session_low
                        self.session_level = self.session_level_break_l
                        self.session_breakout = -2
                    if body.iat[idx] > 2 * body.iat[idx-1] \
                    and df["Range"] > df["ATR4"] * 1.5:
                        if self.session_breakout != -1:
                            self.session_breakout = -1
                            self.session_level = session_low
                            self.session_breakout_timestamp = current_time
                            self.session_breakout_confirmed = False
                            self.session_breakout_failed = False
                if self.session_breakout == -1:
                    # Bearish BO Confirmed
                    if self.session_breakout_confirmed is False \
                    and self.session_breakout_failed is False \
                    and df["Close"] < low.loc[self.session_breakout_timestamp]:
                        self.session_breakout_confirmed = True
                    # Bearish BO Failed
                    if self.session_breakout_failed is False \
                    and df["Close"] > session_low \
                    and df["Close"] > open.loc[self.session_breakout_timestamp]:
                        self.session_breakout_failed = True

        return \
        self.session_level_break, \
        self.session_breakout, self.session_level, \
        self.session_breakout_timestamp, \
        self.session_breakout_confirmed, \
        self.session_breakout_failed 

    def daily_inside_bar(
            self, 
            df: Series, 
            yday_high: Series, 
            yday_low: Series,
            yday_open: Series,
            yday_close: Series,
            yday_hclose: Series,
            yday_lclose: Series,
            iday_idx: Series,
            iday_high: Series,
            iday_low: Series
            ):
        """Return index of daily trading range"""
        inside_day = False
        idx = int(df["Idx"])
        if df["Day_Idx"] > 0 and df["Iday_Idx"] == 0:
            yday_open_close_max = max([df["Yday_Close"],df["Yday_Open"]])
            yday_open_close_min = min([df["Yday_Close"],df["Yday_Open"]])
            if self.dmb_range_high is None and self.dmb_range_low is None:
                # Store Daily Mother Bar range and key levels
                self.dmb_range_high = yday_high.iloc[idx-1]
                self.dmb_range_low = yday_low.iloc[idx-1]
                self.dmb_range_open = yday_open.iloc[idx-1]
                self.dmb_range_close = yday_close.iloc[idx-1]
                self.dmb_range_hclose = yday_hclose.iloc[idx-1]
                self.dmb_range_lclose = yday_lclose.iloc[idx-1]
                
                # Use Iday Index to go 2 days back to Mother Bar day
                yday_end_iday_idx = int(iday_idx.iat[idx-1])
                yday_2_end_iday_idx = iday_idx.iat[(int(idx-2-yday_end_iday_idx))]
                yday_2_start_idx = int(idx - 2 - yday_2_end_iday_idx - yday_end_iday_idx)
                yday_2_end_idx = int(yday_2_start_idx + yday_2_end_iday_idx)
                # Get highs for the day
                h_window = iday_high.iloc[yday_2_start_idx: yday_2_end_idx]
                # Get copy of np array with iday indexes for max high in the session 
                dmbh_iday_idx_arr = np.where(h_window == h_window.max())[0].copy()
                # Get index of max high first occurence 
                self.h_idx = int(yday_2_start_idx + dmbh_iday_idx_arr[0])
                
                l_window = iday_low.iloc[yday_2_start_idx:yday_2_end_idx]
                dmbl_iday_idx_arr = np.where(l_window == l_window.min())[0].copy()
                self.l_idx = int(yday_2_start_idx + dmbl_iday_idx_arr[0])

            if self.dmb_range_high is not None and self.dmb_range_low is not None\
                and yday_open_close_max < self.dmb_range_high and yday_open_close_min > self.dmb_range_low:
                # If yday open and close within previous days high and low, then yday is an inside bar
                pass
            else:
                self.dmb_range_high = None 
                self.dmb_range_low = None
                self.dmb_range_open = None
                self.dmb_range_close = None
                self.dmb_range_hclose = None
                self.dmb_range_lclose = None
                self.h_idx = None
                self.l_idx = None
        if self.dmb_range_high is not None and self.dmb_range_low is not None:
            inside_day = True

        return inside_day, self.h_idx, self.dmb_range_high, self.l_idx, self.dmb_range_low

    def consolidation(
            self, 
            df: Series, 
            slope_angle_threshold: int,
            slow_sma_slope_sma: str,
            bod_sma_slope: str
            ):
        """Returns where current price action has no trend"""
        idx = df["Idx"]
        slope_angles = [
            df[slow_sma_slope_sma],
            df[bod_sma_slope] 
            ]
        if max(slope_angles) < slope_angle_threshold \
        and min(slope_angles) > -slope_angle_threshold:
            return True
        else:
            return False
       
    def fx_sessions_today(self, df: Series):
        """Returns the Timestamps of the start 
        and end of current day's Global FX Sessions"""
        session = {
            "FX_Open": None,
            "FX_Close": None,
            "TYO_Open": None,
            "TYO_Close": None,
            "LDN_Open": None,
            "LDN_Close": None,
            "NY_Open": None,
            "NY_Close": None,
        }
        ts = Timestamp(df.name)
        if ts.hour == 17 and ts.minute == 15:
            self.today_fx_open = ts

        if self.today_fx_open:
            session["FX_Open"] = self.today_fx_open # 17:15 EST
            session["FX_Close"] = \
                self.today_fx_open + Timedelta(hours=23,minutes=45) # 17:00 EST
            session["TYO_Open"] = \
                self.today_fx_open + Timedelta(hours=1,minutes=45) # 19:00 EST
            session["TYO_Close"] = \
                self.today_fx_open + Timedelta(hours=10, minutes=45) # 04:00 EST
            session["LDN_Open"] = \
                self.today_fx_open + Timedelta(hours=8, minutes=45) # 02:00 EST
            session["LDN_Close"] = \
                self.today_fx_open + Timedelta(hours=17, minutes=45) # 11:00 EST
            session["NY_Open"] = \
                self.today_fx_open + Timedelta(hours=13, minutes=45) # 07:00 EST
            session["NY_Close"] = \
                self.today_fx_open + Timedelta(hours=23,minutes=45) # 17:00 EST

        return session

    def fx_session_high_low(self, df: Series, high: Series, low: Series):
        """Return the highest/lowest price (midpoint) for each FX Session"""
        # Tokyo Session
        if df.name >= df["Session"]["TYO_Open"] \
        and df.name < df["Session"]["LDN_Open"]:
            self.tokyo_high = high.loc[df["Session"]["TYO_Open"]:df.name].max()
            self.tokyo_low = low.loc[df["Session"]["TYO_Open"]:df.name].min()
        # London Session
        if df.name >= df["Session"]["LDN_Open"] \
        and df.name < df["Session"]["NY_Open"]:
            self.london_high = high.loc[df["Session"]["LDN_Open"]:df.name].max()
            self.london_low = low.loc[df["Session"]["LDN_Open"]:df.name].min()
        # New York Session
        if df.name >= df["Session"]["NY_Open"] \
        and df.name < df["Session"]["NY_Close"]:
            self.new_york_high = high.loc[df["Session"]["NY_Open"]:df.name].max()
            self.new_york_low = low.loc[df["Session"]["NY_Open"]:df.name].min()
        return \
            self.tokyo_high, self.tokyo_low,\
            self.london_high, self.london_low,\
            self.new_york_high, self.new_york_low\

    def fx_session_range(self, df: Series):
        """Returns whether price is trading in an FX Session's range"""
        is_range_bound = False
        current_time = df.name

        if current_time >= df["Session"]["TYO_Open"] \
        and current_time < df["Session"]["LDN_Open"]:
            if df["Close"] <= df["NY_High"] \
            and df["Close"] >= df["NY_Low"]:
                is_range_bound = True
        elif current_time >= df["Session"]["LDN_Open"] \
        and current_time < df["Session"]["NY_Open"]:
            if df["Close"] <= df["TYO_High"] \
            and df["Close"] >= df["TYO_Low"]:
                is_range_bound = True
        elif current_time >= df["Session"]["NY_Open"] \
        and current_time < df["Session"]["NY_Close"]:
            if df["Close"] <= df["LDN_High"] \
            and df["Close"] >= df["LDN_Low"]:
                is_range_bound = True
        return is_range_bound
            

class Pattern():
    """Class for custom chart patterns"""
    def __init__(
            self, 
            open: Series, high: Series, low: Series, close: Series, 
            range: Series, body: Series
            ) -> None:
        self.open = open
        self.high = high
        self.low = low 
        self.close = close
        self.range = range
        self.body = body
        self.mother_bar = None
        self.mb_high = None
        self.mb_low = None

    def current_bar(self, df: Series):
        return 1 if df["Close"] > df["Open"] else \
                -1 if df["Close"] < df["Open"] else 0

    def hammer(self, df: Series):
        """Returns a boolean on whether a hammer candlestick pattern occured"""

        if self.current_bar(df) == 1:
            if (df["LWick"] >= (df["Body"] * 2)) \
                and df["Body"] > df["UWick"]:
                return True
        elif self.current_bar(df) == -1:
            if (df["LWick"] >= (df["Body"] * 2)) \
                and df["Body"] > df["UWick"]:
                return True
    def bullish_pinbar(self, df: Series):
        """Returns a boolean on whether a bullish pin bar pattern occured"""
        if (df["LWick"] >= (df["Body"] * 2)) \
        and df["Close_Pct_High"] < 0.45:
            return True
        else:
            False
        
    def bearish_pinbar(self, df: Series):
        """Returns a boolean on whether a bearish pin bar pattern occured"""
        if (df["UWick"] >= (df["Body"] * 2)) \
        and df["Close_Pct_High"] > 0.55:
            return True
        else:
            False
    
    def shooting_star(self, df: Series):
        """Returns a boolean on whether a shooting star pattern occured"""
        if  df["UWick"] >= 2 * df["Body"]:
            if self.current_bar(df) == -1: 
                if df["Body"] >= df["LWick"]:
                    return True
            elif self.current_bar(df) == 1:
                if df["Body"] >= df["LWick"]:
                    return True
            
    def bullish_engulfing(self, df: Series):
        """Returns a boolean on whether a bullish engulfing pattern occured"""
        if self.current_bar(df) == 1 and df["Range"] > df["ATR"]:
            idx = int(df["Idx"])
            if idx > 0:
                if self.close.iloc[idx-1] < self.open.iloc[idx-1] \
                and df["Open"] <= self.close.iloc[idx-1] \
                and df["Close"] >= self.open.iloc[idx-1] \
                and df["High"] > self.high.iloc[idx-1] \
                and df["Low"] < self.low.iloc[idx-1]:
                    return True
                
    def bearish_engulfing(self, df: Series):
        """Returns a boolean on whether a bearish engulfing pattern occured"""
        if self.current_bar(df) == -1 and df["Range"] > df["ATR"]:
            idx = int(df["Idx"])
            if idx > 0:
                if self.close.iloc[idx-1] > self.open.iloc[idx-1] \
                and df["Open"] >= self.close.iloc[idx-1] \
                and df["Close"] <= self.open.iloc[idx-1] \
                and df["High"] > self.high.iloc[idx-1] \
                and df["Low"] < self.low.iloc[idx-1]:
                    return True
                
    def dark_cloud_cover(self, df: Series):
        """Returns a boolean on whether a dark cloud cover pattern occured"""
        idx = int(df["Idx"])
        if idx > 0:
            prev_close = self.close.iloc[idx-1]
            prev_open = self.open.iloc[idx-1]
            prev_high = self.high.iloc[idx-1]
            prev_body = prev_close - prev_open
            if self.current_bar(df) == -1 and df["Range"] > df["ATR"]:
                if prev_close > prev_open \
                and df["Open"] > prev_high \
                and df["Close"] <= (prev_close - (0.5 * prev_body)):
                    return True
                elif prev_close > prev_open \
                and df["High"] > prev_high \
                and df["Close"] <= (prev_close - (0.5 * prev_body)) \
                and df["Close"] >= prev_open \
                and df["Body"] > df["LWick"]:
                    return True

    def piercing(self, df: Series):
        """Returns a boolean on whether a piercing pattern occured"""
        idx = int(df["Idx"])
        if idx > 0:
            prev_close = self.close.iloc[idx-1]
            prev_open = self.open.iloc[idx-1]
            prev_low = self.low.iloc[idx-1]
            prev_body = abs(prev_close - prev_open)
            if self.current_bar(df) == 1 and df["Range"] > df["ATR"]:
                if prev_close < prev_open \
                and df["Open"] < prev_low \
                and df["Close"] >= (prev_open - (0.5 * prev_body)):
                    return True
                elif prev_close < prev_open \
                and df["Low"] < prev_low \
                and df["Close"] < prev_open \
                and df["Close"] >= (prev_open - (0.5 * prev_body)) \
                and df["Body"] > df["UWick"]:
                    return True
                

    def bearish_bb_reversal_c1(
            self,
            df: Series,
            bbu: Series,
            ):
        """
        Bearish BBR Case 1 (Classic BB Reversal)
        - Previous close above upper band 
        - Current close below upper band
        - Close above top 20% of the candle range
        """
        idx = int(df["Idx"])
        # base signal conditions
        if self.close.iloc[idx-1] > self.open.iloc[idx-1] \
        and df["Close"] < df["BB_Upper_16_2"]:
            # prev close above BBU 
            # current close below BBU near candle lows
            if self.close.iloc[idx-1] > bbu.iloc[idx-1]:
                if df["Close_Pct_High"] > 0.66:
                    return True
                elif self.close.iloc[idx-1] - df["Close"] / \
                self.body.iloc[idx-1] > 0.80:
                    return True
                
    def bearish_bb_reversal_c2(
            self,
            df: Series
            ):
        """
        Bearish BBR Case 2 (Pinbar Reversal)
        - Price sharply retraces at key level
        - Body inside bollinger band
        - High spikes outside band
        """
        idx = int(df["Idx"])
        lower_candle_range = 0.66 if self.current_bar(df) == -1 else 0.50
        # pinbar reversal pattern
        if df["UWick"] >= (df["Body"] * 2) \
        and df["High"] > df["BB_Upper_16_2"] \
        and df["Open"] < df["BB_Upper_16_2"] \
        and df["Close"] < df["BB_Upper_16_2"] \
        and df["Close"] > df["SMA16"] \
        and df["Close_Pct_High"] > lower_candle_range:
            # sig_high
            if df["IHR"] == True:
                    return True
            # yday_high
            if df["High"] > df["Yday_High"] \
                and df["Close"] < df["Yday_High"]:
                return True
            # support level
            if df["S_R"] == 1 \
            and df["IHR"] is None:
                return True
        
    def bearish_bb_reversal_c3(
            self,
            df: Series
            ):
        """
        Bearish BBR Case 3 (Price Exhaustion)
        Price open and close above Upper Band
        """
        # Candle outside BBL
        if df["Open"] > df["BB_Upper_16_2"] \
        and df["Close"] > df["BB_Upper_16_2"] \
        and df["Close_Pct_DHigh"] < 0.50 \
        and df["Close_Pct_SMA"] > 0.1 \
        and df["Range"] > df["ATR"] * 0.5:
            return True

    def bearish_bb_reversal_c4(
            self,
            df: Series,
            ):
        """
        Bearish BBR Case 4 (Mean Reversion)
        Price extended > 0.30% of SMA16 & bar closes near Low
        """
        idx = int(df["Idx"])
        if df["High_Pct_SMA"] > 0.3 \
        and df["Bear_BBR_C3"] is None \
        and df["High"] > df["BB_Upper_16_2"]:
            if df["RSI_DVG"] == True \
            and df["High"] > self.high.iloc[idx-1] \
            and df["Close"] < self.high.iloc[idx-1]:
                return True
        
        
    def bearish_bb_reversal_v2(self, df:Series):
        """All bearish bb reversal signals"""
        signals = any([
            df["Bear_BBR_C1"],
            df["Bear_BBR_C2"],
            df["Bear_BBR_C3"],
            df["Bear_BBR_C4"]
        ])
        return signals


    def bullish_bb_reversal_c1(
            self,
            df: Series,
            bbl: Series,
            ):
        """
        Bullish BBR Case 1 (Classic BB Reversal)
        - Previous close under lower band 
        - Current close above lower band
        - Close above top 20% of the candle range
        """
        idx = int(df["Idx"])
        # base signal conditions
        if self.close.iloc[idx-1] < self.open.iloc[idx-1] \
        and df["Close"] > df["BB_Lower_16_2"]:
            # prev open below BBL and close above BBL and candle highs
            if self.close.iloc[idx-1] < bbl.iloc[idx-1]:
                if df["Close_Pct_High"] < 0.34:
                    return True
                elif df["Close"] - self.close.iloc[idx-1] /\
                self.body.iloc[idx-1] > 0.80:
                    return True
                
    def bullish_bb_reversal_c2(
            self,
            df: Series
            ):
        """
        Bullish BBR Case 2 (Pinbar Reversal)
        - Price sharply retraces at key level
        - Body inside bollinger band
        - Low spikes outside band
        """
        idx = int(df["Idx"])
        upper_candle_range = 0.34 if self.current_bar(df) == 1 else 0.50
        # pinbar reversal pattern
        if df["LWick"] >= (df["Body"] * 2) \
        and df["Low"] < df["BB_Lower_16_2"] \
        and df["Open"] > df["BB_Lower_16_2"] \
        and df["Close"] > df["BB_Lower_16_2"] \
        and df["Close"] < df["SMA16"] \
        and df["Close_Pct_High"] < upper_candle_range:
            # sig_low
            if df["ILR"] == True:
                    return True
            # yday_low
            if df["Low"] < df["Yday_Low"] \
                and df["Close"] > df["Yday_Low"]:
                return True
            # support level
            if df["S_R"] == 3 \
            and df["ILR"] is None:
                return True

    def bullish_bb_reversal_c3(
            self,
            df: Series
            ):
        """
        Bullish BBR Case 3 (Price Exhaustion)
        Price open and close below Lower Band
        """
        # Candle outside BBL
        if df["Open"] < df["BB_Lower_16_2"] \
        and df["Close"] < df["BB_Lower_16_2"] \
        and df["Close_Pct_DHigh"] > 0.50 \
        and df["Close_Pct_SMA"] > 0.1 \
        and df["Range"] > df["ATR"] * 0.5:
            return True

    def bullish_bb_reversal_c4(
            self,
            df: Series
            ):
        """
        Bullish BBR Case 4 (Mean Reversion)
        Price extended > 0.30% of SMA16 & bar closes near High
        """
        idx = int(df["Idx"])
        if df["Low_Pct_SMA"] > 0.3 \
        and df["Bull_BBR_C3"] is None \
        and df["Low"] < df["BB_Lower_16_2"]:
            if df["RSI_DVG"] == True \
            and df["Low"] < self.low.iloc[idx-1] \
            and df["Close"] > self.low.iloc[idx-1]:
                return True
            
    def bullish_bb_reversal_v2(self, df:Series):
        """All bullish bb reversal signals"""
        signals = any([
            df["Bull_BBR_C1"],
            df["Bull_BBR_C2"],
            df["Bull_BBR_C3"],
            df["Bull_BBR_C4"]
        ])
        return signals

    def intraday_low_reversal(self, df: Series):
        """
        Returns a boolean on whether price failed to close below the 
        lowest significant intraday low
        """

        idx = int(df["Idx"])
        if idx > 0:
            if df["Low"] < df["Sig_Low"] \
            and df["Close"] > df["Sig_Low"] \
            and df["Low"] == df["Iday_Low"]:
                return True

    def intraday_high_reversal(self, df: Series):
        """
        Returns a boolean on whether price failed to close above the highest
        significant high
        """

        idx = int(df["Idx"])
        if idx > 0:
            if df["High"] > df["Sig_High"] \
            and df["Close"] < df["Sig_High"] \
            and df["High"] == df["Iday_High"]:
                return True
            
    def support_resistance(
            self, 
            df: Series, 
            sig_high: Series, 
            sig_low: Series
            ):
        """Return whether price failed at or broke through a significant level
        
        - 1 = Resistance Test
        - 2 = Resistance Break
        - 3 = Support Test
        - 4 = Support Break
        """
        idx = int(df["Idx"])
        start = idx - df["Iday_Idx"]
        sig_h = sig_high.iloc[start:idx+1].unique()
        sig_l = sig_low.iloc[start:idx+1].unique()
        s_r = None
        s_r_level = None
        # # Sig_Highs
        if len(sig_h) > 0:
            for i in range(len(sig_h)):
                if df["Open"] < sig_h[i]:
                    if df["High"] >= sig_h[i] and df["Close"] < sig_h[i]:
                        s_r = 1
                        s_r_level = sig_h[i]
                    elif df["Close"] > sig_h[i]:
                        s_r = 2
                        s_r_level = sig_h[i]
                if df["Open"] > sig_h[i]:
                    if df["Low"] <= sig_h[i] and df["Close"] > sig_h[i]:
                        s_r = 3
                        s_r_level = sig_h[i]
                    elif df["Close"] < sig_h[i]:
                        s_r = 4
                        s_r_level = sig_h[i]
        # Sig_Lows
        if len(sig_l) > 0:
            for i in range(len(sig_l)):
                if df["Open"] < sig_l[i]:
                    if df["High"] >= sig_l[i] and df["Close"] < sig_l[i]:
                        s_r = 1 
                        s_r_level = sig_l[i]
                    elif df["Close"] > sig_l[i]:
                        s_r = 2 
                        s_r_level = sig_l[i]
                if df["Open"] > sig_l[i]:
                    if df["Low"] <= sig_l[i] and df["Close"] > sig_l[i]:
                        s_r = 3 
                        s_r_level = sig_l[i]
                    elif df["Close"] < sig_l[i]:
                        s_r = 4 
                        s_r_level = sig_l[i]
        return s_r, s_r_level

    def bb_breakout(
            self, df: Series, 
            bb_lower: str = "BB_Lower_16_2",
            bb_upper: str = "BB_Upper_16_2",
            pipsize: float = 0.0001
            ):
        """Returns whether bollinger band breakout occured"""

        bbu_bo = False
        bbl_bo = False
        # only need to check 1 because both are same size
        if bb_lower is not None:
            # bearish breakout
            if self.current_bar(df) == -1 and df["Close"] < df[bb_lower]:
                if df["Range"] >= (1.25 * df["ATR"]) \
                and df["Close_Pct_High"] > 0.75 \
                and (df[bb_lower] - df["Close"]) > pipsize:
                    bbl_bo = True
            # bullish breakout
            elif self.current_bar(df) == 1 and df["Close"] > df[bb_upper]:
                if df["Range"] >= (1.25 * df["ATR"]) \
                and df["Close_Pct_High"] < 0.25 \
                and (df["Close"] - df[bb_upper]) > pipsize:
                    bbu_bo = True
        return bbu_bo, bbl_bo
        
    def trend_continuation(self, 
        df: Series
        ):
        """
        Continuation of bullish trend from SMA support

        #### Trading Conditions
        - TP = 1:1 (ATR) R/R SMA16
        """
        bullish_trend_continuation = False
        bearish_trend_continuation = False
        up_slope = 11.25
        down_slope = -11.25
        idx = int(df["Idx"])
        # Uptrend or Consolidation
        # Bullish SMA Pullback
        if df["Close"] < df["BB_Upper_16_2"]:
            if self.current_bar(df) == 1:
                if df["Open"] < df["SMA16"] \
                and df["Close"] > df["SMA16"] \
                and df["Close_Pct_High"] < 0.34 \
                and df["SMA16_Slope"] > up_slope:
                    bullish_trend_continuation = True
                if df["Open"] < df["SMA32"] \
                and df["Close"] > df["SMA32"] \
                and df["Close_Pct_High"] < 0.34 \
                and df["SMA32_Slope"] > up_slope:
                    bullish_trend_continuation = True
        # Downtrend or Consolidation
        # Bearish SMA Pullback
        if df["Close"] > df["BB_Lower_16_2"]:
            if self.current_bar(df) == -1:
                if df["Open"] > df["SMA16"] \
                and df["Close"] < df["SMA16"] \
                and df["Close_Pct_High"] > 0.66 \
                and df["SMA16_Slope"] < down_slope:
                    bearish_trend_continuation = True
                if df["Open"] > df["SMA32"] \
                and df["Close"] < df["SMA32"] \
                and df["Close_Pct_High"] > 0.66 \
                and df["SMA32_Slope"] < down_slope:
                    bearish_trend_continuation = True

        # return data
        return bullish_trend_continuation, bearish_trend_continuation
    
    def pinbar_fail(
            self, 
            df: Series,
            bull_pinbar: Series,
            bear_pinbar: Series
            ):
        
        idx = int(df["Idx"])
        bullish_pb_fail = False
        bearish_pb_fail = False

        """Failure of bearish pinbar"""
        # Failed Shooting_Star
        if bear_pinbar.iloc[idx-1] is True \
        and self.current_bar(df) == 1 \
        and (df["Close"] - self.low.iloc[idx-1]) / \
        self.range.iloc[idx-1] > 0.75 \
        and df["Close_Pct_High"] < 0.34 \
        and df["Close_Pct_DHigh"] > 0.66:
            bullish_pb_fail = True
        # Failed Hammer
        if bull_pinbar.iloc[idx-1] is True \
        and self.current_bar(df) == -1 \
        and (self.high.iloc[idx-1] - df["Close"]) / \
        self.range.iloc[idx-1] > 0.75 \
        and df["Close_Pct_High"] > 0.66 \
        and df["Close_Pct_DHigh"] < 0.34:
            bearish_pb_fail = True
        return bullish_pb_fail, bearish_pb_fail
    
    def inside_bar(
            self, 
            df: Series,
            ):
        """Return whether the open and close of the current bar
        is inside the high and low of the previous bar"""
        idx = int(df["Idx"])
        open_close_max = max([df["Open"],df["Close"]])
        open_close_min = min([df["Open"],df["Close"]])
        prev_high = self.high.iloc[idx-1]
        prev_low = self.low.iloc[idx-1]
        inside_bar = False
        #
        if self.mother_bar is None and open_close_max < prev_high and open_close_min > prev_low:
            self.mother_bar = int(idx-1)
            self.mb_high = self.high.iloc[self.mother_bar]
            self.mb_low = self.low.iloc[self.mother_bar]
            inside_bar = True
        elif self.mother_bar is not None and open_close_max < self.mb_high \
        and open_close_min > self.mb_low:
            inside_bar = True 
        else:
            self.mother_bar = None
            self.mb_high = None 
            self.mb_low = None
        #
        return inside_bar, self.mother_bar, self.mb_high, self.mb_low


    def bullish_sma_breakout(self, df: Series):
        """
        Breakout of SMA consolidation or bearish retracement
        continuing uptrend
        """
        idx = int(df["Idx"])
        sma_all = Series([df["SMA4"], df["SMA16"], df["SMA32"]])
        body_4 = self.body.iloc[idx-4:idx]
        close_4 = self.close.iloc[idx-4:idx]
        open_4 = self.close.iloc[idx-4:idx]
        if df["Open"] < sma_all.min() \
        and df["Close"] > sma_all.max() \
        and df["Body"] > body_4.max() \
        and df["Close"] > close_4.max() \
        and df["Low"] < open_4.min() \
        and df["Close_Pct_High"] < 0.34 \
        and df["SMA32_Slope_SMA"] < -11.25 \
        and df["SMA4_Slope_SMA"] > 11.25:
            return True

    def bearish_sma_breakout(self, df: Series):
        """
        Breakout of SMA consolidation or bullish retracement
        continuing downtrend
        """
        idx = int(df["Idx"])
        sma_all = Series([df["SMA4"], df["SMA16"], df["SMA32"]])
        body_4 = self.body.iloc[idx-4:idx]
        close_4 = self.close.iloc[idx-4:idx]
        open_4 = self.close.iloc[idx-4:idx]
        if df["Open"] > sma_all.max() \
        and df["Close"] < sma_all.min() \
        and df["Body"] > body_4.max() \
        and df["Close"] < close_4.min() \
        and df["High"] > open_4.max() \
        and df["Close_Pct_High"] > 0.66 \
        and df["SMA32_Slope_SMA"] > 11.25 \
        and df["SMA4_Slope"] < -11.25:
            return True
                       

    def bullish_momentum(
            self, 
            df: Series,
            atr: Series,
            close_gt_sma: str,
            period: int
            ):
            """
            Returns if price is rapidly increasing above the average price
            """
            idx = int(df["Idx"])
            open_close_max = max([df["Open"],df["Close"]])
            open_close_min = min([df["Open"],df["Close"]])
            prev_high = self.high.iloc[idx-1]
            prev_low = self.low.iloc[idx-1]
            if df["Momentum"] == 1 \
            and open_close_max < prev_high \
            and open_close_min > prev_low:
                if atr.iloc[idx] > atr.iloc[idx-1]:
                    return True
                elif df[close_gt_sma] >= period:
                    return True
            
    def bearish_momentum(
            self, 
            df: Series,
            atr: Series,
            close_lt_sma: str,
            period: int
            ):
            """
            Returns if price is rapidly decreasing below the average price
            """
            idx = int(df["Idx"])
            open_close_max = max([df["Open"],df["Close"]])
            open_close_min = min([df["Open"],df["Close"]])
            prev_high = self.high.iloc[idx-1]
            prev_low = self.low.iloc[idx-1]
            if df["Momentum"] == -1 \
            and open_close_max <= prev_high \
            and open_close_min >= prev_low:
                if atr.iloc[idx] > atr.iloc[idx-1]:
                    return True
                elif df[close_lt_sma] >= period:
                    return True

    def bar_overlap(
            self, 
            df: Series,
        ):
        """Return a numerical value indicating 
        the strength of directionless or rangebound movemeent
        """
        idx = int(df["Idx"])
        overlap = 1
        prev_body = abs(self.open.iloc[idx-1] - self.close.iloc[idx-1])
        # overlapping / non-trend bars
        if prev_body > 0:
            if self.current_bar(df) == 1 \
            and self.close.iloc[idx-1] > self.open.iloc[idx-1]: 
                overlap = df["LWick"] / prev_body
            elif self.current_bar(df) == -1 \
            and self.close.iloc[idx-1] < self.open.iloc[idx-1]: 
                overlap = df["UWick"] / prev_body
        # return data
        return overlap
    
    def extreme_momentum_v2(
            self,
            df:Series
            ):
        """Return whether there is extreme price momentum"""
        idx = int(df["Idx"])
        BOD_idx = idx - df["Iday_Idx"] # beginning of day
        yday_close = self.close.iloc[BOD_idx-1]

        bullish_extreme_momentum_v2 = False 
        bearish_extreme_momentum_v2 = False 
        bbu_gap = (df["Close"] - df["BB_Upper_16_2"])
        bbl_gap = (df["BB_Lower_16_2"] - df["Close"])
        
        # BullishMomemntum
        if df["Close"] > df["Yday_High"] \
        and df["SMA4_Slope"] > 45:
            if df["Low"] < df["SMA4"] \
            and df["Close"] > df["SMA4"] \
            and df["Range"] < self.range.iloc[idx-1] * 2:
                if bbu_gap > 0:
                    if bbl_gap / df["ATR4"] < 0.33:
                        bullish_extreme_momentum_v2 = True
                else:
                    bullish_extreme_momentum_v2 = True
        # BearishMomentum
        if df["Close"] < df["Yday_Low"] \
        and df["SMA4_Slope"] < -45:
            if df["High"] > df["SMA4"] \
            and df["Close"] < df["SMA4"] \
            and df["Range"] < self.range.iloc[idx-1] * 2:
                if bbl_gap > 0:
                    if bbl_gap / df["ATR4"] < 0.33:
                        bearish_extreme_momentum_v2 = True
                else:
                    bearish_extreme_momentum_v2 = True
        # return tuple
        return bullish_extreme_momentum_v2, bearish_extreme_momentum_v2

    def bullish_pullback(
            self, 
            df: Series, 
            fast_sma: Series,
            fast_sma_slope: str ,
            slow_sma: Series,
            slow_sma_slope: str,
            slope_trend: str = "Trend_16_32"
            ):
        """Pullback prior to move high in uptrend"""
        idx = int(df["Idx"])
        if df[slope_trend] == 1:
            if self.close.iloc[idx-1] > fast_sma.iloc[idx-1] \
            and self.close.iloc[idx] < fast_sma.iloc[idx] \
            and df[fast_sma_slope] >= 22.5:
                return True
            if self.close.iloc[idx-1] > slow_sma.iloc[idx-1] \
            and self.close.iloc[idx] < slow_sma.iloc[idx] \
            and df[slow_sma_slope] >= 22.5:
                return True

    def bearish_pullback(
            self, 
            df: Series,
            fast_sma: Series,
            fast_sma_slope: str ,
            slow_sma: Series,
            slow_sma_slope: str,
            slope_trend: str = "Trend_16_32"
            ):
        """Pullback prior to move lower in downtrend"""
        idx = int(df["Idx"])
        if df[slope_trend] == -1:
            if self.close.iloc[idx-1] < fast_sma.iloc[idx-1] \
            and self.close.iloc[idx] > fast_sma.iloc[idx] \
            and df[fast_sma_slope] <= -22.5:
                return True
            if self.close.iloc[idx-1] < slow_sma.iloc[idx-1] \
            and self.close.iloc[idx] > slow_sma.iloc[idx] \
            and df[slow_sma_slope] <= -22.5:
                return True

    def iday_range_breakout(self, df: Series, ib: Series, mbh: Series, mbl: Series):
        """Return if price broke out from an intraday range"""
        idx = int(df["Idx"])
        bullish_range_bo = False 
        bearish_range_bo = False
        if ib.iat[idx-1] == True and ib.iat[idx] == False \
        and self.range.iat[idx] > (mbh.iat[idx-1] - mbl.iat[idx-1]) * 1.5 \
        and self.range.iat[idx] > df["ATR4"]:
            if self.close.iat[idx] > mbh.iat[idx-1] \
            and df["Close_Pct_High"] < 0.34:
                bullish_range_bo = True
            if self.close.iat[idx] < mbl.iat[idx-1] \
            and df["Close_Pct_High"] > 0.66:
                bearish_range_bo = True
        return bullish_range_bo, bearish_range_bo
    
    def session_level_break_signal(self, df: Series, slb: Series):
        idx = df["Idx"]
        if slb.iat[idx] is not NaT \
        and slb.iat[idx] != slb.iat[idx-1] \
        and slb.iat[idx] != df["SBO_TS"]:
            return True
        else:
            return False
    
    def session_breakout_signal(self, df: Series, sbo_ts: Series):
        idx = df["Idx"]
        if sbo_ts.iat[idx] is not None \
        and sbo_ts.iat[idx] > sbo_ts.iat[idx-1]:
            return True
        if sbo_ts.iat[idx-1] is NaT \
        and sbo_ts.iat[idx] is not NaT:
            return True
        else:
            return False

    def session_breakout_failed_signal(self, df: Series, sbo_failed: Series):
        idx = df["Idx"]
        if sbo_failed.iat[idx-1] == False \
        and sbo_failed.iat[idx] == True:
            return True
        else:
            return False
        
    def session_false_breakout_reversal(self, df: Series, slb_signal: Series):
        """Return whether false breakout has become a reversal signal"""
        idx = df["Idx"]
        if slb_signal.iat[idx-1] == True:
            # bullish reversal
            if self.close.iat[idx-1] < df["SBO_Level"] \
            and self.close.iat[idx] > self.open.iat[idx-1]:
                return 1
            elif self.close.iat[idx-1] > df["SBO_Level"] \
            and self.close.iat[idx] < self.open.iat[idx-1]:
                return -1
            else:
                return 0
        elif df["SLB"] is not NaT and df["SBO_TS"] is NaT:
            # bullish
            if self.open.iat[idx] < df["SBO_Level"] \
            and df["SBO"] == -2 \
            and df["Bull_BBR_C1"] == True:
                return 1
            # bearish
            elif self.open.iat[idx] > df["SBO_Level"] \
            and df["SBO"] == 2 \
            and df["Bear_BBR_C1"]:
                return -1
            else:
                return 0
        else:
            return 0
        
    # Breakout Strategy
        # Market order at close
        # Stop beyond the extreme of breakout candle
        # exit when price closes back into SMA8
        # exit if breakout turns into bollinger band reversal
        # exit if price closes back into session level
        # If entering breakout on pullback, then target is 61.8 fib

    # Session Break Strategy
        # limit order at previous session high if trend is down
        # limit order at previous low if trend is up
        # target
        # if session level if far away, could use "candle range breakout" setup instead
        # bollinger band reversal more likely after level break that is not a valid breakout