from time import sleep
import datetime

from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from secret import api_key, api_secret

def buy(quantity, trading_client):
    market_order_data = MarketOrderRequest(
        symbol="BTC/USD",
        qty=quantity,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )

    trading_client.submit_order(order_data=market_order_data)
    print("Bought: " + str(datetime.datetime.now()))

def sell(quantity, trading_client):
    market_order_data = MarketOrderRequest(
        symbol="BTC/USD",
        qty=quantity,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )

    trading_client.submit_order(order_data=market_order_data)

    print("Sold: " + str(datetime.datetime.now()))

def main():
    history_client = CryptoHistoricalDataClient()
    request_params = CryptoLatestQuoteRequest(symbol_or_symbols="BTC/USD")

    trading_client = TradingClient(api_key,
                                   api_secret, paper=True)
    account = trading_client.get_account()

    buying_power = float(account.buying_power)

    latest_quote = history_client.get_crypto_latest_quote(request_params)
    ask = latest_quote["BTC/USD"].ask_price
    bid = latest_quote["BTC/USD"].bid_price
    last_bid = bid

    while 1 :
        spread = ask - bid

        latest_quote = history_client.get_crypto_latest_quote(request_params)
        ask = latest_quote["BTC/USD"].ask_price
        bid = latest_quote["BTC/USD"].bid_price



        if bid - last_bid > spread:
            sell(float(trading_client.get_open_position("BTCUSD").qty) / 2, trading_client)
            last_bid = bid
        elif bid - last_bid < -spread:
            buy((buying_power/2) / ask, trading_client)
            last_bid = bid

        sleep(1)

if __name__ == '__main__':
    main()