import calendar
from datetime import datetime
from datetime import timedelta
from lumibot.backtesting import PolygonDataBacktesting
from lumibot.credentials import IS_BACKTESTING
from lumibot.strategies import Strategy
from lumibot.entities import Asset
from lumibot.traders import Trader
from alpaca_trade_api import REST
import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets/v2"

class BullishCallSpread(Strategy):

    def initialize(self, symbol:str = "NONE", quantity:int = 0, frequency:str = "24H", cash_at_risk:float = 0.5, spread_size:int = 5, delta:int = 1): 
        self.symbol = symbol #ticker symbol
        self.sleeptime = frequency #time to sleep before next iteration
        self.last_trade = None 
        self.cash_at_risk = cash_at_risk
        self.quantity = quantity #quantity of shares to trade
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET) 
        self.spread_size = spread_size #spread size
        self.delta = delta #time to expiration in days

    def on_trading_iteration(self):
        symbol = self.symbol
        date = self.get_datetime().replace(tzinfo=None).date()
        exp = self.get_next_exp(date)
        price = self.get_last_price(symbol)
        size = self.spread_size
        strike_low, strike_high = self.calc_strikes(price, size)
        delta = timedelta(days=self.delta)
        close = exp - delta #expiration date


        long_call = Asset(
            symbol= symbol,
            asset_type = Asset.AssetType.OPTION,
            expiration = exp,
            strike = strike_low,
            right = Asset.OptionRight.CALL 
        )


        short_call = Asset(
            symbol= symbol,
            asset_type = Asset.AssetType.OPTION,
            expiration = exp,
            strike = strike_high,
            right = Asset.OptionRight.CALL 
        )


        positions = len(self.get_positions())
        if positions <= 1:
            quantity = self.quantity
            orders = [
                self.create_order(long_call, quantity, "buy"),
                self.create_order(short_call, quantity, "sell")
            ]

            for order in orders:
                self.submit_order(order)

        if date == close:
            exp = self.get_next_exp(date)
            self.sell_all()
   
   
    def find_strike(self, price, base=5):
        return round(price/base) * 5
    

    def calc_strikes(self, price, spread_size = 5):
        atm = self.find_strike(price)
        return atm, atm + spread_size
    

    def get_next_exp(self, date):
        first_friday = 0
        
        if date.month == 12:
            year = date.year + 1    
        else:
            year = date.year
        if date.month == 12:
            month = (date.month + 1) % 12
        else:
            month = date.month + 1    
                
        next_month = calendar.monthcalendar(year, month)
        
        for week in next_month:
            for day in week:
                if day > 0 and calendar.weekday(year, month, day)  == calendar.FRIDAY:
                    first_friday = day
                    break
            if first_friday:
                break    
        return datetime(year, month, first_friday + 14).date()       


def excecute_bull_spread(broker, symbol, quantity, frequency, cash_at_risk, backtest, start_date, end_date, spread_size, delta):
    strategy = BullishCallSpread(name='bull_spread', broker=broker, 
                    parameters={"symbol":symbol, "quantity": quantity, "frequency": frequency, "cash_at_risk": cash_at_risk, "spread_size": spread_size, "delta": delta})
    if backtest:
        strategy.backtest(
            PolygonDataBacktesting, 
            start_date, 
            end_date, 
            benchmark_asset= symbol,
            parameters={"symbol":symbol, "quantity": quantity, "frequency": frequency, "cash_at_risk": cash_at_risk, "spread_size": spread_size, "delta": delta}
        )
                                    
    else:
        trader = Trader(strategy)
        trader.run()