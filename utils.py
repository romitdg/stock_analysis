import numpy as np
import pandas as pd
import yfinance as yf
from datetime import date, timedelta


def calculate_ema(data, window):
    return data['Close'].ewm(span=window, adjust=False).mean()

def get_ema_cross_stocks(symbol:str):
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
    
    
def get_market_cap(symbol:str) -> dict:
    company = yf.Ticker(symbol)
    company_info = company.info
    
    try:
        mkt_cap = company_info['marketCap']*1.0/10e7
    except KeyError:
        mkt_cap = None
        
    try:
        free_float = company_info['floatShares']*1.0/company_info['sharesOutstanding']
    except KeyError:
        free_float = None
        
    
    company_dict = {'nse_symbol': symbol,
                    'company': company_info['shortName'],
                    'market_cap': mkt_cap, 
                    'free_float': free_float}
    return company_dict



def nse_symbols() -> list:
    nse_names = pd.read_csv('EQUITY_L.csv')

    nse_names['SYMBOL_UPTD'] = nse_names['SYMBOL'].map(lambda x : str(x) + '.NS')

    return list(set(nse_names['SYMBOL_UPTD'].tolist()))


def execute_ema_cross_process(nse_names_list:list):
    ema_list = []
    for symbol in nse_names_list:
        symbol, crosses = get_ema_cross_stocks(symbol)
        company_info = get_market_cap(symbol)

        if crosses is not None and len(crosses) > 0 and crosses[0]>pd.Timestamp('now').floor('D') + pd.offsets.Day(-5):
            print(f"{symbol} has EMA cross on {crosses[0].date()}")
            company_info['EMA_Cross_Date'] = crosses[0].date()
            ema_list += [company_info]
        #elif crosses is not None:
         # print(f"{symbol} doesn't have EMA cross in the last 5 days.")
    df = pd.DataFrame(ema_list)
    df_sorted = df.sort_values(by='EMA_Cross_Date',ascending=False)
    df_sorted=df_sorted.reset_index(drop=True)
    df_sorted.to_csv('EMA Cross.csv', index=False)
    return 0
    

def main():
    execute_ema_cross_process(nse_symbols())
    

    
if __name__=="__main__": 
    main()