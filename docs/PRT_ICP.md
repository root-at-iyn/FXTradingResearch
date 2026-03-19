# ProRealTime - Intraday Candlestick Patterns

This is my custom script created with the ProRealTime
charting package, and added here as a reference for 
candlestick patterns. The language is called ProBuilder, 
which is similar to Pinescript on TradingView.
You can view the language reference at: https://www.prorealcode.com/documentation/probuilder-welcome/

```java
IRPClose, IRPOpen, IRPHigh, IRPLow = CALL "Intraday Range Percentage"
SMADowntrend, SMAUptrend, SMAConsolidation, SMABearishRetracement, SMABullishRetracement, SMASupportBreak, SMAResistanceBreak = CALL "SMA Directional Bias"
ICPADR = CALL "ADR"
ICPIDR = CALL "IDR"


// =================== Bar Variables ===================================

//This Bar
if Close < Open then
CurrentBar = -1 // Neagtive
elsif Close = Open then
CurrentBar = 0 // Neutral
else
CurrentBar = 1 // Positive
endif

Body = ABS(Close - Open)

if CurrentBar = 1 then
UpperWick = High - Close
else
UpperWick = High - Open
endif

if CurrentBar = 1 then
LowerWick = Open - Low
else
LowerWick = Close - Low
endif

ATR =  AverageTrueRange[12](close)

BarCloseNearHighs = (Close >= (High - Range * 0.34)) // Closed within 34% of the high of candle's range
BarCloseNearLows = (Close <= (High - Range * 0.66)) // Closed within 66% of the low of candle's range
BarOpenNearHighs = (Open >= (High - Range * 0.34)) // Opened within 34% of the high of candle's range
BarOpenNearLows = (Open <= (High - Range * 0.66)) // Opened within 66% of the low of candle's range


// Day's Range

LowerEndOfDaysRange = (IRPOpen >= 0.66) // lower third of todays range
UpperEndOfDaysRange = (IRPOpen <= 0.34) // upper third of todays range

// Bollinger Band
UpperBollinger = BollingerUp[16](close)
LowerBollinger = BollingerDown[16](close)

// SMA
SMA = Average[16](close)

// =================== Candlestick Patterns ===================================



// ====================== Bullish Candles ========================= //

//
// Hammer
If CurrentBar = 1 and LowerWick >= 2 * Body and BarCloseNearHighs  and Range >= ATR then
Hammer = 1
elsif CurrentBar = -1 and LowerWick >= 2 * Body and BarOpenNearHighs  and Range >= ATR then
Hammer = 1
else
Hammer = 0
endif

// Morning Star
// Valid in a downtrend or at bottom of trading range
// Ideal pattern should have the 2nd candle gap away from the 1st and 3rd candle close into the majority of the 1st candle (which is a large body)
// If candle 3 is larger than risk in pips, then entry should be at the open price of candle 3
If CurrentBar[2] = -1 and Body[2] > ATR[2] and BarOpenNearHighs[2] and BarCloseNearLows[2] and Body[2] > Body[1] * 2 and Open[1] =< Close[2] and Body[1] < ATR[1] and CurrentBar = 1 and (Close > High[2] - Range[2] * 0.50) and Body > Body[1] * 2   then
MorningStar = 1
else
MorningStar = 0
endif

// Abandoned Baby Bottom
If CurrentBar[2] = -1 and Body[2] > ATR[2] and BarOpenNearHighs[2] and BarCloseNearLows[2] and CurrentBar[1] = 0 and (Open[1] < Close[2]) and (Close[1] < Close[2]) and Body[1] < ATR[1] and CurrentBar = 1 and (Close > High[2] - Range[2] * 0.50) and Open > Close[1]  then
AbandonedBabyBottom = 1
else
AbandonedBabyBottom = 0
endif

// Bullish Engulfing
// Valid in a downtrend / retracement, or near the lows / support area
// Ideally, place a buy order at the open of the engulfing candle which acts as support
// If it occurs near the highs / top of the days range it could be a bearish sign
if CurrentBar = 1 and BarCloseNearHighs and BarOpenNearLows and CurrentBar[1] < 1 and (Open < Close[1]) and (Close > Open[1]) then
BullishEngulfing = 1
else
BullishEngulfing = 0
endif

// Bullish Piercing
if (CurrentBar = 1 and BarCloseNearHighs and (CurrentBar[1] = -1 ) and Open < Close[1] and Close < Open[1] and (Close >= (Open[1] - (Body[1] * 0.5))))  then
BullishPiercing = 1
else
BullishPiercing = 0
endif

// Bullish Harami
if CurrentBar[1] = -1 and (Body[1] > ATR[1]) and CurrentBar > -1 and Open > Close[1] and Close < Open[1] and Body < ATR and Body[1] > 3* Body  then
BullishHarami = 1
else
BullishHarami = 0
endif

// Bullish Belt-Hold
if CurrentBar = 1 and Body > 1.25 * ATR and BarCloseNearHighs and BarOpenNearLows   then
BullishBeltHold = 1
else
BullishBeltHold = 0
endif

// Three White Soldiers
Soldier = CurrentBar > 0 and BarCloseNearHighs and BarOpenNearLows
if Soldier[2] > 0 and Soldier[1] > 0 and Open[1] <= Close[2] and Body[1] >= Body[2] and Soldier > 0 and Open <= Close[1] and Body >= Body[1]   then
ThreeWhiteSoldiers = 1
else
ThreeWhiteSoldiers = 0
endif

// BullishBreakOut
if BullishBeltHold and (Close - UpperBollinger) / Body > 0.20 and (ICPIDR / ICPADR) < 0.75 then
BullishBreakOut = 1
else
BullishBreakOut = 0
endif


// ===================== Bearish Candles ================================= //

// Hanging Man
If Hammer[1] = 1 and CurrentBar[2] = 1 and Close < Low[1]   then
HangingMan = 1
else
HangingMan = 0
endif

// Shooting Star
If CurrentBar = -1 and UpperWick >= 2 * Body and BarCloseNearLows  and Open >= Close[1]and Range >= ATR  then
ShootingStar = 1
elsif CurrentBar = 1 and UpperWick >= 2 * Body and BarOpenNearLows  and Open >= Close[1] and Range >= ATR  then
ShootingStar = 1
else
ShootingStar = 0
endif


// Evening Star
// Valid in an uptrend or at top of trading range
// Ideal pattern should have the 2nd candle gap away from the 1st and 3rd candle close into the majority of the 1st candle (which is a large body)
// If candle 3 is larger than risk in pips, then entry should be at the open price of candle 3
If CurrentBar[2] = 1 and Body[2] > ATR[2] and BarOpenNearLows[2] and BarCloseNearHighs[2] and Body[2] > Body[1] * 2 and Open[1] >= Close[2] and Body[1] < ATR[1] and CurrentBar = -1 and (Close < (High[2] - Range[2] * 0.50)) and Body > Body[1] * 2  then
EveningStar = 1
else
EveningStar = 0
endif

// Abandoned Baby Top
If CurrentBar[2] = 1 and Body[2] > ATR[2] and BarOpenNearLows[2] and BarCloseNearHighs[2] and CurrentBar[1] = 0 and (Open[1] > Close[2]) and (Close[1] > Close[2]) and Body[1] < ATR[1] and CurrentBar = -1 and (Close < (High[2] - Range[2] * 0.50)) and Open < Close[1]  then
AbandonedBabyTop = 1
else
AbandonedBabyTop = 0
endif


// Bearish Engulfing
// Valid in an uptrend / retracement, or near the highs / resistance area
// Ideally, place a buy order at the open of the engulfing candle which acts as support
if CurrentBar = -1 and BarCloseNearLows and BarOpenNearHighs and CurrentBar[1] > -1 and (Open > Close[1]) and (Close < Open[1]) then
BearishEngulfing = 1
else
BearishEngulfing = 0
endif



// Dark-Cloud Cover
if (CurrentBar = -1 and BarCloseNearLows and (CurrentBar[1] = 1 ) and Open > Close[1] and Close > Open[1] and (Close =< (Close[1] - (Body[1] * 0.33))))  then
DarkCloudCover = 1
else
DarkcloudCover = 0
endif



// Bearish Harami
if CurrentBar[1] = 1 and Body[1] > ATR[1] and CurrentBar < 1 and Open < Close[1] and Close > Open[1] and Body < ATR and Body[1] > 3* Body  then
BearishHarami = 1
else
BearishHarami = 0
endif

// Bearish Belt-Hold
if CurrentBar = -1 and Body > 1.25 * ATR and BarCloseNearLows and BarOpenNearHighs  then
BearishBeltHold = 1
else
BearishBeltHold = 0
endif

// Three Black Crows
Crow = CurrentBar < 0 and BarCloseNearLows and BarOpenNearHighs
if Crow[2] > 0 and Crow[1] > 0 and Open[1] <= Close[2] and Body[1] >= Body[2] and Crow > 0 and Open <> Close[1] and Body >= Body[1]  then
ThreeBlackCrows = 1
else
ThreeBlackCrows = 0
endif

// BearishBreakOut
if BearishBeltHold and (LowerBollinger - Close) / Body > 0.20 and (ICPIDR / ICPADR) < 0.75 then
BearishBreakOut = 1
else
BearishBreakOut = 0
endif

// ================== Conditional Signals ========================= //

if ConditionalSignals then

// Hammer
if Hammer = 1 and (SMADowntrend = 1 or SMABearishRetracement = 1)  and (Low < LowerBollinger) then
Hammer = 1
elsif Hammer = 1 and SMAConsolidation = 1 and ((Low < LowerBollinger) ) then
Hammer = 1
elsif Hammer = 1 and (SMAUptrend = 1 or SMABullishRetracement = 1) and (Low < LowerBollinger ) then
Hammer = 1
else
Hammer = 0
endif

// ShootingStar

if ShootingStar = 1 and (SMAUptrend = 1 or SMABullishRetracement = 1) and (High > UpperBollinger) then
ShootingStar = 1
elsif ShootingStar = 1 and (SMAConsolidation = 1) and ((High > UpperBollinger)) then
ShootingStar = 1
elsif ShootingStar = 1 and (SMADowntrend = 1 or SMABearishRetracement = 1) and (High > UpperBollinger) then
ShootingStar = 1
else
ShootingStar = 0
endif

// BullishPiercing

if BullishPiercing = 1 and (SMADowntrend = 1 or SMABearishRetracement = 1) then
BullishPiercing = 1
elsif BullishPiercing = 1 and SMAUptrend = 1 and (Low < SMA and Close > SMA) then
BullishPiercing = 1
else
BullishPiercing = 0
endif

// DarkCloudCover
if DarkCloudCover = 1 and (SMAUptrend = 1 or SMABullishRetracement = 1) then
DarkCloudCover = 1
elsif DarkCloudCover = 1 and (SMADowntrend = 1 and (High > SMA and Close < SMA)) then
DarkCloudCover = 1
else
DarkCloudCover = 0
endif

// EveningStar
if EveningStar = 1 and SMAUptrend = 1 then
EveningStar = 1
else
EveningStar = 0
endif

// MorningStar
if MorningStar = 1 and SMADowntrend = 1 then
MorningStar = 1
else
MorningStar = 0
endif

// AbandonedBabyTop
if AbandonedBabyTop = 1 and SMAUptrend = 1 then
AbandonedBabyTop = 1
else
AbandonedBabyTop = 0
endif

// AbandonedBabyBottom
if AbandonedBabyBottom = 1 and SMADowntrend = 1 then
AbandonedBabyBottom = 1
else
AbandonedBabyBottom = 0
endif

// BearishHarami
if BearishHarami = 1 and SMAUptrend = 1 then
BearishHarami = 1
else
BearishHarami = 0
endif

// BullishHarami
if BullishHarami = 1 and SMADowntrend = 1 then
BullishHarami = 1
else
BullishHarami = 0
endif

// ThreeBlackCrows
if ThreeBlackCrows = 1 and UpperEndOfDaysRange = 1 then
ThreeBlackCrows = 1
else
ThreeBlackCrows = 0
endif

// ThreeWhiteSoldiers
if ThreeWhiteSoldiers = 1 and LowerEndOfDaysRange = 1 then
ThreeWhiteSoldiers = 1
else
ThreeWhiteSoldiers = 0
endif

// BullishEngulfing
if BullishEngulfing = 1 and (SMADowntrend = 1 or SMABearishRetracement = 1 ) then
BullishEngulfing = 1
elsif BullishEngulfing = 1 and (SMAUptrend = 1 or SMABullishRetracement = 1 ) and (Low < SMA) then
BullishEngulfing = 1
else
BullishEngulfing = 0
endif

// BearishEngulfing
if BearishEngulfing = 1 and (SMAUptrend = 1 or SMABullishRetracement = 1 ) then
BearishEngulfing = 1
elsif BearishEngulfing = 1 and (SMADowntrend = 1 or SMABearishRetracement = 1 ) and (High > SMA) then
BearishEngulfing = 1
else
BearishEngulfing = 0
endif

// BullishBeltHold
if BullishBeltHold = 1 and SMADowntrend = 1 then
BullishBeltHold = 1
else
BullishBeltHold = 0
endif

// BearishBeltHold
if BearishBeltHold = 1 and SMAUptrend = 1 then
BearishBeltHold = 1
else
BearishBeltHold = 0
endif


endif // ===========  End ConditionalSignals ============== //



RETURN Hammer as "Hammer" COLOURED("green"), HangingMan as "HangingMan" COLOURED("red"), BullishEngulfing as "Bullish Engulfing" COLOURED("green"), BearishEngulfing as "Bearish Engulfing" COLOURED("red"), DarkCloudCover as "DarkCloudCover" COLOURED("red"), BullishPiercing as "BullishPiercing" COLOURED("green"), BullishHarami as "BullishHarami" COLOURED("green"), BearishHarami as "BearishHarami" COLOURED("red"), ShootingStar as "ShootingStar" COLOURED("red"), MorningStar as "MorningStar" COLOURED("green"), EveningStar as "EveningStar" COLOURED("red"), AbandonedBabyTop as "AbandonedBabyTop" COLOURED("red"), AbandonedBabyBottom as "AbandonedBabyBottom" COLOURED("green"), BullishBeltHold as "BullishBeltHold" COLOURED("green"), BearishBeltHold as "BearishBeltHold" COLOURED("red"), ThreeBlackCrows as "ThreeBlackCrows" COLOURED("red"), ThreeWhiteSoldiers as "ThreeWhiteSoldiers" COLOURED("green"), BullishBreakOut as "BullishBreakOut" COLOURED("lime"), BearishBreakOut as "BearishBreakOut" COLOURED("crimson")

```