from alpaca.data import TimeFrameUnit
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from Range import Range
import secret

# check for trade opportunities every x minutes
TRADE_INTERVAL = 10

# Used to calculate price range over the last x minutes
RANGE_INTERVAL = 240

MIN_HOURLY_CHANGE = 0
MIN_RANGE_DIFF = (RANGE_INTERVAL / 60) * MIN_HOURLY_CHANGE

TRIGGER = 0.75

# Fee for each trade
FEE = 0.0025
FEE_MULT = 1 - FEE

api_key = secret.api_key
api_secret = secret.api_secret
client = CryptoHistoricalDataClient(api_key, api_secret)

# test range
# data available from 2021 - present
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

START_BALANCE = trade_data["open"].iloc[0]
# Percent of starting balance to use on each trade
TRADE_STRENGTH = 0.1
TRADE_AMOUNT = START_BALANCE * TRADE_STRENGTH

cost_basis = trade_data["close"].iloc[0]
transactions = 0
buy_and_hold = trade_data["close"].iloc[trade_data["close"].size - 1] / trade_data["close"].iloc[0]
# start with half invested and half not
usd_balance = 0.5 * START_BALANCE
btc_balance = (0.5 * START_BALANCE / trade_data["close"].iloc[0]) * FEE_MULT
volatile_count = 0

results = [START_BALANCE]

# Loop through price data
for i in range(trade_data["close"].size):
    close = trade_data["close"].iloc[i]
    balance = usd_balance + btc_balance * close
    results.append(balance)
    change = close / cost_basis

    if change > 2:
        usd_balance += btc_balance * close * FEE_MULT
        btc_balance = 0

    if balance / START_BALANCE > trade_data["close"].iloc[i] / trade_data["close"].iloc[0] and btc_balance == 0:
        btc_balance += ((usd_balance / 2) / close)
        usd_balance /= 2

print("USD: " + str(usd_balance))
print("BTC: " + str(btc_balance * trade_data["close"].iloc[trade_data["close"].size - 1]))
print()

final_balance = usd_balance + btc_balance * trade_data["close"].iloc[-1]
final_return = final_balance/START_BALANCE

print("Actions: " + str(transactions))
print("Final return: " + str(final_return))
print("Buy and hold: " + str(buy_and_hold))
print("Buy and hold 1/2: " + str(1 + (buy_and_hold - 1) / 2))

x = np.arange(0, trade_data["close"].size)
btc_y = trade_data["close"].iloc[x]
results_y = np.array(results)[x]
plt.plot(x, btc_y, label = "BTC")
plt.plot(x, results_y, label = "Results")
plt.show()