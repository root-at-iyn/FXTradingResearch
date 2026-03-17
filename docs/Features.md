# Feature Engineering

## Overview
The FX data from a broker includes basic price data such as the open, high, low, close, volume (OHLCV), volume weighted average price (VWAP), and the number of trades transacted (BarCount). By itself, this presents a limited view of price action without considering other factors market participants evaluate when making a buy or sell decision. Without further information it will be difficult to see price patterns and infer whether looking back at the last *n* time intervals tells us anything meaningful about price behaviour or future directional movement. To properly explore price behaviour we need to transform the raw price data into a dataset that includes other data points relevant to our model. This will help to improve it's predictive accuracy. The process of transforming the data is called Feature Engineering. 

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


## Selected Features
The following features have been selected beacuse they are widely accepted by traders as factors that can influence price, or metrics used by analysts when forcasting price direction.

<!-- Template -->
### Name
| Data Type | |
------------|------|
| Definition| |
| Use Case  | |
<!-- Template End -->

### Intraday Range (IR)
| Data Type | float|
------------|------|
| Definition| The distance between the highest and lowest price of the day, calculated as (High - Low).|
| Use Case  | Can be used to help define other features like the average daily range, or show whether today's range was greater than the previous day's range. Theoretically, an increase in the day's range and a daily close at the high of the range could indicate rising price momentum.|

### Average Daily Range (ADR)
| Data Type | float|
------------|------|
| Definition| The average of daily ranges over the last *n* periods, calculated by $\frac{\sum_{i=x1}^{n} i+(i_{-1})}{n}$|
| Use Case  | |

### Name
| Data Type | |
------------|------|
| Definition| |
| Use Case  | |

### Name
| Data Type | |
------------|------|
| Definition| |
| Use Case  | |

### Name
| Data Type | |
------------|------|
| Definition| |
| Use Case  | |

### Name
| Data Type | |
------------|------|
| Definition| |
| Use Case  | |
