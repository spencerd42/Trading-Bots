from time import sleep
from datetime import datetime, timedelta
import pytz

from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

from secret import api_key, api_secret

def buy(quantity, trading_client):
    market_order_data = MarketOrderRequest(
        symbol="BTC/USD",
        qty=quantity,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )

    trading_client.submit_order(order_data=market_order_data)
    print("Bought: " + str(datetime.now()))

def sell(quantity, trading_client):
    market_order_data = MarketOrderRequest(
        symbol="BTC/USD",
        qty=quantity,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )

    trading_client.submit_order(order_data=market_order_data)

    print("Sold: " + str(datetime.now()))

def main():
    history_client = CryptoHistoricalDataClient()
    quote_params = CryptoLatestQuoteRequest(symbol_or_symbols="BTC/USD")

    trading_client = TradingClient(api_key, api_secret, paper=True)
    account = trading_client.get_account()

    latest_quote = history_client.get_crypto_latest_quote(quote_params)
    ask = latest_quote["BTC/USD"].ask_price
    bid = latest_quote["BTC/USD"].bid_price
    last_bid = bid

    while 1 :
        buying_power = float(account.buying_power)
        spread = ask - bid

        latest_quote = history_client.get_crypto_latest_quote(quote_params)
        ask = latest_quote["BTC/USD"].ask_price
        bid = latest_quote["BTC/USD"].bid_price

        # Define the time range (last 30 minutes)
        end_time = datetime.now(tz=pytz.timezone('Etc/GMT-0'))
        start_time = end_time - timedelta(minutes=30)

        # Create the request for BTC data
        bars_params = CryptoBarsRequest(
            symbol_or_symbols=['BTC/USD'],
            timeframe=TimeFrame.Minute,
            start=start_time,
            end=end_time
        )

        # Get the historical BTC data
        btc_bars = history_client.get_crypto_bars(bars_params).df

        # Find the highest BTC price in the last 30 minutes
        highest_price = btc_bars['high'].max()
        lowest_price = btc_bars['low'].min()

        price_range = highest_price - lowest_price

        if bid - last_bid > spread:
            if price_range/bid > 0.005:
                print("Momentum")
                buy((buying_power/2) / ask, trading_client)
                print()
            else:
                print("Mean Reversion")
                sell(float(trading_client.get_open_position("BTCUSD").qty) / 2, trading_client)
                print()
            last_bid = bid
        elif bid - last_bid < -spread:
            if price_range / bid > 0.005:
                print("Momentum")
                sell(float(trading_client.get_open_position("BTCUSD").qty) / 2, trading_client)
            else:
                print("Mean Reversion")
                buy((buying_power/2) / ask, trading_client)
                print()
            last_bid = bid

        sleep(1)

if __name__ == '__main__':
    main()