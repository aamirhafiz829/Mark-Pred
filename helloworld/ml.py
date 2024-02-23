import yfinance as yf
import datetime
import os
from sklearn.metrics import precision_score,confusion_matrix
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from simulations import simulate_trading

def analyzeRF(df,tickerSymbol):
    df,new_predictors = preprocessing(df, tickerSymbol)
    return trainRF(df, new_predictors,tickerSymbol)
def preprocessing(df,tickerSymbol):
    df.index = pd.to_datetime(df.index)
    df["Tomorrow"] = df["Close"].shift(-1)
    df["Target"] = (df["Tomorrow"] > df["Close"]).astype(int)
    #model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)
    horizons = [5,60,250]
    new_predictors = ["Volume"]
    for horizon in horizons:
        rolling_averages = df.rolling(horizon).mean()
        ratio_column = f"Close_Ratio_{horizon}"
        df[ratio_column] = df["Close"] / rolling_averages["Close"]
        trend_column = f"Trend_{horizon}"
        df[trend_column] = df.shift(1).rolling(horizon).sum()["Target"]
        
        rolling_averages = df.rolling(horizon).mean()
        vol_ratio_column = f"Volume_Ratio_{horizon}"
        df[vol_ratio_column] = df["Volume"] / rolling_averages["Volume"]
        #vol_trend_column = f"Volume_Trend_{horizon}"
        #df[vol_trend_column] = df.shift(1).rolling(horizon).sum()["Target"]
        
        new_predictors+= [ratio_column, trend_column, vol_ratio_column]
    df = df.dropna(subset=df.columns[df.columns != "Tomorrow"])
    #return df


    train = df.iloc[:-100]
    test = df.iloc[-100:]
    print("train",train.head())
    print("test",test.head())
    return df,new_predictors
def trainRF(df,new_predictors,tickerSymbol):
    model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)
    predictions = backtest(df, model, new_predictors)
    multiPredictions = multiPredictBacktest(df,model,new_predictors)
    differences = predictions["Predictions"] - predictions["Target"]
    correct = (differences == 0).sum()
    fails = (differences != 0).sum()
    results_table = {"correct": correct, "fails": fails}
    balance, transactions = simulate_trading(df, predictions,tickerSymbol)
    
    output = "Balances per share: \n"
    for i in range(len(balance)):
        output += "$ "+str(round(balance[i], 3)) + " with " + str(transactions[i]) + " transactions\n"
    
    return (confusion_matrix(predictions["Target"], predictions["Predictions"]), output)
#def cacheRFModel(model, tickerSymbol):

def predictRF(train, test, predictors, model):
    model.fit(train[predictors], train["Target"])
    preds = model.predict_proba(test[predictors])[:,1]
    preds[preds >= 0.55] = 1
    preds[preds<0.55]=0
    preds = pd.Series(preds, index=test.index, name="Predictions")
    combined = pd.concat([test["Target"], preds], axis=1)
    return combined

def multiPredictRF(train, test, predictors, model):
    model.fit(train[predictors], train["Target"])
    preds = model.predict_proba(test[predictors])[:,1]
    preds[preds >= 0.6] = 1
    preds[preds<0.4]= -1
    preds[(preds < 0.6) & (preds>=0.4)]= 0

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

def multiPredictBacktest(data, model, predictors, start=1000, step=100):
    all_predictions = []

    for i in range(start, data.shape[0], step):
        train = data.iloc[0:i].copy()
        test = data.iloc[i:(i+step)].copy()
        predictions = multiPredictRF(train, test, predictors, model)
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
