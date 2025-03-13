from datetime import datetime
from lumibot.backtesting import BacktestingBroker, PolygonDataBacktesting , YahooDataBacktesting
from lumibot.credentials import IS_BACKTESTING
from lumibot.strategies import Strategy
from lumibot.traders import Trader
import os
from alpaca_trade_api import REST

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets/v2"

class SwingHigh(Strategy):
    def initialize(self, symbol:str="SPY", quantity:int = 10, frequency: str = "1M", cash_at_risk:float=.5): 
        self.symbol = symbol
        self.sleeptime = frequency 
        self.last_trade = None 
        self.cash_at_risk = cash_at_risk
        self.quantity = quantity
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
        self.vars.data = []
        self.vars.order_number = 0
    
    def position_sizing(self): 
        cash = self.get_cash() 
        last_price = self.get_last_price(self.symbol)
        if self.quantity==0:
            quantity = round(cash * self.cash_at_risk / last_price,0)
        else: 
            quantity = self.quantity
        return int(quantity)

    def on_trading_iteration(self):
        symbol = self.symbol
        entry_price = self.get_last_price(symbol)
        quantity = self.position_sizing()
        #shows any existing positions
        self.log_message(f"Position: {self.get_position(symbol)}")
        self.vars.data.append(entry_price)

        if len(self.vars.data) > 3:
            temp = self.vars.data[-3:]
            if temp[-1] > temp[1] > temp[0]:
                #trade confomration / last three prices
                self.log_message(f"Last three prices: {temp}")
                order = self.create_order(symbol, quantity, 'buy')
                self.submit_order(order)
                self.vars.order_number += 1

                if self.vars.order_number == 1:
                    entry_price = temp[-1]

        if self.get_position(symbol) and self.vars.data[-1] < entry_price * .9975:
            position = self.get_position(symbol)
            self.get_selling_order(position)
            self.submit_order(order)
            order_number = 0
        elif self.get_position(symbol) and self.vars.data[-1] > entry_price * 1.01:
            position = self.get_position(symbol)
            self.get_selling_order(position)
            self.submit_order(order)
            order_number = 0

    def before_market_closes(self):
        self.sell_all()
        self.vars.order_number = 0


def execute_swinghigh(broker, backtest, symbol, quantity, frequency, cash_at_risk, start_date, end_date):
    strategy = SwingHigh(name='swing_high', broker=broker, 
                    parameters={"symbol":symbol, "quantity": quantity, "frequency": frequency, "cash_at_risk": cash_at_risk})
    if backtest:
        SwingHigh.backtest(
            PolygonDataBacktesting,
            backtesting_start=start_date,
            backtesting_end=end_date,
            benchmark_asset = symbol,
            polygon_api_key=os.getenv("POLYGON_API_KEY")
        )
    else:
        trader = Trader(strategy)
        trader.run()               
    
