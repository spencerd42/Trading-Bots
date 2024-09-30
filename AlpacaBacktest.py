from alpaca.data import TimeFrameUnit
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

import secret

# Time interval for data
INTERVAL = 10

# Percent change to trigger action
TRIGGER = 0.01

START_BALANCE = 100000

# Initialize the client with your API key and secret
api_key = secret.api_key
api_secret = secret.api_secret
client = CryptoHistoricalDataClient(api_key, api_secret)

# Define the time range for the data
start_time = datetime(2022, 7, 8)
end_time = datetime(2023, 9, 15)

# Create a request object for historical crypto bars (BTCUSD, 1 minute bars)
request_params = CryptoBarsRequest(
    symbol_or_symbols="BTC/USD", # Use symbol_or_symbols instead of symbol
    timeframe=TimeFrame(INTERVAL, TimeFrameUnit.Minute),  # Time interval
    start=start_time,            # Start date of the data
    end=end_time                 # End date of the data
)

print("Retrieving bars...")
# Fetch historical data using the client
bars = client.get_crypto_bars(request_params)

print("Converting to DataFrame...")
# Convert to a DataFrame (bars.df is a pandas DataFrame)
data = bars.df

# pd.set_option('display.max_rows', None)  # Show all rows
# pd.set_option('display.max_columns', None)  # Show all columns

print("Testing...")

last_open = data["open"].iloc[0]
count = 0
buy_and_hold = data["open"].iloc[data["open"].size - 1] / data["open"].iloc[0]
usd_balance = 0.5 * START_BALANCE
btc_balance = 0.5 * START_BALANCE / last_open
volatile_count = 0

for i in range(data["open"].size):
    open = data["open"].iloc[i]
    high = data["high"].iloc[i]
    low = data["low"].iloc[i]

    percent_change = 1 - (open/last_open)
    range = high - low
    volatile = range > open * 0.01

    if abs(percent_change) > TRIGGER:
        count += 1
        last_open = open
        if volatile:
            volatile_count += 1

        if ((percent_change > TRIGGER) and volatile) or ((percent_change < TRIGGER) and not volatile):
            # buy
            btc_balance += (usd_balance / 2) / open
            usd_balance /= 2
        else:
            # sell
            usd_balance += (btc_balance / 2) * open
            btc_balance /= 2

        print("USD: " + str(usd_balance))
        print("BTC: " + str(btc_balance * open))
        print()

final_balance = usd_balance + btc_balance * data["open"].iloc[data["open"].size - 1]
final_return = final_balance/START_BALANCE

print("Actions: " + str(count))
print("Volatile trades: " + str(volatile_count))
print("Final return: " + str(final_return))
print("Buy and hold: " + str(buy_and_hold))
