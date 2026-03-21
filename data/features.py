from pandas import DataFrame, Series

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

class Clean():
    def __init__(self) -> None:
        pass

    @staticmethod
    def datetime(df: DataFrame) -> Series:
        """Split the ISO format date string into separate date and time columns
        """
        df["Time"] = df.apply(lambda x: x["Date"].rsplit("T")[1], axis=1)
        df["Date"] = df.apply(lambda x: x["Date"].rsplit("T")[0], axis=1)
        time = df.pop("Time")
        df.insert(1,"Time", time)
        return 
