# Feature Engineering

## Overview
The FX data from a broker includes basic price data such as the open, high, low, close, volume (OHLCV), weighted average price (WAP), and the number of trades transacted (BarCount). By itself, this presents a limited view of price action without considering other factors market participants evaluate when making a buy or sell decision. Without further information it will be difficult to see price patterns and infer whether looking back at the last *n* time intervals tells us anything meaningful about price behaviour or future directional movement. To properly explore price behaviour we need to transform the raw price data into a dataset that includes other data points relevant to our model. This will help to improve it's predictive accuracy. The process of transforming the data is called Feature Engineering. 

A feature is a another data point (i.e. *variable*) that relates to the dependable variable *(e.g. price)* under exploration. A feature enhances the dataset by adding contributing factors that can improve the understanding and accuracy of the model. The types of trading related factors in the context of FX analysis may include but are not limited to:

- **Events -** 
An event can be defined as an occurrence that happens at a point in time, like a candlestick pattern, price breakout, news release, or geo-political event. It can be represented as a binary since the event either occured or did not occur. For some events e.g. news, you may want to grade whether the new was positive or negative, or an ordinal scale of positive/negativeness.

- **Context -**
Contextual data helps to explain why results may differ at times, and capture factors that influence the result. This can include things like major highs/lows, sentiment, risk off, interest rate expectations, trendiness, time-of-day e.g. FX Sessions (London, NY, Asia) ... etc.

## Feature Types
*Ref: https://domino.ai/data-science-dictionary/feature-engineering#ff2abbea257a*

### Numerical
Features with numerical values (i.e. integers/floats), e.g. SMA, RSI, Bollinger Bands.

### Categorical
Features that take one of a limited number of values, e.g. FX Sessions (London, New-York, Asia).

### Ordinal
Categorical features that have an order, e.g. day of the week, (Sun=0, Mon=1, Tue=2, Wed=3 ... etc.)

### Binary
Features that have data that results in True or False values, e.g. candlestick pattern, close above previous high, NFP week ... etc.

### Textual
Features that contain textual data. Textual data typically requires special preprocessing steps (like tokenization) to transform it into a format suitable for machine learning models. Example textual data from an FX trading perspective could be a Trump post, Federal Reserve or other Central Bank speak, or the details of an NFP release. This would rely on an AI model to analyse the text and return a result of whether the text is considered "bearish" or "bullish".


# Selected Features
The following features have been selected beacuse they are widely accepted by traders as factors that can influence decisions to enter or exit positions.

<!-- Template >
### Name
| Data Type | |
|-----------|------|
| Definition| |
| Use Case  | |
< Template End -->

## Continuous Features
These are data points that are continuous in their distribution, meaning there's a data point for each bar on chart timeframe under analysis.

### Body
| Data Type | float|
-----------|------|
| Definition| The range between the open and close price, calculated by: $abs(close - open)$|
| Use Case  | Used to determine the strength of price movement within a single bar. If a candle's body is larger than it's *wicks* (i.e. price extremes), it indicates the price moved in a given direction and maintained that direction for the duration of the bar's interval. This can be used in calculating candlstick patterns like the `shooting star`, where the *body* should be smaller than the price extreme (i.e. $high - open$ when the close is lower than the open price.)|

### Range
| Data Type | float|
|-----------|------|
| Definition| The difference between the highest and lowest price of the interval, calculated as $high - low$.|
| Use Case  | Can reveal an increase in price volatility when the range is larger than its average or larger than the previous *n* intervals. Can also be used in calculations to define some candlestick patterns.|

### Upper Wick
| Data Type | float|
|-----------|------|
| Definition| The price range between the highest price and the top of the *body*. The top of the body is close price when the bar is positive, and the open price when the bar is negative.|
| Use Case  | Used in calculations to define some candlestick patterns.|

### Lower Wick
| Data Type | float|
|-----------|------|
| Definition| The price range between the lowest price and the bottom of the *body*. The bottom of the body is open price when the bar is positive, and the close price when the bar is negative.|
| Use Case  | Used in calculations to define some candlestick patterns.|

### Intraday High
| Data Type | float|
------------|------|
| Definition| The highest price in the intraday session.|
| Use Case  | Used to calculate the intraday range, but can also be used in reversal strategies.|

### Intraday Low
| Data Type | float|
------------|------|
| Definition| The lowest price in the intraday session.|
| Use Case  | Used to calculate the intraday range, but can also be used in reversal strategies.|

### Intraday Range (IR)
| Data Type | float|
------------|------|
| Definition| The distance between the highest and lowest price of the day, calculated as (DHigh - DLow).|
| Use Case  | Can be used to help define other features like the average daily range, or show whether today's range was greater than the previous day's range. Theoretically, an increase in the day's range and a daily close at the high of the range could indicate rising price momentum.|

### Average Daily Range (ADR)
| Data Type | float|
------------|------|
| Definition| The average daily price range over the last *n* daily periods, calculated by $\frac{\sum_{i=1}^{n} x_{i}}{n}$|
| Use Case  | Helps to determine if the intraday price movement has moved further or less than average daily range. It can be used in combination with other calculations to determine the probability of the current intraday price moving *x* more pips by the end of the day. |

### Simple Moving Average (SMA)
| Data Type | float|
------------|------|
| Definition| The mean average price over *n* periods ($\frac{\sum_{i=1}^{n} Price_{i}}{n}$), where price can be the closing price, high, low, or open. By default this is usually set to the closing price. |
| Use Case  | SMA is used to help detect if the price is trending. It is also used in Moving Average Cross strategies where two SMA's are used, a longer period and a shorter period. When the shorter period crosses the longer period, it could indicate a change in the trend. |

### Relative Strength Index (RSI)
| Data Type | float|
------------|------|
| Definition| RSI is an overbought/oversold indicator used to measure price momentum on a scale between 0-100 over *n* periods. It is calculated in two steps: 1. Calculate the relative strength (RS) over *n* periods = $\frac{Avg Gain}{Avg Loss}$, 2. Calculate (RSI) = $$\left[ 100 - \left[ \frac{100}{1 + RS} \right] \right]$$ Values over the upper limit (typically 70) is considered overbought, and values under the lower limit (typically 30) is considered oversold. |
| Use Case  | RSI is often used to indicate divergences between RSI and the extreme price high/low. For example, is the price is at the lowest point of the day, but RSI is higher than the previous low of point of the day, then this would indicate a bullish divergence in price.|

### Bollinger Bands
| Data Type | float|
------------|------|
| Definition| Bollinger bands measure the volatility of price by computing *n* standard deviations above and below the SMA. The calculation works by first computing the SMA over *n* periods:<br><br>$SMA = \left[\frac{\sum_{i=1}^{n} Price_{i}}{n}\right]$<br><br> then computing the standard deviation ($\sigma$) over *n* periods. This is done by summing the result of subtracting the SMA from the each price period *i* and squaring it, then dividing the sum of squares by *n*, and taking the square root of the sum:<br><br> $$\sigma = \left[ \sqrt{\frac{\sum_{i=1}^{n} (Price_i - SMA)^2}{n}} \right]$$<br><br> The Upper Band is calculated by adding the SMA and the $\sigma$ times its multiplier *k*, which is often 2 by default: $SMA(n) + K \times \sigma_n$. For the Lower Band the same equation is used but this time subtracting i.e. $SMA(n) - K \times \sigma_n$. |
| Use Case  | Bollinger Bands can be used in different scenarios, but are mainly used in reversal strategies. For example, when the price opens above the Upper Bollinger Band and Closes at its lows below the Upper Bollinger Band, this could indicate that the price will fall.|

## Reference Features
These are data points that are used as a reference to support or add weight to another feature. For example a shooting star candlestick pattern might have better results when it occurs at yesterday's high (the reference). 

### Day High (DHigh)
| Data Type | float|
------------|------|
| Definition| The highest price of today's session (24hr period).|
| Use Case  | Used in IR calculation and can help to determine if prices are trending up, e.g. newer highs are being made but not newer lows.|

### Day Low (DLow)
| Data Type | float|
------------|------|
| Definition| The lowest price of today's session (24hr period).|
| Use Case  | Used in IR calculation and can help to determine if prices are trending down, e.g. newer lows are being made but not newer highs.|

### Intraday Signficant Levels (ISigLvl)
| Data Type | array|
------------|------|
| Definition| An array of significant high and low price points within the current day's trading session. A high or low is significant when the price was the higest or lowest price in an intraday session over *n* periods.|
| Use Case  | The longer a price holds as the high/low of the session, the more likely traders will be using it as a target to take profit, or to enter a new position. The ISigLvls act as intraday support and resistance (S/R) levels, while supporting the concept of S/R polarity (support and resistance can swap roles depending on the price action.)  |

### Monthly Signficant Levels (MSigLvl)
| Data Type | array|
------------|------|
| Definition| An array of significant daily high and low price points within the trading month. A daily high or low is significant when the price was the higest or lowest price in a calendar month over *n* periods.|
| Use Case  | The longer a price holds as the high/low of the month, the more likely traders will be using it as a target to take profit, or to enter a new position. |

### Intraday Range Percentage (IRP)
### Name
| Data Type | float|
------------|------|
| Definition| The percentage of how far the price is from the intraday high (Top of today's trading range). Calculated by $\frac{IRHigh - Price}{IR} \times 100$, where *Price* is one of *OHLC*.|
| Use Case  | Shows what percentage of the days range the current price action is in. This is useful because some candlestick patterns are only valid when appearing at the top of the day's range, or at the bottom of the day's range.|

### Close Percent from Bar High (CPfBH)
| Data Type | float|
------------|------|
| Definition| The percentage of the bar's closing price from the bar's highest price. This is calculated by $\frac{High - Close}{BarRange} \times 100$. A low percentage shows the price closed near the high of the bar.|
| Use Case  | Used to calculate some candlestick patterns that depend on the closing price being near the high of the candle.|

### Open Percent from Bar Low (OPfBL)
| Data Type | float|
------------|------|
| Definition| The percentage of the bar's opening price from the bar's lowest price. This is calculated by $\frac{Open - Low}{BarRange} \times 100$. A low percentage shows the price opened near the low of the bar.|
| Use Case  | Used to calculate some candlestick patterns that depend on the opening price being near the low of the candle.|

## Event-based Features
These are data points where an event occurs at some time (*x*) on the *x* axis at the closing price *y* on the *y* axis. Even with a news event, the closing price is an important factor because it reveals the initial reaction after the event has occured. Candlestick patterns are also only confirmed at the closing price of the candle's interval. There are many candlestick patterns but not all are equal, so I will only add what I think are commonly used and well known patterns. These are more likely to get a reaction when they occur.  

### Shooting Star
| Data Type | boolean|
------------|------|
| Definition| A bearish reversal candlestick pattern that has a wider than average price range with the open near the close, and close at or near its low. The pattern creates a distinctive looking *wick* because of the wide price range between the high and the top of the candle's body, which is also larger than the candle's body. The top of the candle's body is the open when the bar is negative, and the close when the bar is positive. Specifically, the upper wick should be at least twice the height of the body. The pattern must occur in after a rally in price.|
| Use Case  | Used in reversal strategies to signal a change in the current trend.|

### Hammer
| Data Type | boolean|
------------|------|
| Definition| A bullish reversal candlestick pattern that has a wider than average price range with the close near the open, and close at or near it's high. The pattern creates a distinctive looking *wick* because of the wide price range between the low and the bottom of the candle's body, which is also larger than the candle's body. Specifically, the lower wick should be at least twice the height of the body. The hammer must occur after a decline in price. If it occurs after a rally, then the pattern is a 'hanging man' indicating price action is turning bearish.|
| Use Case  | Used in reversal strategies to signal a change in the current trend.|

### Bullish Engulfing
| Data Type | boolean|
|-----------|------|
| Definition| A bullish reversal candlestick pattern that occurs after a decline in price, where the current candle's body (which is positive) wraps around (i.e. engulfs) the body of the prior negative candle. The current candle should have its open below or equal to the close of the prior candle, and its close greater than or equal to the previous candle. The current candle should have a larger than average range, indicating an acceleration in the price rising. |
| Use Case  | Used in reversal strategies to signal the end of a price decline. The pattern also acts as support.|

### Bearish Engulfing
| Data Type | boolean|
|-----------|------|
| Definition| A bearish reversal candlestick pattern that occurs after a rally in price, where the current candle's body (which is negative) wraps around (i.e. engulfs) the body of the prior positive candle. The current candle should have its open above or equal to the close of the prior candle, and its close below than or equal to the previous candle. The current candle should have a larger than average range, indicating an acceleration in the price falling. |
| Use Case  | Used in reversal strategies to signal the end of a price rally. The pattern also acts as resistance.|