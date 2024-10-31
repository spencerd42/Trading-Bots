from alpaca.data import TimeFrameUnit
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import talib
import pandas

import secret

TRADE_INTERVAL = 1

# Fee for each trade
FEE = 0.00
FEE_MULT = 1 - FEE

api_key = secret.api_key
api_secret = secret.api_secret
client = CryptoHistoricalDataClient(api_key, api_secret)

# test range
# data available from 2021 - present
start_time = datetime(2022, 1, 1)
end_time = datetime(2023,1, 1)

# historical data request for trading data
trade_request = CryptoBarsRequest(
    symbol_or_symbols="eth/USD",
    timeframe=TimeFrame(TRADE_INTERVAL, TimeFrameUnit.Day),
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
live_data = pandas.DataFrame()
above_signal = False
for i in range(trade_data["close"].size):
    open = trade_data["open"].iloc[i]
    close = trade_data["close"].iloc[i]
    balance = usd_balance + btc_balance * close
    results.append(balance)
    new_data = pandas.DataFrame({'close': [close]})
    live_data = pandas.concat([live_data, new_data], ignore_index=True)

    live_data['macd'], live_data['macdsignal'], live_data['macdhist'] = talib.MACD(live_data['close'], fastperiod=12, slowperiod=26, signalperiod=9)

    macd_val = live_data['macd'].iloc[-1]
    signal_val = live_data['macdsignal'].iloc[-1]

    if macd_val > signal_val and not above_signal and (trade_data["high"].iloc[i] - trade_data["low"].iloc[i]) / trade_data["low"].iloc[i] > 0.1:
        # print("Moving above " + str(i))
        above_signal = True
        btc_balance += (usd_balance / close) * FEE_MULT
        usd_balance = 0
        transactions += 1
    elif macd_val < signal_val and above_signal:
        # print("Moving below " + str(i))
        above_signal = False
        usd_balance += btc_balance * close * FEE_MULT
        btc_balance = 0
        transactions += 1


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


# # Calculate MACD
# macd, macdsignal, macdhist = talib.MACD(trade_data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
#
# # Add MACD values to the DataFrame
# trade_data['macd'] = macd
# trade_data['macdsignal'] = macdsignal
# trade_data['macdhist'] = macdhist
#
# above_signal = False
# for i in range(trade_data['close'].size):
#     macd_val = trade_data['macd'].iloc[i]
#     signal_val = trade_data['macdsignal'].iloc[i]
#     if macd_val > signal_val and not above_signal:
#         print("Moving above " + str(i))
#         above_signal = True
#     elif macd_val < signal_val and above_signal:
#         print("Moving below " + str(i))
#         above_signal = False

plt.show()