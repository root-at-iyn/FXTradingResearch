from pandas import Series, DataFrame, DatetimeIndex, to_datetime
from datetime import time
from math import sqrt, atan, pi

class Candle():
    """
    Class to return the properties of a time period derived from the OHLC

    Takes a Pandas Series of `OHLC` data, and returns the calculated 
    properties of the period (represented as candlestick on the chart). 
    This is designed to work with the pandas.apply() method and should set 
    `axis=1` to receive a series and apply to the column.
    """

    def __init__(self) -> None:
        pass 

    def body(self, df: Series) -> Series:
        """Returns the body of the candlestick"""

        return abs(df["Open"] - df["Close"])
    
    def range(self, df:Series) -> Series:
        """Returns the range of the candlestick"""

        return (df["High"] - df["Low"])
    
    def upper_wick(self, df: Series) -> Series:
        """Returns the upper wick of the candlestick"""

        if df["Close"] >= df["Open"]:
            wick = df["High"] - df["Close"]
        else:
            wick = df["High"] - df["Open"]
        
        return wick
    
    def lower_wick(self, df: Series) -> Series:
        """Returns the lower wick of the candlestick"""

        if df["Close"] <= df["Open"]:
            wick = df["Close"] - df["Low"]
        else:
            wick = df["Open"] - df["Low"]
        
        return wick

    def close_pct_high(self, df: Series):
        """Return the percentage of the candle's Close from the High"""

        if df["Range"] == 0:
            return df["Range"]
        else:
            return (df["High"] - df["Close"]) / df["Range"]

    def open_pct_high(self, df: Series):
        """Return the percentage of the candle's Open from the High"""

        if df["Range"] == 0:
            return df["Range"]
        else:
            return (df["High"] - df["Open"]) / df["Range"]


class Intraday():
    def __init__(self) -> None:
        self.index_count = 0
        self.dhigh = 0
        self.dlow = 0

    def index(self, df: Series, dt_index: DatetimeIndex, hr=16, min=45):
        """Returns the intraday index

        Takes in a DatetimeIndexed Series and specified time to set as the 
        start of the trading session, given by `hr` (hour) and `min` (minutes).
        The default is 17:15, which is the start of the FX trading session in
        IBKR (US/Eastern). 
        Returns the intraday index relative to the start of the trading session
        """

        idx = int(df["Idx"])
        EOD_time = time(hour=hr,minute=min)
        if idx > 0:
            if dt_index[idx-1].time() == EOD_time:
                self.index_count = 0
            else:
                self.index_count += 1   
        return self.index_count

    def high(self, df: Series):
        """Returns the high of the intraday session"""
        
        if df["Iday_Idx"] == 0:
            self.dhigh = df["High"]
        elif df["High"] > self.dhigh:
            self.dhigh = df["High"]
    
        return self.dhigh
        
    def low(self, df: Series):
        """Returns the low of the intraday session"""
        
        if df["Iday_Idx"] == 0:
            self.dlow = df["Low"]
        elif df["Low"] < self.dlow:
            self.dlow = df["Low"]
    
        return self.dlow
    
    def range(self, df: Series):
        """Returns the range of the intrday session"""
        
        return df["Iday_High"] - df["Iday_Low"]

    def close_pct_iday_high(self, df: Series):
        """Return the percentage of the Close from the Intraday High"""

        if df["Iday_Range"] == 0:
            return df["Iday_Range"]
        else:
            return (df["Iday_High"] - df["Close"]) / df["Iday_Range"]

    def open_pct_iday_high(self, df: Series):
        """Return the percentage of the Open from the Intraday High"""

        if df["Iday_Range"] == 0:
            return df["Iday_Range"]
        else:
            return (df["Iday_High"] - df["Open"]) / df["Iday_Range"]


class Indicator():
    def __init__(self) -> None:
        self.h = None
        self.yday_high = None
        self.l = None 
        self.yday_low = None
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
    
    def ADR(self, df: Series, period: int):
        """Returns the average daily range for `period` trading sessions"""

        if int(df["Iday_Idx"]) == 0 and int(df["Idx"]) > 0:
            self.daily_range.append(df["Yday_High"] - df["Yday_Low"])
            if len(self.daily_range) > period:
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
            lookback: int = 2, 
            run: int = 3,
            pipsize: int = 0.0001
        ):
        """Return the angle of the SMA slope"""

        idx = int(df["Idx"])
        if idx >= lookback:
            pipsize = 0.0001
            rise = (sma.iloc[idx] - sma.iloc[idx-lookback]) / pipsize
            slope = rise / run
            return atan(slope) * (180/pi)


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
                
    def bullish_bb_reversal(
            self, 
            df:Series, 
            bb_lower: Series, 
            atr: Series
            ):
        """
        Returns a boolean on whether a bullish bollinger band reversal occured
        """

        idx = int(df["Idx"])
        if idx > 0 and df["ADR"] > 0:
            prev_open = self.open.iloc[idx-1]
            prev_close = self.close.iloc[idx-1]
            # base signal condition
            if self.current_bar(df) ==1 and prev_close < prev_open \
                and prev_close < bb_lower.iloc[idx-1] \
                and df["Range"] > (prev_open - prev_close) * 0.50 \
                and df["Close_Pct_High"] <= 0.5 \
                and self.range.iloc[idx-1] > atr.iloc[idx-1]:
                return True


    def bearish_bb_reversal(
            self, 
            df:Series, 
            bb_upper: Series,
            atr: Series
            ):
        """
        Returns a boolean on whether a bearish bollinger band reversal occured
        """

        idx = int(df["Idx"])
        if idx > 0 and df["ADR"] > 0:
            prev_open = self.open.iloc[idx-1]
            prev_close = self.close.iloc[idx-1]
            # base signal condition
            if self.current_bar(df) ==-1 and prev_close > prev_open \
                and prev_close > bb_upper.iloc[idx-1] \
                and (df["Range"] > (prev_close - prev_open) * 0.50 \
                and df["Close_Pct_High"] >= 0.50) \
                and self.range.iloc[idx-1] > atr.iloc[idx-1]:
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
            if self.close.iloc[idx-1] > bbu.iloc[idx-1] \
            and df["Close_Pct_High"] > 0.80:
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
            if self.close.iloc[idx-1] < bbl.iloc[idx-1] \
            and df["Close_Pct_High"] < 0.20:
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
        
    def trend_continuation(self, df: Series):
        """
        Continuation of bullish trend from SMA support

        #### Trading Conditions
        - TP = 1:1 (ATR) R/R SMA16
        """
        bullish_trend_continuation = False
        bearish_trend_continuation = False
        # Uptrend or Consolidation
        if df["SMA_Trend"] in [0,2] \
        and df["SMA16"] > df["SMA32"] \
        and df["Close_Pct_High"] < 0.34:
            # SMA16
            if df["SMA16_Slope_SMA"] > 11.25 \
            and df["Low"] < df["SMA16"] \
            and df["Close"] > df["SMA16"]:
                if self.current_bar(df) == 1 \
                and df["Open"] > df["SMA16"]:
                    bullish_trend_continuation = True
                elif self.current_bar(df) == -1:
                    bullish_trend_continuation = True
            # SMA32
            if df["SMA32_Slope_SMA"] > 11.25 \
            and df["Low"] < df["SMA32"] \
            and df["Close"] > df["SMA32"]:
                if self.current_bar(df) == 1 \
                and df["Open"] > df["SMA32"]:
                    bullish_trend_continuation = True
                elif self.current_bar(df) == -1:
                    bullish_trend_continuation = True
        # Downtrend or Consolidation
        if df["SMA_Trend"] in [0,-2] \
        and df["SMA16"] < df["SMA32"] \
        and df["Close_Pct_High"] > 0.66:
            # SMA16
            if df["SMA16_Slope_SMA"] < -11.25 \
            and df["High"] > df["SMA16"] \
            and df["Close"] < df["SMA16"]:
                if self.current_bar(df) == -1 \
                and df["Open"] < df["SMA16"]:
                    bearish_trend_continuation = True
                elif self.current_bar(df) == 1:
                    bearish_trend_continuation = True
            # SMA32
            if df["SMA32_Slope_SMA"] < -11.25 \
            and df["High"] > df["SMA32"] \
            and df["Close"] < df["SMA32"]:
                if self.current_bar(df) == -1 \
                and df["Open"] < df["SMA32"]:
                    bearish_trend_continuation = True
                elif self.current_bar(df) == 1:
                    bearish_trend_continuation = True
        # return data
        return bullish_trend_continuation, bearish_trend_continuation

    def bullish_sma_breakout(self, df: Series):
        """
        Breakout of SMA consolidation or bearish retracement
        continuing uptrend
        """
        idx = int(df["Idx"])
        sma_all = Series([df["SMA4"], df["SMA16"], df["SMA32"]])
        body_4 = self.body.iloc[idx-4:idx]
        range_4 = self.range.iloc[idx-4:idx]
        high_4 = self.high.iloc[idx-4:idx]
        if df["Open"] < sma_all.min() \
        and df["Close"] > sma_all.max() \
        and df["Range"] > range_4.max() \
        and df["Body"] > body_4.max() \
        and df["Body"] > self.body.iloc[idx-1] * 2 \
        and df["Range"] > df["ATR"] * 1.25 \
        and df["Close"] > high_4.max() \
        and df["Close_Pct_High"] < 0.34:
            return True

    def bearish_sma_breakout(self, df: Series):
        """
        Breakout of SMA consolidation or bullish retracement
        continuing downtrend
        """
        idx = int(df["Idx"])
        sma_all = Series([df["SMA4"], df["SMA16"], df["SMA32"]])
        body_4 = self.body.iloc[idx-4:idx]
        range_4 = self.range.iloc[idx-4:idx]
        low_4 = self.low.iloc[idx-4:idx]
        if df["Open"] > sma_all.max() \
        and df["Close"] < sma_all.min() \
        and df["Range"] > range_4.max() \
        and df["Body"] > body_4.max() \
        and df["Body"] > self.body.iloc[idx-1] * 2 \
        and df["Range"] > df["ATR"] * 1.25 \
        and df["Close"] < low_4.max() \
        and df["Close_Pct_High"] > 0.66:
            return True
        
    def breakout_momentum(
            self, 
            df: Series, 
            sma4: Series,
            bbu_bo: Series,
            bullish_sma_bo: Series,
            bbl_bo: Series,
            bearish_sma_bo: Series
            ):
            """
            Momentum after a breakout
            """
            idx = int(df["Idx"])
            bullish_bo_momentum = False
            bearish_bo_momentum = False
            if idx > 3 and sma4 is not None:
                start = idx - df["Iday_Idx"]
                bull_bo = bbu_bo.iloc[start:idx]
                bull_sma_bo = bullish_sma_bo.iloc[start:idx]
                bear_bo = bbl_bo.iloc[start:idx]
                bear_sma_bo = bearish_sma_bo.iloc[start:idx]
                # breakouts
                # get timestamp of breakout
                bo_ts = None
                bo_sma_ts = None
                now = df.name
                for i in range(len(bull_bo)):
                    # bbu breakout
                    if bull_bo.iloc[i] == True:
                        bo_ts = bull_bo.iloc[i:i+1].index[0]
                        bullish_bo_momentum = True
                    # bullish sma breakout
                    if bull_sma_bo.iloc[i] == True:
                        bo_sma_ts = bull_sma_bo.iloc[i:i+1].index[0]
                        bullish_bo_momentum = True
                    # bbl breakout
                    if bear_bo.iloc[i] == True:
                        bo_ts = bear_bo.iloc[i:i+1].index[0]
                        bearish_bo_momentum = True
                    # bearish sma breakout
                    # if bear_sma_bo.iloc[i] == True:
                        bo_sma_ts = bear_sma_bo.iloc[i:i+1].index[0]
                        bearish_bo_momentum = True
                # get timestamp of the last breakout
                if all([bo_ts, bo_sma_ts]) and bo_ts is not None:
                    ts = max([bo_ts, bo_sma_ts])
                else:
                    ts = bo_ts if bo_ts is not None else bo_sma_ts                        
                # get window from start of breakout upto this candle
                sma4_window = sma4.loc[ts:now]
                close_window = self.close.loc[ts:now]
                # breakout within the same trading day
                # and price has not crossed sma4 since breakout
                for i in range(len(sma4_window)):
                    # Bullish case
                    if bullish_bo_momentum is True:
                        if close_window.iloc[i] < sma4_window.iloc[i]:
                            bullish_bo_momentum = False
                    # Bearish case
                    if bearish_bo_momentum is True:
                        if close_window.iloc[i] > sma4_window.iloc[i]:
                            bearish_bo_momentum = False
                            
            return bullish_bo_momentum, bearish_bo_momentum
                

    def bullish_trend_momentum(
            self, 
            df: Series
            ):
            """
            Bullish momentum during a retracement or uptrend
            """
            idx = int(df["Idx"])
            # low condition
            low_condition = None 
            if self.close.iloc[idx-1] > self.open.iloc[idx-1] \
            and df["Low"] < self.low.iloc[idx-1] \
            and df["Close"] > self.high.iloc[idx-1]:
                low_condition = True
            if df["Low"] > self.low.iloc[idx-1] \
            and df["Close"] > self.high.iloc[idx-1]:
                low_condition = True
            # sharp momentum along the SMA4 Slope
            if df["SMA4_Slope"] >= 45 \
            and low_condition is True:
                return True
            # SMA4 uptrend (covers SMA4 Slope pullbacks)
            elif df["SMA4_Slope"] > 22.5 \
            and low_condition is True \
            and df["Body"] > df["ATR"]:
                return True
            
    def bearish_trend_momentum(
            self, 
            df: Series
            ):
            """
            Bearish momentum during a retracement or uptrend
            """
            idx = int(df["Idx"])
            # high condition
            high_condition = None 
            if self.close.iloc[idx-1] < self.open.iloc[idx-1] \
            and df["High"] > self.high.iloc[idx-1] \
            and df["Close"] < self.low.iloc[idx-1]:
                high_condition = True
            if df["High"] < self.high.iloc[idx-1] \
            and df["Close"] < self.low.iloc[idx-1]:
                high_condition = True
            # sharp momentum along the SMA4 Slope
            if df["SMA4_Slope"] <= -45 \
            and high_condition is True:
                return True
            # SMA16 downtrend (covers SMA4 Slope pullbacks)
            elif df["SMA4_Slope"] < -22.5 \
            and high_condition is True \
            and df["Body"] > df["ATR"]:
                return True
                

    def trend_candle(self, df: Series):
        """
        Candlestick pattern in uptrend or downtrend

        - TP = 1:1 R/R (Range/ATR)
        """
        bullish_trend_candle = False
        bearish_trend_candle = False
        # CANDLESTICK PATTERNS
        bullish_candles = any(
            [df["Hammer"], df["Bull_Engulf"], df["Piercing"]])
        bearish_candles = any(
            [df["Shooting_Star"], df["Bear_Engulf"], df["Dark_Cloud"]])
        # Uptrend or Consolidation
        if df["SMA_Trend"] in [-1,0,2] \
        and bullish_candles == True \
        and df["Close"] > df["SMA32"] \
        and df["Range"] > df["ATR"] \
        and df["SMA32_Slope_SMA"] > 11.25 \
        and df["SMA16_Slope_SMA"] > df["SMA32_Slope_SMA"]:
            if self.current_bar(df) == 1:
                if df["Low"] < df["SMA32"]:
                    bullish_trend_candle = True
                if df["Low"] < df["SMA16"] \
                and df["Close"] > df["SMA16"]:
                    bullish_trend_candle = True
        # Downtrend or Consolidation
        if df["SMA_Trend"] in [1,0,-2] \
        and bearish_candles == True \
        and df["Close"] < df["SMA32"] \
        and df["Range"] > df["ATR"] \
        and df["SMA32_Slope_SMA"] < -11.25 \
        and df["SMA16_Slope_SMA"] < df["SMA32_Slope_SMA"]:
            if self.current_bar(df) == -1:
                if df["High"] > df["SMA32"]:
                    bearish_trend_candle = True
                if df["High"] > df["SMA16"] \
                and df["Close"] < df["SMA16"]:
                    bearish_trend_candle = True
        # return data
        return bullish_trend_candle, bearish_trend_candle
                
    def s_r_signal(
            self, 
            df: Series, 
            s_r: Series, 
            close_pct_high: Series, 
            s_r_level: Series
            ):
        """
        (TESTING ONLY)
        - S_R_Signal function is used to validate if buy or sell entry was hit
        - For raw_signal in live trading use S_R and S_R_Level
        - Limit order at S_R_Level
        """
        signal = None 
        entry = None
        idx = int(df["Idx"])
        # support
        if s_r.iloc[idx-1] == 3 \
        and close_pct_high.iloc[idx-1] < 0.50 \
        and df["Low"] < s_r_level.iloc[idx-1]:
            signal = s_r.iloc[idx-1]
            entry = s_r_level.iloc[idx-1]
        if s_r.iloc[idx-2] == 4 \
        and s_r.iloc[idx-1] == 2 \
        and close_pct_high.iloc[idx-1] < 0.34 \
        and df["Low"] < s_r_level.iloc[idx-1]:
            signal = s_r.iloc[idx-1]
            entry = s_r_level.iloc[idx-1]
        # resistance
        if s_r.iloc[idx-1] == 1 \
        and close_pct_high.iloc[idx-1] > 0.50 \
        and df["High"] > s_r_level.iloc[idx-1]:
            signal = s_r.iloc[idx-1]
            entry = s_r_level.iloc[idx-1]
        if s_r.iloc[idx-2] == 2 \
        and s_r.iloc[idx-1] == 4 \
        and close_pct_high.iloc[idx-1] > 0.66 \
        and df["High"] > s_r_level.iloc[idx-1]:
            signal = s_r.iloc[idx-1]
            entry = s_r_level.iloc[idx-1]
        return signal, entry
