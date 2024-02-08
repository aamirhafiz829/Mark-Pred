import yfinance as yf
import datetime
import os
from sklearn.metrics import precision_score
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
def simulate_trading(stock_df, predictions_df,tickerSymbol):
    # Join the 'Close' column from stock_df with predictions_df on the date index
    joined_df = predictions_df.join(stock_df['Close'])
    is_holding_stock = False
    balance = 0
    stocks_held = 0
    buy_sell_log = []  # To keep track of buy/sell actions
    
    for date, row in joined_df.iterrows():
        if row['Predictions'] == 1 and not is_holding_stock:  # Buy signal
            is_holding_stock = True
            stocks_held += 1  # Simulate buying one unit of stock
            balance -= row['Close']  # Subtract the cost from balance
            buy_sell_log.append(('buy', date, row['Close']))
        elif row['Predictions'] == 0 and is_holding_stock:  # Sell signal
            is_holding_stock = False
            stocks_held -= 1  # Simulate selling one unit of stock
            balance += row['Close']  # Add the sale proceeds to balance
            buy_sell_log.append(('sell', date, row['Close']))
    
    # If holding stock at the end, sell it
    if is_holding_stock:
        final_row = joined_df.iloc[-1]
        balance += final_row['Close'] * stocks_held
        buy_sell_log.append(('sell', joined_df.index[-1], final_row['Close']))
        stocks_held = 0
    
    file_path = "simulations/"+tickerSymbol + "_simulation.txt"
    with open(file_path, 'w') as file:
        for action, date, price in buy_sell_log:
            if action == 'buy': 
                buy_str = f"{date.strftime('%Y-%m-%d')} at {str(round(price,3))}"
                buy_pr = round(price,3)
            else:
                
                buy_str += f"--> {date.strftime('%Y-%m-%d')} delta: {str(round(buy_pr - price,3))} %: {str(round((price - buy_pr)/buy_pr*100,3))}"
                # print(buy_str)
                file.write(buy_str + "\n")
                # Reset buy_str for the next set of actions
                buy_str = ""
    print(f"The simulation log has been saved to: {file_path}")
    return balance, buy_sell_log
