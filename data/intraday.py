from pandas import Series, DataFrame

class Intraday():
    def __init__(self, df: DataFrame) -> None:
        self.index_count = 0
        self.dhigh = 0
        self.dhigh_idx = 0
        self.dlow = 0
        self.dlow_idx = 0
        self.dhighest_close = 0
        self.dhighest_close_idx = 0
        self.dlowest_close = 0
        self.dlowest_close_idx = 0
        self.df = df

    def high(self, df: Series):
        """Returns the high of the intraday session"""
        
        if df["Iday_Idx"] == 1:
            self.dhigh = df["High"]
            self.dhigh_idx = int(df["Idx"])
        elif df["High"] > self.dhigh:
            self.dhigh = df["High"]
            self.dhigh_idx = int(df["Idx"])
    
        return self.dhigh, self.dhigh_idx

    def highest_close(self, df: Series):
        """Returns the highest close of the intraday session"""
        
        if df["Iday_Idx"] == 1:
            self.dhighest_close = df["Close"]
            self.dhighest_close_idx = int(df["Idx"])
        elif df["Close"] > self.dhighest_close:
            self.dhighest_close = df["Close"]
            self.dhighest_close_idx = int(df["Idx"])
    
        return self.dhighest_close, self.dhighest_close_idx
        
    def low(self, df: Series):
        """Returns the low of the intraday session"""
        
        if df["Iday_Idx"] == 1:
            self.dlow = df["Low"]
            self.dlow_idx = int(df["Idx"])
        elif df["Low"] < self.dlow:
            self.dlow = df["Low"]
            self.dlow_idx = int(df["Idx"])
    
        return self.dlow, self.dlow_idx
    
    def lowest_close(self, df: Series):
        """Returns the highest close of the intraday session"""
        
        if df["Iday_Idx"] == 1:
            self.dlowest_close = df["Close"]
            self.dlowest_close_idx = int(df["Idx"])
        elif df["Close"] < self.dlowest_close:
            self.dlowest_close = df["Close"]
            self.dlowest_close_idx = int(df["Idx"])
    
        return self.dlowest_close, self.dlowest_close_idx

    def non_vectorised_apply(self):
        """Apply Intraday features as columns to pandas dataframe"""
        # Non-Vectorised
        self.df[["Iday_High", "Iday_H_Idx"]] = self.df.apply(self.high, axis=1, result_type='expand')
        self.df[["Iday_Low", "Iday_L_Idx"]] = self.df.apply(self.low, axis=1, result_type='expand')
        self.df[["Iday_HClose", "Iday_HC_Idx"]] = self.df.apply(self.highest_close, axis=1, result_type='expand')
        self.df[["Iday_LClose", "Iday_LC_Idx"]] = self.df.apply(self.lowest_close, axis=1, result_type='expand')
        # Vectorised
        self.df["Iday_Range"] = self.df["Iday_High"] - self.df["Iday_Low"]
        self.df["Close_Pct_DHigh"] = (self.df["Iday_High"] - self.df["Close"]) / self.df["Iday_Range"]
        self.df["Open_Pct_DHigh"] = (self.df["Iday_High"] - self.df["Open"]) / self.df["Iday_Range"]
        
        return self.df

