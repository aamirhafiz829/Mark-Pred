#import requests
from flask import Flask, jsonify, send_file
import yfinance as yf
from datetime import datetime, timedelta
import os
import pandas as pd
import matplotlib.pyplot as plt



# Make a button that goes to this route

def obtain_stock(tickerSymbol):
    startDate = datetime.datetime.now() - datetime.timedelta(days=10*365)
    endDate = datetime.datetime.now()

    # Fetch the historical data
    # Add error handling
    tickerData = yf.Ticker(tickerSymbol)
    tickerDf = tickerData.history(period='1d', start=startDate, end=endDate)

    # Save the data to a CSV file
    path_csv = 'data/' + tickerSymbol + '_10_years.csv'
    print("saving to csv...")
    tickerDf.to_csv(path_csv)
    print("saved to csv")
    try:
        # Get the size of the file in bytes
        size_bytes = os.path.getsize(path_csv)
        
        # Print the size in a readable format (e.g., in KB, MB, etc.)
        print(f"Size of '{path_csv}': {size_bytes} bytes")

    except OSError as e:
        print(f"Error: {e}")
    clean_data(tickerSymbol)
    return tickerSymbol + " saved"

def MakeBaseImage(tickerSymbol):
    end_date = datetime.now()

    # Date 10 years ago from the current date
    start_date = end_date - timedelta(days=10*365)
    ticker_df = yf.download(tickerSymbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    
    ticker_df.index = pd.to_datetime(ticker_df.index)
    #ticker_df["Tomorrow"] = ticker_df["Close"].shift(-1)
    #ticker_df["Target"] = (ticker_df["Tomorrow"] > ticker_df["Close"]).astype(int)
    #print(ticker_df.head())
    
    fig, ax = plt.subplots()
    ticker_df.plot.line(y='Close', use_index=True, ax=ax)
    plt.savefig('plots/' + tickerSymbol + '_base.png')
    plt.close(fig)
    #print("Cleaned data.. ready to run")
    return
