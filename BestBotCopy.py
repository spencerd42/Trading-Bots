from alpaca.data import TimeFrameUnit
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from Range import Range
import secret

# check for trade opportunities every x minutes
TRADE_INTERVAL = 1

# Used to calculate price range over the last x minutes
RANGE_INTERVAL = 60

# Percent change from cost basis to trigger action
TRIGGER = 0.1

# Percent change between consecutive trades
SPACER = 0.1

# Start balance in USD
START_BALANCE = 100000

# Percent of balance to use on each trade
TRADE_STRENGTH = 0.5

# Fee for each trade
FEE = 0.0025
FEE_MULT = 1 - FEE

api_key = secret.api_key
api_secret = secret.api_secret
client = CryptoHistoricalDataClient(api_key, api_secret)

# test range
# data available from 2021 - present
start_time = datetime(2021, 1, 1)
end_time = datetime(2021,1, 2)

# historical data request for trading data
trade_request = CryptoBarsRequest(
    symbol_or_symbols="BTC/USD",
    timeframe=TimeFrame(TRADE_INTERVAL, TimeFrameUnit.Hour),
    start=start_time,
    end=end_time
)

print("Retrieving bars...")
trade_bars = client.get_crypto_bars(trade_request)

print("Converting to DataFrame...")
trade_data = trade_bars.df

print("Testing...")

last_close = trade_data["close"].iloc[0]
transactions = 0
buy_and_hold = trade_data["close"].iloc[trade_data["close"].size - 1] / trade_data["close"].iloc[0]
# start with half invested and half not
usd_balance = 0.5 * START_BALANCE
btc_balance = (0.5 * START_BALANCE / trade_data["close"].iloc[0]) * FEE_MULT
volatile_count = 0

price_range = Range(RANGE_INTERVAL, TRADE_INTERVAL)
results = [START_BALANCE]

# Loop through price data
for i in range(trade_data["close"].size):
    close = trade_data["close"].iloc[i]
    balance = usd_balance + btc_balance * close
    results.append(balance)
    price_range.add(trade_data["high"].iloc[i], trade_data["low"].iloc[i])
    if price_range.size < price_range.capacity:
        continue

    range_diff = price_range.max - price_range.min

    change_since_last = -((close/last_close) - 1)

    if range_diff < close * 0.02:
        continue

    if abs(change_since_last) > SPACER:
        transactions += 1
        last_close = close

        if change_since_last > TRIGGER:
            # buy
            trade_value = ((usd_balance * TRADE_STRENGTH) / close) * FEE_MULT
            btc_balance += trade_value
            usd_balance *= (1 - TRADE_STRENGTH)
        else:
            # sell
            usd_balance += ((btc_balance * TRADE_STRENGTH) * close) * FEE_MULT
            btc_balance *= (1 - TRADE_STRENGTH)

print("USD: " + str(usd_balance))
print("BTC: " + str(btc_balance * trade_data["close"].iloc[trade_data["close"].size - 1]))
print()

final_balance = usd_balance + btc_balance * trade_data["close"].iloc[trade_data["close"].size - 1]
final_return = final_balance/START_BALANCE

print("Actions: " + str(transactions))
print("Final return: " + str(final_return))
print("Buy and hold: " + str(buy_and_hold))

x = np.arange(0, trade_data["close"].size)
btc_y = START_BALANCE * (trade_data["close"].iloc[x] / trade_data["open"].iloc[0])
results_y = np.array(results)[x]
plt.plot(x, btc_y, label = "BTC")
plt.plot(x, results_y, label = "Results")
plt.show()