from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting, PolygonDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime 
from alpaca_trade_api import REST 
from timedelta import Timedelta 
from finbert_utils import estimate_sentiment
import os
from sentiment import Sentiment
from swing_high import SwingHigh
from sentiment import excecute_sentiment
from swing_high import execute_swinghigh
from SMA_3_8_15 import excecute_SMA_3_8_15


API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets/v2"

ALPACA_CREDS = {
    "API_KEY":API_KEY, 
    "API_SECRET": API_SECRET, 
    "PAPER": True
}
broker = Alpaca(ALPACA_CREDS) 

start_date = datetime(2023,1,1)
end_date = datetime(2024,11,25)

symbol = "GLD"   #ticker symbol
cash_at_risk = .5 #risk factor to determine how much cash to risk can be used intead of quantity
quantity = 10 #quantity of shares if not specified will be calculated by the bot using risk factor
frequency = "24H" #frequency of trading we want the bot to place trades
backtest = True #enbale backtesting when true / live trading when false







#excecute_sentiment(broker, symbol, quantity, frequency, cash_at_risk, backtest, start_date, end_date) #excutes the sentiment strategy
#execute_swinghigh(broker, symbol, quantity, frequency, cash_at_risk, backtest, start_date, end_date) #excutes the swing high strategy
excecute_SMA_3_8_15(broker, symbol, quantity, frequency, cash_at_risk, backtest, start_date, end_date)

# Trader(strategy).run()
# run the bot
