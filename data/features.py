from pandas import DataFrame, Series, to_datetime
from datetime import datetime, time

class Candle():
    """
    Class to return the properties of a time period derived from the OHLC

    Takes a Pandas DataFrame of `OHLC` data, and returns the calculated 
    properties of the period (represented as candlestick on the chart). 
    This is designed to work with the pandas.apply() method and should set 
    `axis=1` to receive a series and apply to the column.
    """

    def __init__(self) -> None:
        pass 

    def body(self, df: DataFrame) -> Series:
        """Returns the body of the candlestick"""

        return abs(df["Open"] - df["Close"])
    
    def range(self, df:DataFrame) -> Series:
        """Returns the range of the candlestick"""

        return (df["High"] - df["Low"])
    
    def upper_wick(self, df: DataFrame) -> Series:
        """Returns the upper wick of the candlestick"""

        if df["Close"] >= df["Open"]:
            wick = df["High"] - df["Close"]
        else:
            wick = df["High"] - df["Open"]
        
        return wick
    
    def lower_wick(self, df: DataFrame) -> Series:
        """Returns the lower wick of the candlestick"""

        if df["Close"] <= df["Open"]:
            wick = df["Close"] - df["Low"]
        else:
            wick = df["Open"] - df["Low"]
        
        return wick

class Intraday():
    def __init__(self) -> None:
        self.index_count = 0

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

    def high(df: DataFrame):
        """Returns the high of the intraday session"""
        
        pass    
    