from alpaca.data import TimeFrameUnit
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

import secret

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
end_time = datetime(2021,6, 7)

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

cost_basis = trade_data["close"].iloc[0]
transactions = 0
buy_and_hold = trade_data["close"].iloc[trade_data["close"].size - 1] / trade_data["close"].iloc[0]
# start with half invested and half not
usd_balance = START_BALANCE
btc_balance = 0

take_profit = 0
stop_loss = 0
max_trade_balance = START_BALANCE

results = [START_BALANCE]

# Loop through price data
last_buy = trade_data["close"].iloc[0]
for i in range(trade_data["close"].size):
    open = trade_data["open"].iloc[i]
    close = trade_data["close"].iloc[i]
    balance = usd_balance + btc_balance * close
    results.append(balance)
    cur_return = (balance / START_BALANCE) - 1

    change = (close - open) / open
    max_trade_balance = max(max_trade_balance, balance)

    if change > 0.01 and btc_balance == 0:
        take_profit = change * 4
        stop_loss = change

        btc_balance += (usd_balance / close) * FEE_MULT
        usd_balance = 0
        last_buy = close
        max_trade_balance = balance
        print("buy: " + str(close) + " at i = " + str(i))
    elif (last_buy - close) / last_buy < -take_profit and btc_balance > 0:
        print("take profit: " + str(close) + " at i = " + str(i))
        print()
        usd_balance += btc_balance * close * FEE_MULT
        btc_balance = 0
    elif (last_buy - close) / last_buy > stop_loss and btc_balance > 0:
        print(change)
        print("stop loss: " + str(close) + " at i = " + str(i))
        print()
        usd_balance += btc_balance * close * FEE_MULT
        btc_balance = 0
    elif (max_trade_balance - balance) / max_trade_balance > 0.05 and btc_balance > 0:
        print("drawdown protection: " + str(close) + " at i = " + str(i))
        print()
        usd_balance += btc_balance * close * FEE_MULT
        btc_balance = 0

    # if (last_buy - close) / last_buy > 0.01 and btc_balance > 0:
    #     print("stop loss: " + str(i))
    #     usd_balance += btc_balance * close * FEE_MULT
    #     btc_balance = 0
    # elif (last_buy - close) / last_buy < -0.05 and btc_balance > 0:
    #     print("take profit: " + str(i))
    #     usd_balance += btc_balance * close * FEE_MULT
    #     btc_balance = 0
    # elif change >= 0.05 and btc_balance == 0:
    #     btc_balance += (usd_balance / close) * FEE_MULT
    #     usd_balance = 0
    #     last_buy = close
    # else:
    #     transactions -= 1

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