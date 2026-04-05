from pandas import Series, to_datetime
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

    def index(self, df: Series, hr=17, min=15):
        """Returns the intraday index

        Takes in a DatetimeIndexed Series and specified time to set as the 
        start of the trading session, given by `hr` (hour) and `min` (minutes).
        The default is 17:15, which is the start of the FX trading session in
        IBKR (US/Eastern). 
        Returns the intraday index relative to the start of the trading session
        """

        # access row of series with row.name
        idx_time = to_datetime(df.name).time()
        roll = time(hour=hr,minute=min)
        if idx_time == roll:
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
        self.closes = []
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
    
    def SMA(self, df: Series, n: int):
        "Return the Simple Moving Average of Close prices over `n` periods"
        
        self.closes.append(df["Close"])
        if len(self.closes) > n:
            return sum(self.closes[-n:])/n
        
    def sma_standard_deviation(self, df: Series, sma_col_name: str, n: int):
        """Return the Standard Deviation of the last `n` SMA periods"""

        idx = int(df["Idx"])
        square_dev = [(x - df[sma_col_name])**2 for x in self.closes[((idx-n+1)):idx+1]]
        variance = sum(square_dev)/n
        standard_dev = sqrt(variance)
        return standard_dev
    
    def bollinger_band_upper(
            self, df: Series, k: int, sma_col_name: str, n: int = 16
            ):
        """
        Return the Bollinger Upper-Band value to `k` standard 
        deviations for the last `n` SMA periods
        """
        std = self.sma_standard_deviation(df, sma_col_name, n)
        if std is not None:
            return df[sma_col_name] + std * k

    def bollinger_band_lower(
            self, df: Series, k: int, sma_col_name: str, n: int = 16
            ):
        """
        Return the Bollinger Lower-Band value to `k` standard 
        deviations for the last `n` SMA periods
        """

        std = self.sma_standard_deviation(df, sma_col_name, n)
        if std is not None:
            return df[sma_col_name] - std * k

    def rsi(self, df: Series, period: int = 16):
        """
        Returns the Relative Strength Index (RSI)
        """

        idx = int(df["Idx"])
        if idx > 0:
            change = df["Close"] - self.closes[idx-1]
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
        idh = iday_high.round(4)
        
        # Reset significant intraday highs every trading day
        if df["Iday_Idx"] == 0:
            self.sig_high = set()

        if idx >= period:
            if round(df["Iday_High"],4) in self.sig_high:
                return df["Iday_High"]
            # Check if the Iday High has been the same for `period`
            # Check if the High Low was created in this session
            elif idh.iloc[idx] == idh.iloc[idx - period] \
                and day_idx.iloc[idx - period] == day_idx.iloc[idx]:
                self.sig_high.add(idh.iloc[idx])
                return df["Iday_High"]
            else:
                return None

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
        idl = iday_low.round(4)
        
        # Reset significant intraday lows every trading day
        if int(df["Iday_Idx"]) == 0:
            self.sig_low = set()

        if idx >= period:
            if round(df["Iday_Low"],4) in self.sig_low:
                return df["Iday_Low"]
            # Check if the Iday Low has been the same for `period`
            # Check if the Iday Low was created in this session
            elif idl.iloc[idx] == idl.iloc[idx - period] \
                and day_idx.iloc[idx - period] == day_idx.iloc[idx]:
                self.sig_low.add(idl.iloc[idx])
                return df["Iday_Low"]
            else:
                return None
    
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
            open: Series, high: Series, low: Series, close: Series
            ) -> None:
        self.open = open
        self.high = high
        self.low = low 
        self.close = close

    def current_bar(self, df: Series):
        return 1 if df["Close"] > df["Open"] else \
                -1 if df["Close"] < df["Open"] else 0

    def hammer(self, df: Series):
        """Returns a boolean on whether a hammer candlestick pattern occured"""

        if self.current_bar(df) == 1:
            if (df["LWick"] >= (df["Body"] * 2)) \
                and (df["Close_%High"] <= 0.34) \
                and df["Body"] > df["UWick"]:
                return True
            else:
                return False
        elif self.current_bar(df) == -1:
            if (df["LWick"] >= (df["Body"] * 2)) \
                and (df["Close_%High"] <= 0.34) \
                and df["Body"] > df["UWick"]:
                return True
            else:
                return False
        else:
            return False
    
    def shooting_star(self, df: Series):
        """Returns a boolean on whether a shooting star pattern occured"""
        if  df["UWick"] >= 2 * df["Body"]:
            if self.current_bar(df) == -1: 
                if df["Close_%High"] >= 0.66 \
                    and df["Body"] > df["LWick"]:
                    return True
            elif self.current_bar(df) == 1:
                if df["Close_%High"] >= 0.66 \
                and df["Body"] > df["LWick"]:
                    return True
            else:
                return False
            
    def bullish_engulfing(self, df: Series):
        """Returns a boolean on whether a bullish engulfing pattern occured"""
        if self.current_bar(df) == 1 and df["Range"] > df["ATR"]:
            idx = int(df["Idx"])
            if idx > 0:
                if self.close.iloc[idx-1] < self.open.iloc[idx-1] \
                and df["Open"] <= self.close.iloc[idx-1] \
                and df["Close"] >= self.open.iloc[idx-1]:
                    return True
                else:
                    return False
                
    def bearish_engulfing(self, df: Series):
        """Returns a boolean on whether a bearish engulfing pattern occured"""
        if self.current_bar(df) == -1 and df["Range"] > df["ATR"]:
            idx = int(df["Idx"])
            if idx > 0:
                if self.close.iloc[idx-1] > self.open.iloc[idx-1] \
                and df["Open"] >= self.close.iloc[idx-1] \
                and df["Close"] <= self.open.iloc[idx-1]:
                    return True
                else:
                    return False
                
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