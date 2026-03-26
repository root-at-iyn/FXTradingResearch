from pandas import Series, to_datetime
from datetime import time
from math import sqrt

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
        if len(self.closes) > n:
            square_dev = [(x - df[sma_col_name])**2 for x in self.closes[-n:]]
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

        return df[sma_col_name] + self.sma_standard_deviation(
            df, sma_col_name, n) * k
    
    def bollinger_band_lower(
            self, df: Series, k: int, sma_col_name: str, n: int = 16
            ):
        """
        Return the Bollinger Lower-Band value to `k` standard 
        deviations for the last `n` SMA periods
        """

        return df[sma_col_name] - self.sma_standard_deviation(
            df, sma_col_name, n) * k