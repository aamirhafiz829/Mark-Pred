import yfinance as yf
import datetime
import os
from sklearn.metrics import precision_score,confusion_matrix
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from simulations import simulate_trading
def analyzeRF(df,tickerSymbol):
    df.index = pd.to_datetime(df.index)
    df["Tomorrow"] = df["Close"].shift(-1)
    df["Target"] = (df["Tomorrow"] > df["Close"]).astype(int)
    model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)
    train = df.iloc[:-100]
    test = df.iloc[-100:]
    
    predictors = ["Close", "Volume", "Open", "High", "Low"]
    predictions = backtest(df, model, predictors)
    differences = predictions["Predictions"] - predictions["Target"]
    correct = (differences == 0).sum()
    fails = (differences != 0).sum()
    results_table = {"correct": correct, "fails": fails}
    balance, buy_sell_log = simulate_trading(df, predictions,tickerSymbol)
    return (confusion_matrix(predictions["Target"], predictions["Predictions"]), round(balance,3))


def analyzeRFLegacy(df):
    
    df.index = pd.to_datetime(df.index)
    df["Tomorrow"] = df["Close"].shift(-1)
    df["Target"] = (df["Tomorrow"] > df["Close"]).astype(int)
    model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)
    train = df.iloc[:-100]
    test = df.iloc[-100:]
    print("train", train.head())
    print("test",test.head())
    predictors = ["Close", "Volume", "Open", "High", "Low"]
    #model.fit(train[predictors], train["Target"])
    #preds = model.predict(test[predictors])
    #preds = pd.Series(presudo systemctl restart helloworldds, index=test.index)
    predictions = backtest(df, model, predictors)
    return (predictions["Predictions"].value_counts(),precision_score(predictions["Target"],predictions["Predictions"]))
    
def predictRF(train, test, predictors, model):
    model.fit(train[predictors], train["Target"])
    preds = model.predict(test[predictors])
    preds = pd.Series(preds, index=test.index, name="Predictions")
    combined = pd.concat([test["Target"], preds], axis=1)
    return combined

def backtest(data, model, predictors, start=1000, step=100):
    all_predictions = []

    for i in range(start, data.shape[0], step):
        train = data.iloc[0:i].copy()
        test = data.iloc[i:(i+step)].copy()
        predictions = predictRF(train, test, predictors, model)
        all_predictions.append(predictions)

    return pd.concat(all_predictions)


#this is a legacy function
def stock(tickerSymbol):
    startDate = datetime.datetime.now() - datetime.timedelta(days=10*365)
    endDate = datetime.datetime.now()

    # Fetch the historical data
    tickerData = yf.Ticker(tickerSymbol)
    tickerDf = tickerData.history(period='1d', start=startDate, end=endDate)

    # Save the data to a CSV file
    path_csv = 'data/' + tickerSymbol + '_10_years.csv'
    tickerDf.to_csv(path_csv)
    try:
        # Get the size of the file in bytes
        size_bytes = os.path.getsize(path_csv)
        
        # Print the size in a readable format (e.g., in KB, MB, etc.)
        print(f"Size of '{path_csv}': {size_bytes} bytes")
    except OSError as e:
        print(f"Error: {e}")
    
    return tickerSymbol + " saved: " + str(size_bytes) + " bytes"
