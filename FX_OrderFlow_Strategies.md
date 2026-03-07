# FX Order Flow Strategies
*The following text is the output from Gemini AI which summarises typical order flow strategies*

FX order flow trading focuses on the real-time interaction between buyers and sellers by analyzing the stream of executed and pending orders to identify supply and demand imbalances. Unlike traditional technical analysis, which uses historical price data, order flow reveals immediate market aggression and institutional activity. [1, 2, 3] 
Core Strategies

* Absorption:
* Occurs when a large number of market orders (aggressive) hit a price level but fail to move it because a major player is "absorbing" the flow with limit orders (passive).
   * Signal: A high-volume price level that stalls often precedes a sharp reversal as the aggressive side becomes "trapped".
* Exhaustion:
* Market momentum fades as fewer aggressive orders enter the market to support the current trend.
   * Signal: Decreasing volume and delta (the difference between buy and sell volume) at price extremes, indicating the move is running out of steam.
* Iceberg Order Detection:
* Institutions use "iceberg" orders to hide large positions by only showing a small portion of the total size in the order book.
   * Signal: Price repeatedly hits a level and fills more volume than is visible on the Depth of Market (DOM), suggesting hidden institutional accumulation or distribution.
* Delta Divergence:
* Analyzes the relationship between price movement and net buying/selling pressure.
   * Signal: A "bearish divergence" occurs when price makes a new high but the Cumulative Volume Delta (CVD) is lower, suggesting the rally lacks real conviction.
* Liquidity Sweeps (Stop Hunts):
* Large players often push price into "liquidity pools" (areas where retail stop-losses are clustered) to fill their own large orders.
   * Signal: A rapid spike through a known support/resistance level that immediately reverses, confirmed by a massive surge in volume. [1, 2, 3, 4, 5, 6, 7, 8, 9] 

Key Components & Tools

* Depth of Market (DOM): A live display of the "order book," showing pending limit orders at different price levels.
* Footprint Charts: Visualise executed volume at each price within a candle, often color-coded to show buying vs. selling aggression.
* Volume Profile: A horizontal histogram showing where the most trading activity (Value Area) and high-volume nodes (HVN) occurred.
* Time and Sales (The Tape): A real-time log of every executed trade, including its size and whether it hit the "bid" or "ask". [2, 5, 7, 8, 10, 11] 

Forex Specific Considerations

* Decentralised Market: Unlike futures, spot FX has no central exchange. Retail traders often use "tick volume" or aggregated data from specific liquidity providers as a proxy for true order flow.
* Currency Futures: Many professional traders analyze order flow on currency futures (e.g., 6E for EUR/USD) because they provide transparent, exchange-based volume data. [5, 8, 12, 13, 14] 

Would you like to explore how to set up footprint charts or delta indicators on a specific platform like TradingView or NinjaTrader?

[1] [https://www.cmcmarkets.com](https://www.cmcmarkets.com/en/trading-strategy/order-flow-trading)
[2] [https://www.cmcmarkets.com](https://www.cmcmarkets.com/en-gb/trading-strategy/order-flow-trading)
[3] [https://www.xs.com](https://www.xs.com/en/blog/order-flow-trading/)
[4] [https://www.xs.com](https://www.xs.com/en/blog/order-flow-trading/)
[5] [https://citytradersimperium.com](https://citytradersimperium.com/order-flow-trading-analysis/)
[6] [https://mondfx.com](https://mondfx.com/what-is-order-flow)
[7] [https://theforexscalpers.com](https://theforexscalpers.com/how-does-order-flow-trading-work/)
[8] [https://www.ultimamarkets.com](https://www.ultimamarkets.com/academy/order-flow-trading-explained-improve-forex-trading-edge/)
[9] [https://tradefundrr.com](https://tradefundrr.com/order-flow-analysis/)
[10] [https://en.wikipedia.org](https://en.wikipedia.org/wiki/Order_flow_trading)
[11] [https://www.exclusivemarkets.com](https://www.exclusivemarkets.com/blog/order-flow-trading)
[12] [https://www.econstor.eu](https://www.econstor.eu/bitstream/10419/278743/1/1860573126.pdf#:~:text=257%29.%20Due%20to%20the%20nature%20of%20the,currencies%20on%20the%20spot%20and%20forward%20market.)
[13] [https://www.learnsignal.com](https://www.learnsignal.com/blog/understanding-futures-fx-markets/#:~:text=Centralisation:%20Futures%20markets%20are%20centralised%20and%20operate,and%20work%20as%20an%20over%2Dthe%2Dcounter%20%28OTC%29%20market.)
[14] [https://www.futurelearn.com](https://www.futurelearn.com/info/courses/defi-exploring-decentralised-finance-with-blockchain-technologies/0/steps/251888#:~:text=Decentralised%20Finance:%20Blockchain%2C%20Ethereum%2C%20and%20The%20Future,a%20debt%20contract%20or%20a%20futures%20contract.)
