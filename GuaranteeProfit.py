from alpaca.data import TimeFrameUnit
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

from Range import Range
import secret

# check for trade opportunities every x minutes
TRADE_INTERVAL = 50

# Used to calculate price range over the last x minutes
RANGE_INTERVAL = 150

# Percent change to trigger action
TRIGGER = 0.1

# Start balance in USD
START_BALANCE = 100000

# Percent of balance to use on each trade
TRADE_STRENGTH = 0.1

# Consider the currency volatile if the price range is greater than this percentage
VOLATILITY_CUTOFF = 1

# Fee for each trade
FEE = 0.0025
FEE_MULT = 1 - FEE

api_key = secret.api_key
api_secret = secret.api_secret
client = CryptoHistoricalDataClient(api_key, api_secret)

# test range
# data available from 2021 - present
# start_time = datetime(2024, 1, 1)
# end_time = datetime(2024,10, 1)
start_time = datetime(2021, 1, 1)
end_time = datetime(2022,1, 1)

# historical data request for trading data
trade_request = CryptoBarsRequest(
    symbol_or_symbols="BTC/USD",
    timeframe=TimeFrame(TRADE_INTERVAL, TimeFrameUnit.Minute),
    start=start_time,
    end=end_time
)

print("Retrieving bars...")
trade_bars = client.get_crypto_bars(trade_request)

print("Converting to DataFrame...")
trade_data = trade_bars.df

print("Testing...")

avg_cost_basis = trade_data["open"].iloc[0]
last_open = trade_data["open"].iloc[0]
transactions = 0
buy_and_hold = trade_data["open"].iloc[trade_data["open"].size - 1] / trade_data["open"].iloc[0]
# start with half invested and half not
usd_balance = 0
btc_balance = (START_BALANCE / trade_data["open"].iloc[0]) * FEE_MULT
volatile_count = 0

price_range = Range(RANGE_INTERVAL, TRADE_INTERVAL)

for i in range(trade_data["open"].size):
    price_range.add(trade_data["high"].iloc[i], trade_data["low"].iloc[i])
    if price_range.size < price_range.capacity:
        continue

    range_diff = price_range.max - price_range.min

    open = trade_data["open"].iloc[i]

    cost_basis_change = (open/avg_cost_basis) - 1
    change_since_last = (open/last_open) - 1
    volatile = range_diff > open * VOLATILITY_CUTOFF

    if cost_basis_change > TRIGGER:
        transactions += 1
        last_open = open
        if volatile:
            volatile_count += 1
        # sell
        usd_balance += ((btc_balance * TRADE_STRENGTH) * open) * FEE_MULT
        btc_balance *= (1 - TRADE_STRENGTH)

        # print("USD: " + str(usd_balance))
        # print("BTC: " + str(btc_balance * open))
        # print()

final_balance = usd_balance + btc_balance * trade_data["open"].iloc[trade_data["open"].size - 1]
final_return = final_balance/START_BALANCE

print("Actions: " + str(transactions))
print("Volatile trades: " + str(volatile_count))
print("Final return: " + str(final_return))
print("Buy and hold: " + str(buy_and_hold))
