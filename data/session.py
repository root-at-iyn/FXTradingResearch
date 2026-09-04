from pandas import DataFrame, Timedelta
class SessionTimes():
    """Class to handle FX Session times"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def vectorised_apply(df: DataFrame):
        """Returns Global FX Session start and end times"""
        # Intraday Index
        hour_start_of_day: int = 17
        tf_minutes: int = 15
        df["Iday_Idx"] = \
            (((df.index.hour + (24 - hour_start_of_day)) * (60 / tf_minutes)) \
             + (df.index.minute /tf_minutes )) % ((60 / tf_minutes) * 24)
        df["FX_Open"] = df.iloc[df["Idx"]-df["Iday_Idx"]+1].index # 17:15 EST
        df["FX_Close"] = df["FX_Open"] + Timedelta(hours=23,minutes=45) # 17:00 EST
        df["TYO_Open"] = df["FX_Open"] + Timedelta(hours=1,minutes=45) # 19:00 EST
        df["TYO_Close"] = df["FX_Open"] + Timedelta(hours=10, minutes=45) # 04:00 EST
        df["LDN_Open"] = df["FX_Open"] + Timedelta(hours=8, minutes=45) # 02:00 EST
        df["LDN_Close"] = df["FX_Open"] + Timedelta(hours=17, minutes=45) # 11:00 EST
        df["NY_Open"] = df["FX_Open"] + Timedelta(hours=13, minutes=45) # 07:00 EST
        df["NY_Close"] = df["FX_Open"] + Timedelta(hours=23,minutes=45) # 17:00 EST

        return df