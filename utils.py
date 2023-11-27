import numpy as np
import pandas as pd
import yfinance as yf
from datetime import date, timedelta


def calculate_ema(data, window):
    return data['Close'].ewm(span=window, adjust=False).mean()

def get_ema_cross_stocks(symbol):
    try:
        # Fetch historical data using yfinance
        stock_data = yf.download(symbol, start=date.today()-timedelta(days=500), end=date.today())

        if stock_data.empty:
            raise ValueError(f"No data available for {symbol}")

        # Calculate 10-day and 20-day Exponential Moving Averages (EMA)
        stock_data['ema_10'] = calculate_ema(stock_data, 10)
        stock_data['ema_20'] = calculate_ema(stock_data, 20)

        # Identify EMA cross
        cross_signal = (stock_data['ema_10'] > stock_data['ema_20']) & (stock_data['ema_10'].shift(1) <= stock_data['ema_20'].shift(1))

        # Filter dates with EMA cross in the last 5 days
        recent_crosses = cross_signal.index[cross_signal][-1:]

        return symbol, recent_crosses

    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return symbol, None

    
    
def get_market_cap(symbol):
    company = yf.Ticker(symbol)
    company_info = company.info
    
    company_dict = {'nse_symbol': symbol,
                    'company': company_info['shortName']
                    'market_cap': company_info['marketCap']*1.0/10e7, 
                    'free_float': company_info['floatShares']*1.0/company_info['sharesOutstanding']}
    return company_dict