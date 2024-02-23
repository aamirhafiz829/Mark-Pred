import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Parameters 
n = 3 
tickers = ['AAPL', 'TSLA', 'AMZN']

# finwiz_url = 'https://finviz.com/quote.ashx?t='
news_tables = {}

# for ticker in tickers:
# url = finwiz_url + ticker
url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=demo'
req = Request(url=url) 
resp = urlopen(req)    
html = BeautifulSoup(resp, features="lxml")
news_table = html.find(id='news-table')
news_tables['AAPL'] = news_table

try:
    # for ticker in tickers:
    df = news_tables['AAPL']
    df_tr = df.findAll('tr')
    
    print ('\n')
    print ('Recent News Headlines for {}: '.format('AAPL'))
    
    for i, table_row in enumerate(df_tr):
        a_text = table_row.a.text
        td_text = table_row.td.text
        td_text = td_text.strip()
        print(a_text,'(',td_text,')')
        if i == n-1:
            break
except KeyError:
    pass