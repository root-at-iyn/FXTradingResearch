from pandas import Series, DataFrame

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
        
    @staticmethod
    def vectorised_apply(df):
        """Apply Candle related features as columns 
        using pandas vectorized operations"""
        df["CHG"] = df["Close"] - df["Open"]
        df["Body"] = abs(df["Open"] - df["Close"])
        df["Range"] = df["High"] - df["Low"]
        # Candle Upper Wick
        df["UWick"] = 0.0
        df.loc[df["Close"] > df["Open"],"UWick"] = df["High"] - df["Close"]
        df.loc[df["Close"] < df["Open"],"UWick"] = df["High"] - df["Open"]
        # Candle Lower Wick
        df["LWick"] = 0.0
        df.loc[df["Close"] > df["Open"],"LWick"] = df["Open"] - df["Low"]
        df.loc[df["Close"] < df["Open"],"LWick"] = df["Close"] - df["Low"]
        # Close Pct High
        df["Close_Pct_High"] = 0.0
        df.loc[df["Range"] > 0, "Close_Pct_High"] = (df["High"] - df["Close"]) / df["Range"]
        df["Open_Pct_High"] = 0.0
        df.loc[df["Range"] > 0, "Open_Pct_High"] = (df["High"] - df["Open"]) / df["Range"]

        return df