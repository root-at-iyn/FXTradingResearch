import pandas as pd
from data.candle import Candle
from data.intraday import Intraday
from data.session import SessionTimes

PATH = "./output"
OUT_PATH = "./research/price_data"
SYMBOL = "GBPUSD"
FILE = f"{SYMBOL}_15mins_1yr_End_20260311.csv"
df = pd.read_csv(f"{PATH}/{FILE}")
#clean IBKR data
df.drop(columns=["Volume", "WAP", "BarCount"], inplace=True)
data = df
# set date to datetimeindex
data["Date"] = pd.DatetimeIndex(data["Date"],tz="Europe/London")
data.set_index("Date", inplace=True)
data = data.tz_convert("US/Eastern")

# set row index
pd.options.display.max_rows = 100
data["Idx"] = df.index.argsort()
data =  Candle().vectorised_apply(data)
data = SessionTimes().vectorised_apply(data)
iday = Intraday(data)
data = iday.non_vectorised_apply()
print(data.iloc[0])