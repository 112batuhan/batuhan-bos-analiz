individual_dates = True
neural_network_training = True

import pickle
import pandas as pd
import numpy as np
import datetime as dt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

if neural_network_training:
    from sklearn.neural_network import MLPRegressor

else:
    from sklearn.multioutput import MultiOutputRegressor
    from sklearn.linear_model import SGDRegressor
    from sklearn.metrics import mean_squared_error, r2_score



EXCEL_PATH = r"C:\borsa\boxanalyse\regression\data_for_SGD.xlsx"

print("Started reading")

columns_to_read = ["start_date", "box_median", "box_duration_excel", "transactions", "pip", "box_size"]
df = pd.read_excel(EXCEL_PATH, sheet_name="DATA",  usecols=columns_to_read)
df.dropna(axis=0, inplace=True)

if individual_dates:
    #datetime as individual metrics (slightly better results)
    df["year"] = df["start_date"].dt.year
    df["month"] = df["start_date"].dt.month
    df["week"] = df["start_date"].dt.week
    df["dayofmonth"] = df["start_date"].dt.day
    df["hour"] = df["start_date"].dt.hour
    df["minute"] = df["start_date"].dt.minute
    df["dayofweek"] = df["start_date"].dt.dayofweek
    X = df[["year", "month", "week", "dayofmonth", "hour", "minute" , "dayofweek", "box_median", "box_size"]]

else:
    df['start_date'] = (df["start_date"] - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1) 
    X = df[["start_date", "box_median", "box_size"]].to_numpy() 

print(df)
print(df.info())

y = df[["pip", "box_duration_excel", "transactions"]].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)
print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)

X_scaler = StandardScaler()
X_scaler.fit(X_train)  #fit only on training data
X_train_scaled = X_scaler.transform(X_train)
X_test_scaled = X_scaler.transform(X_test)

if neural_network_training:

    y_scaler = StandardScaler()
    y_scaler.fit(y_train)  #fit only on training data
    y_train_scaled = y_scaler.transform(y_train)
    y_test_scaled = y_scaler.transform(y_test)

    regr = MLPRegressor((3, 1000), random_state=1, max_iter=1000, verbose=True, early_stopping=True).fit(X_train_scaled, y_train_scaled)
    score = regr.score(X_test_scaled, y_test_scaled)
    y_pred = regr.predict(X_test_scaled)
    print(score)

    print(y_pred[30:])
    print(y_test_scaled[30:])

else:

    #Linear SGD regression (didn't work well, r2 0.16, MSE 130)

    sgd = SGDRegressor( max_iter=1000, alpha=0.0001)
    model = MultiOutputRegressor(sgd).fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    print(y_pred[30:])
    print(y_test[30:])

    MSE = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"MSE: {MSE}, r2: {r2}")

    filename = 'finalized_model.sav'
    pickle.dump(model, open(filename, 'wb'))


    '''

    loaded_model = pickle.load(open(filename, 'rb'))
    result = loaded_model.score(X_test_scaled, y_test)
    print(result)
    '''