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
    start_date = end_date - timedelta(days=10*365)
    ticker_df = yf.download(tickerSymbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    ticker_df.index = pd.to_datetime(ticker_df.index)
    # Calculate moving averages
    ticker_df['65-day MA'] = ticker_df['Close'].rolling(window=65).mean()
    ticker_df['130-day MA'] = ticker_df['Close'].rolling(window=130).mean()
    ticker_df['260-day MA'] = ticker_df['Close'].rolling(window=260).mean()

    # Plotting   
    fig, ax = plt.subplots()
    ticker_df.plot.line(y='Close', use_index=True, ax=ax)
    ticker_df['65-day MA'].plot.line(use_index=True, ax=ax, label='65-day (3 mo.) Moving Avg')
    ticker_df['130-day MA'].plot.line(use_index=True, ax=ax, label='130-day (6 mo.) Moving Avg')
    ticker_df['260-day MA'].plot.line(use_index=True, ax=ax, label='260-day (1 yr) Moving Avg')

    # Add legend
    plt.legend()
    plt.savefig('plots/' + tickerSymbol + '_base.png')
    plt.savefig('static/' + tickerSymbol+'_base.png')
    plt.close(fig)
    return

def MakeTradingHistoryImage(tickerSymbol):
    # Read intervals from the text file
    with open('simulations/'+tickerSymbol + '_simulation.txt', 'r') as file:
        intervals = [line.strip().split('-->') for line in file.readlines()]

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7*365)
    ticker_df = yf.download(tickerSymbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    ticker_df.index = pd.to_datetime(ticker_df.index)

    # Calculate moving averages
    ticker_df['65-day MA'] = ticker_df['Close'].rolling(window=65).mean()
    ticker_df['130-day MA'] = ticker_df['Close'].rolling(window=130).mean()
    ticker_df['260-day MA'] = ticker_df['Close'].rolling(window=260).mean()

    # Plotting
    fig, ax = plt.subplots()
    ticker_df.plot.line(y='Close', use_index=True, ax=ax)
    ticker_df['65-day MA'].plot.line(use_index=True, ax=ax, label='65-day Moving Avg')
    ticker_df['130-day MA'].plot.line(use_index=True, ax=ax, label='130-day Moving Avg')
    ticker_df['260-day MA'].plot.line(use_index=True, ax=ax, label='260-day Moving Avg')

    # Highlight intervals
    for interval in intervals:
        start, end = interval[0].split(' at ')[0], interval[1].split(' ')[1]
        delta = interval[1].split(',')[1][1:5]
        # print(start, end, delta)
        start, end = pd.to_datetime(start), pd.to_datetime(end)

        if delta[0] == '-':
            delta_color = float(delta[0:4])
            if delta_color < -5.0:
                print(delta_color)
                delta_color = 0.75
            else:
                delta_color = 0.15
            ax.axvspan(start, end, color='red', alpha=delta_color)
        elif delta[0] == '0':
            ax.axvspan(start, end, color='yellow', alpha=0.25)
        else:
            delta_color = float(delta[0:3])
            if delta_color > 5.0:
                print(delta_color)
                delta_color =  0.75
            else:
                delta_color = 0.15
            ax.axvspan(start, end, color='green', alpha=delta_color)

    # Add legend
    plt.legend()
    plt.savefig('static/'+tickerSymbol+'_trading.png')
    plt.savefig('plots/' + tickerSymbol + '_trading.png')
    plt.close(fig)
