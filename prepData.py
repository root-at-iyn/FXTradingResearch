import pandas as pd
from data.features import Candle, Intraday

if __name__ == '__main__':
    #get data
    data = pd.read_csv("./output/GBPUSD_15mins_1yr_End_20260311.csv")
    
    #clean data
    data.drop(columns=["Volume", "WAP", "BarCount"], inplace=True)
    
    #set date to datetimeindex
    data["Date"] = pd.DatetimeIndex(data["Date"],tz="Europe/London")
    data.set_index("Date", inplace=True)
    data = data.tz_convert("US/Eastern")
    
    #add candle properties
    candle = Candle()
    data["CBody"] = data.apply(candle.body, axis=1)
    data["CRange"] = data.apply(candle.range, axis=1)
    data["CUWick"] = data.apply(candle.upper_wick, axis=1)
    data["CLWick"] = data.apply(candle.lower_wick, axis=1)
    
    #add intraday index
    intraday = Intraday()
    data["Iday_Idx"] = data.apply(intraday.index, axis=1)
    
    # show data
    print(data.loc['2026-03-08 17:15':'2026-03-09 17:45'])

# Expect
"""
                               Open      High       Low     Close     CBody    CRange    CUWick    CLWick  Iday_Idx
Date                                                                                                               
2026-03-08 17:15:00-04:00  1.335075  1.335110  1.334565  1.334795  0.000280  0.000545  0.000035  0.000230         0
2026-03-08 17:30:00-04:00  1.334795  1.335095  1.334285  1.334635  0.000160  0.000810  0.000300  0.000350         1
2026-03-08 17:45:00-04:00  1.334635  1.335175  1.333840  1.334035  0.000600  0.001335  0.000540  0.000195         2
2026-03-08 18:00:00-04:00  1.334035  1.334700  1.331915  1.331920  0.002115  0.002785  0.000665  0.000005         3
2026-03-08 18:15:00-04:00  1.331920  1.333780  1.331745  1.333085  0.001165  0.002035  0.000695  0.000175         4
...                             ...       ...       ...       ...       ...       ...       ...       ...       ...
2026-03-09 16:30:00-04:00  1.343580  1.343885  1.342410  1.343875  0.000295  0.001475  0.000010  0.001170        93
2026-03-09 16:45:00-04:00  1.343875  1.344715  1.343390  1.343390  0.000485  0.001325  0.000840  0.000000        94
2026-03-09 17:15:00-04:00  1.344065  1.344155  1.343390  1.344085  0.000020  0.000765  0.000070  0.000675         0
2026-03-09 17:30:00-04:00  1.344085  1.344305  1.343920  1.343920  0.000165  0.000385  0.000220  0.000000         1
2026-03-09 17:45:00-04:00  1.343920  1.344455  1.343855  1.344270  0.000350  0.000600  0.000185  0.000065         2

[98 rows x 9 columns]
"""