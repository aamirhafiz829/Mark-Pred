from flask import Flask, jsonify, render_template, request, send_file
import logging
from datetime import datetime, timedelta
import yfinance as yf
from ml import analyzeRF
from clean import obtain_stock, MakeBaseImage,MakeTradingHistoryImage 
import pandas as pd
from simulations import simulate_trading

app = Flask(__name__)
print("1/25... startup")
@app.route('/')
def index():
    return render_template('index.html')
    
if not app.debug:
    file_handler = logging.FileHandler('terminal_output.log')
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

@app.route('/name/<name>/',methods=["GET"])
def show_name(name):
    return name + '!'

@app.route('/stock/<ticker>/',methods = ["GET"])
def obtain_stock_handler(ticker):
    if exists(ticker): 
        MakeBaseImage(ticker)
        return render_template('ticker_dashboard.html',ticker=ticker)
    return ("No ticker exists: ", tickerSymbol)
    
@app.route('/base/<ticker>/',methods = ["GET"])
def view_base(ticker):
    return send_file('plots/' + ticker + '_base.png', mimetype='image/png')

@app.route('/analyze/<tickerSymbol>/',methods = ["GET"])
def analyze_handler(tickerSymbol):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365)
    df = yf.download(tickerSymbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d')) 
    confusion_matrix, output = analyzeRF(df,tickerSymbol)
    cm_df = pd.DataFrame(confusion_matrix, columns=['Predicted Decrease', 'Predicted Increase'], index=['Actual Decrease', 'Actual Increase'])
    # Convert the DataFrame to HTML
    cm_html = cm_df.to_html(classes='table table-striped', index=True, border=0)
    MakeTradingHistoryImage(tickerSymbol)
    return render_template('analysis.html', cm_table=cm_html, trading_output=output, ticker=tickerSymbol)

def exists(tickerSymbol):
    end_date = datetime.now()
    # Date 10 years ago from the current date
    start_date = end_date - timedelta(days=5*365)
    data = yf.download(tickerSymbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    if data.empty:
        return False
    print(data.head())
    return True

if __name__ == "__main__":
	app.run()
