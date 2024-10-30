from alpaca.data import TimeFrameUnit
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

import secret

# check for trade opportunities every x minutes
TRADE_INTERVAL = 10

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
    timeframe=TimeFrame(TRADE_INTERVAL, TimeFrameUnit.Hour),
    start=start_time,
    end=end_time
)

print("Retrieving bars...")
trade_bars = client.get_crypto_bars(trade_request)

print("Converting to DataFrame...")
trade_data = trade_bars.df

print("Testing...")

START_BALANCE = trade_data["open"].iloc[0]

cost_basis = trade_data["close"].iloc[0]
transactions = 0
buy_and_hold = trade_data["close"].iloc[trade_data["close"].size - 1] / trade_data["close"].iloc[0]
# start with half invested and half not
usd_balance = 0.5 * START_BALANCE
start_usd = usd_balance
btc_balance = ((START_BALANCE * 0.5) / trade_data["close"].iloc[0]) * FEE_MULT
start_btc = btc_balance
# usd_balance = 0
# btc_balance = (START_BALANCE / trade_data["close"].iloc[0]) * FEE_MULT
volatile_count = 0

results = [START_BALANCE]
hold = [START_BALANCE]

# Loop through price data
for i in range(trade_data["close"].size):
    open = trade_data["open"].iloc[i]
    close = trade_data["close"].iloc[i]
    balance = usd_balance + btc_balance * close
    results.append(balance)
    hold.append(start_usd + start_btc * close)
    cur_return = (balance / START_BALANCE) - 1

    above_hold = cur_return > trade_data["close"].iloc[i] / trade_data["close"].iloc[0]

    change = (close - open) / open
    if abs(change) < 0.01:
        continue
    transactions += 1
    if abs(change) > 1:
        change = 1 * (change / abs(change))
    if change >= 0:
        # usd_balance += (btc_balance * change) * close * FEE_MULT
        # btc_balance *= 1 - change
        trade_amount = (usd_balance * abs(change))
        trade_amount *= 5
        if trade_amount > usd_balance:
            trade_amount = usd_balance
        btc_balance += (trade_amount / close) * FEE_MULT
        usd_balance -= trade_amount
    elif change < 0:
        # btc_balance += ((usd_balance * abs(change)) / close) * FEE_MULT
        # usd_balance *= change + 1
        trade_amount = (btc_balance * abs(change)) * close
        trade_amount *= 5
        if trade_amount / close > btc_balance:
            trade_amount = btc_balance * close
        usd_balance += trade_amount * FEE_MULT
        btc_balance -= trade_amount / close

    # if change > 0.02:
    #     btc_balance += (usd_balance / close) * FEE_MULT
    #     usd_balance = 0
    # elif change < -0.01:
    #     usd_balance += btc_balance * close * FEE_MULT
    #     btc_balance = 0

    # if change > 0.04:
    #     print(i)
    #     btc_balance += (usd_balance / close) * 0.5 * FEE_MULT
    #     usd_balance /= 2

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
hold_y = np.array(hold)[x]
plt.plot(x, btc_y, label = "BTC")
plt.plot(x, results_y, label = "Results")
plt.plot(x, hold_y, label = "Hold")
plt.show()