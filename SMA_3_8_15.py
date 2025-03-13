
from datetime import datetime, timedelta
from lumibot.backtesting import YahooDataBacktesting
from lumibot.credentials import IS_BACKTESTING
from lumibot.strategies import Strategy
from lumibot.traders import Trader
import numpy as np
import pandas as pd
from alpaca_trade_api import REST
import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets/v2"



class SMA_3_8_15(Strategy):

    def initialize(self, symbol:str="GLD", quantity:int = 0, frequency:str = "24H", cash_at_risk:float=.5, start:str="2023-01-01"): 
        self.symbol = symbol
        self.sleeptime = frequency 
        self.last_trade = None 
        self.cash_at_risk = cash_at_risk
        self.quantity = quantity
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
        self.vars.signal = None
        self.vars.start = start
    
    def on_trading_iteration(self):
        symbol = self.symbol
        bars = self.get_historical_prices(symbol, 22, "day")
        gld = bars.df
        gld['SMA_5'] = gld['close'].rolling(5).mean() # We calculate the 5 day moving average
        gld['SMA_8'] = gld['close'].rolling(8).mean() # We calculate the 8 day moving average
        gld['SMA_13'] = gld['close'].rolling(13).mean() # We calculate the 13 day moving average
        
        #generate buy signal
        gld['Signal'] = np.where(
                                (gld['SMA_5'] > gld['SMA_13']) & (gld['SMA_8'] > gld['SMA_13']) & 
                                (gld['SMA_5'].shift(1) < gld['SMA_13'].shift(1)) & (gld['SMA_8'].shift(1) < gld['SMA_13'].shift(1)), 
                                "BUY",  # If these conditions are met we send a buy signal 
                                None    # Otherwise we send no signal
                                )

        gld['Signal'] = np.where(
                                (gld['SMA_5'] < gld['SMA_13']) & (gld['SMA_8'] < gld['SMA_13']) & 
                                (gld['SMA_5'].shift(1) > gld['SMA_13'].shift(1)) & (gld['SMA_8'].shift(1) > gld['SMA_13'].shift(1)), 
                                "SELL", # If conditions are met we send a sell signal
                                gld['Signal'] # Otherwise we keep the previous signal
                            )
        self.vars.signal = gld.iloc[-1].Signal # Last signal sent is what we use to place the trade
        
        price = self.get_last_price(symbol)
        cash = self.get_cash()
        quantity = cash * .5 // price
        if self.vars.signal == 'BUY':
            pos = self.get_position(symbol)
            if pos:
                self.sell_all()
                
            order = self.create_order(symbol, quantity, "buy")
            self.submit_order(order)

        elif self.vars.signal == 'SELL':
            pos = self.get_position(symbol)
            if pos:
                self.sell_all()
            cash = self.get_cash()
            quantity = cash * .5 // price    
            order = self.create_order(symbol, quantity, "sell")
            self.submit_order(order)
        

def excecute_SMA_3_8_15(broker, symbol, quantity, frequency, cash_at_risk, backtest, start_date, end_date):
    strategy = SMA_3_8_15(name='sma_3_8_15', broker=broker, 
                    parameters={"symbol":symbol, "quantity": quantity, "frequency": frequency, "cash_at_risk": cash_at_risk, "start":start_date})
    if backtest:
        strategy.backtest(
            YahooDataBacktesting, 
            start_date, 
            end_date, 
            benchmark_asset= symbol
        )
                                    
    else:
        trader = Trader(strategy)
        trader.run()   

