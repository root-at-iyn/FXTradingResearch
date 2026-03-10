# FX Price Pattern Research

## Introduction
This project is my personal workspace for researching FX price behaviour and statistical patterns that can be used in trading strategies. This is not financial advice, so read, review, or use with caution. I decided to make this short project to help with calculating the odds of price movement when patterns occurr, which will be helpful in determining risk and position sizing in some of my strategies. The intro page is just a summary of FX Trading from a retail perspective, and my thought process on price research and building strategies.

### Price Charts - Candlesticks
A Candlestick chart plots the price (Y) over a time series (X) with each bar representing an interval of time, e.g. seconds, minutes, hours, days ... etc. Each bar contains the Open, High, Low, Close, and Volume (OHLCV) of the price at that interval. For example, a candlestick starting at 10:00 on a 5 minute timeframe would have the OHLCV data between 10:00:00 and 10:04:59. The next bar would start at 10:05:00. This offers a simplified way to visualise more of the price movement within the time interval, capturing the price extremes (high/low) with the open and close quotes. Since Candlesticks condense more info in the time interval than line charts, they are often preferred by traders and widely available on charting packages. 

### Candlestick Price Patterns and Technical Analysis
It is somewhat accepted that Candlestick charts can display repeatable patterns of price behaviour, which may represent the demand of participants in the market and infer the direction of price over a period of time. An example of a commonly used candlestick pattern is the "hammer", which gets its name from the visual shape of the bar when it appears. A hammer candlestick forms when the price goes down substantially from the opening price of the bar, but moves all the way back up past the open of the bar, closing just above the open at its highs. The wide price range between the candle's low and the opening price shows that the price could not move down any further due to high demand at the price low, resulting in prices rapidly increasing. This would indicate the market expects prices to continue rising.

Steve Nixon wrote a book on Japanse Candlesticks Chart Patterns and brought the idea from Asia to US/Europe in the 1990's, however I am unaware of any research that shows the estimated probability of price moving in a particular direction after a pattern occuring. Steve Nixon was careful to mention in his book that the patterns are somewhere between Art and Science, not revealing how far price will move, but giving clues to market demand for higher or lower prices. 

Candlesticks chart patterns can be combined with tradtional Technical Analysis (TA), which is the manual study chart patterns that occur on line or bar charts. For example, traditional TA introduces concepts of, support, resistance, trend lines, reversal patterns, and indicators such as moving averages, RSI ... etc. His argument was that when Candlestick chart patterns occur in combination with TA patterns, the patterns become more powerful and more likely. That said, we can only verify the likelihood of success by running a significant number of trials for Candlestick patterns that occur with TA patterns. Candlestick and TA trials will be a component of this research, and explained in more detail when applicable to the test case. 

### The FX Market
Candlestick and TA patterns visually show the effects of directional price movement, but they are not the cause of the movement, although they may play a small role in it. According to the [Bank of International Settlements (BIS)](https://www.bis.org/statistics/rpfx25_fx.htm), the Foreign Exchange (FX) market traded $9.6 trillion USD per day in 2025, with 46% of the volume attributed to inter-dealer trading, and 50% of the volume traded between FX dealers and other financial institutions. This means 96% of the FX market volume is done by FX dealers and financial institutions. The FX Spot market accounts for 31% of daily volume, with FX Swaps at 42%, and FX Forwards accounting for 19%. In 2025 38% of FX volume was traded from the UK, and 19% in the US. The most traded currency is the USD which accounted for 89% of all traded pairs.

These statistics highlight that the market is dominated by financial institutions, with the dollar being the most traded currency followed by GBP, JPY, and CHF. Around 50% of the daily FX trading volume is done between the US and UK, so the London / New York FX overlap is a highly liquid and important time to trade. Since the USD is the most traded currency, econonmic data releases from the US have weight, and will be watched by more traders. In addition, 42% of traded contracts involve FX Swaps, so participants are also hedging currency risk, interest rate differentials, and attempting to get cheaper loans. Any changes around interest rates, bond yields, inflation, or sizeable moves in either currency in the pair, will have an effect on the Swaps and therefore the price.   

### Price Discovery
The FX market structure and macroeconomics needs to be considered when looking for fundamental drivers that can move price. They play a part in the decision making process of why a financial institution may be proactively trading a currency ahead of a data release, or trading reactively to the release. This gives you the human reasoning, but technically price moves in a given direction because of order flows in the market.

All financial markets take the form of an auction, where participants send in a Bid to buy an asset at their desired price, or send in their Asking price for an asset they want to sell. The main party of the transaction is the dealer, who acts as a market maker for the participants. In FX, for the dealer to make a profit they charge a transaction fee, to manage the order and add it to their orderbook. 

The orderbook contains all of the orders in the market, which is made up of Bids and Offers at multiple price levels. In the orderbook the Bid price is always lower than the Ask price. If the Bid is at the Ask price or higher, a trade will occur. The orderbook matches the nearest Bid to the nearest Ask/Offer price (i.e. NBNO). The price is quoted to the market by showing the highest Bid, and lowest Offer. The difference between the Bid and the Offer is called the spread. When the spread is small, it indicates the market is active and has high liquidity. This means there's a lot participants sending in Bids and Offers and the orderbook doesn't have to stretch wide to find Bid/Offer prices.

When participants want to trade at market prices, they simply accept the nearest bid to sell the asset, or accept the offer price to buy the asset. When this transaction happens orders are removed from the book, and if there are no more orders left at that price level, the orderbook moves to the next price in the book. 

For example, say I want to buy at market £150,000 worth of USD at 1.3350, but there is only £100,000 worth left at that price, the orderbook will take my order and buy £100,000 at 1.3350, then buy the remaining £50,000 at the next Ask price, e.g. 1.3355. For the next participant wanting to buy at market prices, the new GBP/USD price would be 1.3355. If I sent a limit order to the market, then the order would only be filled at the 1.3350 level for the specified quantity, but if no seller wants to drop their Ask price to that level for the amount that I need, my order would not get filled. This is how orders flow through the market, and is the actual mechanism that moves prices.

### Order Flow Analysis

Some trading strategies utilise order flow analysis to inspect prices where there's an accumulation of orders, and trade based on price reaction at those levels. See [FX Order Flow Strategies](./FX_OrderFlow_Strategies.md) for more info. This relies on obtaining volume metrics from the price data feed or the Level 2 "Depth of Book" data from the broker/exchange. Since FX is mainly traded Over the Counter (OTC), you can't get an acurate figure of the volume at a particular time-interval, or the market's Depth-of-Book. The Depth-of-Book will be unique to the broker/dealer, but in some cases there are data brokers that aggregate orderbooks across a number of Banks and Financial Institutions. This can be more representative and a good approximation of real order flow in the market. It should be noted however, obtaining aggregated orderbook data is expensive (See [DX Feeds](https://dxfeed.com/market-data/fx/)), so it could be a barrier for a continuous order-flow strategy.


Futures prices can be used to get a sample of real volume (i.e. number of contracts traded) in the FX market at a time-interval. This is more accurate than some broker feeds which only show "tick" volume (i.e. number of price changes within the period). Without the orderbook, if you have real volume data, you can see the number of contracts traded over a time interval when the currency reached a specific price, and infer that institutions had a high interest at that time or level.  

### Strategy Types

There are three types of trading strategies widely used in the professional and retail trading community; Momentum, Mean Reversion, and Trend Following. These strategy types also base their logic on price pattern behaviour in different scenarios.

#### Momentum
A momentum-based strategy takes advantage of short term volatility as prices surge in a given direction. Technical indicators like RSI can help to identify abnormal price movement and momentum-based opportunities. For example, if the price of GBP/USD jumps 50% of its daily range within 5 minutes, this could indicate strong buying momentum for GBP. Traders will buy at the higher price, expecting the price to rise even higher. This is typically used in breakout strategies.

#### Mean Reversion
A mean reversion stratgey is based on the idea that after an extended or extreme move in price, the asset will move back to its mean average price. This can be used in trend following or reversal strategies, and is freequently used by algorithmic traders.

#### Trend Following
Trend following strategies as the name indicates tracks the trend of prices in a given direction. Traders will take positions in the direction of that trend until it changes direction. Indicators such as a Moving Averages and MACD work well with trend following stratgeies. An example of a trend following strategy is the Moving Average, where prices above the moving average indicate the price is trending higher, resulting in a buy signal. If the price falls below the moving average, it would indicate the price is trending lower resulting in a sell signal. A widely accepted moving average period on daily chart timeframe is the 200 period Simple Moving Average (SMA), which is watched by many financial analysts and advisors.

There are dozens of different technical trading strategies not mentioned here, but they all tend to be based on one of the three strategy types.

## Investigating Price Patterns
I have not described all Candlestick and TA patterns on this page because it would take up too much time, and there's a vast amount of free online resources (e.g. [Investopedia](https://www.investopedia.com/articles/active-trading/092315/5-most-powerful-candlestick-patterns.asp)) that can explain this effectively. What I intend to focus on is investigating the reliability of price patterns in general. 

TA can be very subjective at times, since many TA principles come down to what you can visually see on the chart, and of course people may interpret this differently. It also widely accepted that Candlestick and TA patterns do not always yield a successful result, nor can a pattern predict the extent of a move. Its possible for a pattern to occur, briefly go in the intended direction, then reverse and move in the opposite direction. This forces the trader to think about how far they are willing to let the price move against their position, and at what point do they accept a price pattern has failed. A trader also needs to think about where to take profit when a pattern moves price in the expected direction.

Most people jump straight into backtesting a strategy using technical indicators, then attempt to optimise the indicators for the best results. Over optimisation can lead to curve fitting, even with walk-forward testing, so optimisation needs to be constrained. However, backtesting a strategy based on an indicator or TA pattern in isolation, ignores the other marjor market dynamics, such as time-of-day, wider technical trends on higher level timeframes, macroeconomic factors, liquidity, and volume. It also ignores whether a strategy improves if combined with other price pattern behaviour.

My approach to this problem is to look fundamently at the price behaviour of a currency pair. This may involve questions like:
- What is the average range of prices in a time-interval?
- How often does price go beyond this range?
- What is the probability of price extending beyond the range, in isolation or with another event occuring?
- What is the probability a currency pair moves in a direction after a pattern occurs?
- What is the probability of a reversal pattern being successful when paired with other TA reversal signs?

This approach tries to ask questions of the price and related market data, to find out the probabilities of different scenarios occurring. The output can be used to start forming a statistically driven strategy that can be backtested. The approach is not perfect, because changes in price behaviour or regime change could affect the odds of the expected outcome. However, if the statistical metrics are frequently checked, the probablilites can be updated on a daily basis.

The following sections will link to dedicated pages that discuss different research ideas, and the output from that study.

## Research Topics
tbd.
