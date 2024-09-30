from alpaca.data import TimeFrameUnit
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

import secret

TRADE_INTERVAL = 5

RANGE_INTERVAL = 30

# Percent change to trigger action
TRIGGER = 0.01

START_BALANCE = 100000

# Percent of balance to use on each trade
TRADE_STRENGTH = 0.5

VOLATILITY_CUTOFF = 0.01

# Initialize the client with your API key and secret
api_key = secret.api_key
api_secret = secret.api_secret
client = CryptoHistoricalDataClient(api_key, api_secret)

# Define the time range for the data
start_time = datetime(2022, 7, 4)
end_time = datetime(2023,8, 2)

# Create a request object for historical crypto bars
trade_request = CryptoBarsRequest(
    symbol_or_symbols="BTC/USD",
    timeframe=TimeFrame(TRADE_INTERVAL, TimeFrameUnit.Minute),
    start=start_time,
    end=end_time
)

range_request = CryptoBarsRequest(
    symbol_or_symbols="BTC/USD",
    timeframe=TimeFrame(RANGE_INTERVAL, TimeFrameUnit.Minute),
    start=start_time,
    end=end_time
)

print("Retrieving bars...")
# Fetch historical data using the client
trade_bars = client.get_crypto_bars(trade_request)
range_bars = client.get_crypto_bars(range_request)

print("Converting to DataFrame...")
# Convert to a DataFrame (bars.df is a pandas DataFrame)
trade_data = trade_bars.df
range_data = range_bars.df

print(trade_data)

# pd.set_option('display.max_rows', None)  # Show all rows
# pd.set_option('display.max_columns', None)  # Show all columns

print("Testing...")

last_open = trade_data["open"].iloc[0]
count = 0
buy_and_hold = trade_data["open"].iloc[trade_data["open"].size - 1] / trade_data["open"].iloc[0]
usd_balance = 0.5 * START_BALANCE
btc_balance = 0.5 * START_BALANCE / last_open
volatile_count = 0

for i in range(trade_data["open"].size):
    open = trade_data["open"].iloc[i]
    high = trade_data["high"].iloc[i]
    low = trade_data["low"].iloc[i]

    percent_change = 1 - (open/last_open)
    range_index = int(i / RANGE_INTERVAL)
    range = range_data["high"].iloc[range_index] - range_data["low"].iloc[range_index]
    volatile = range > open * VOLATILITY_CUTOFF

    if abs(percent_change) > TRIGGER:
        count += 1
        last_open = open
        if volatile:
            volatile_count += 1

        if ((percent_change > TRIGGER) and volatile) or ((percent_change < TRIGGER) and not volatile):
            # buy
            btc_balance += (usd_balance * TRADE_STRENGTH) / open
            usd_balance *= (1 - TRADE_STRENGTH)
        else:
            # sell
            usd_balance += (btc_balance * TRADE_STRENGTH) * open
            btc_balance *= (1 - TRADE_STRENGTH)

        # print("USD: " + str(usd_balance))
        # print("BTC: " + str(btc_balance * open))
        # print()

final_balance = usd_balance + btc_balance * trade_data["open"].iloc[trade_data["open"].size - 1]
final_return = final_balance/START_BALANCE

print("Actions: " + str(count))
print("Volatile trades: " + str(volatile_count))
print("Final return: " + str(final_return))
print("Buy and hold: " + str(buy_and_hold))
