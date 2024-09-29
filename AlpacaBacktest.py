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

# Initialize the client with your API key and secret
api_key = secret.api_key
api_secret = secret.api_secret
client = CryptoHistoricalDataClient(api_key, api_secret)

# Define the time range for the data (e.g., start and end date)
start_time = datetime(2023, 9, 1)
end_time = datetime(2024, 9, 1)

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

last_open = data["open"].iloc[0]
count = 0

print("Testing...")
for open in data["open"]:
    if abs(1 - (open/last_open)) > TRIGGER:
        count += 1
        last_open = open
print("Actions: " + str(count))
