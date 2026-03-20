import pandas as pd
from data.features import Candle


if __name__ == '__main__':
    data = pd.read_csv("./output/GBPUSD_15mins_1yr_End_20260311.csv")
    candle = Candle()
    data["Body"] = data.apply(candle.body, axis=1)
    data["Range"] = data.apply(candle.range, axis=1)
    data["UWick"] = data.apply(candle.upper_wick, axis=1)
    data["LWick"] = data.apply(candle.lower_wick, axis=1)
    print(data)