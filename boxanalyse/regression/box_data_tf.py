import pandas as pd
import numpy as np
import datetime as dt
from pickle import dump

from tensorflow import keras
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def r_square(y_true, y_pred):
    from tensorflow.keras import backend as K
    SS_res =  K.sum(K.square(y_true - y_pred)) 
    SS_tot = K.sum(K.square(y_true - K.mean(y_true))) 
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )


print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

continue_train = False
individual_dates = True
EXCEL_PATH = r"C:\borsa\boxanalyse\regression\data_for_SGD.xlsx"

print("Started reading")

columns_to_read = ["start_date", "box_median", "box_duration_excel", "transactions", "pip", "box_size"]
df = pd.read_excel(EXCEL_PATH, sheet_name="DATA",  usecols=columns_to_read)
df.dropna(axis=0, inplace=True)

if individual_dates:
    #datetime as individual metrics (slightly better results)
    #df["year"] = df["start_date"].dt.year only one year in this data
    df["month"] = df["start_date"].dt.month
    df["week"] = df["start_date"].dt.week
    df["dayofmonth"] = df["start_date"].dt.day
    df["hour"] = df["start_date"].dt.hour
    df["minute"] = df["start_date"].dt.minute
    df["dayofweek"] = df["start_date"].dt.dayofweek
    X = df[["month", "week", "dayofmonth", "hour", "minute" , "dayofweek", "box_median", "box_size"]]

else:
    df['start_date'] = (df["start_date"] - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1) 
    X = df[["start_date", "box_median", "box_size"]].to_numpy() 

print(df)
print(df.info())

y = df[["pip", "box_duration_excel", "transactions"]].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)

X_scaler = StandardScaler()
X_scaler.fit(X_train)  #fit only on training data
X_train_scaled = X_scaler.transform(X_train)
X_test_scaled = X_scaler.transform(X_test)

y_scaler = StandardScaler()
y_scaler.fit(y_train)  #fit only on training data
y_train_scaled = y_scaler.transform(y_train)
y_test_scaled = y_scaler.transform(y_test)

dump(X_scaler, open('scaler_X.pkl', 'wb'))
dump(y_scaler, open('scaler_y.pkl', 'wb'))

if continue_train:
    model = keras.models.load_model("model",custom_objects={'r_square':r_square})

else:
    model = keras.Sequential()
    model.add(tf.keras.Input(shape=(X_train_scaled.shape[1],)))
    model.add(keras.layers.Dense(500, activation="relu"))
    model.add(keras.layers.Dense(500, activation="relu"))
    model.add(keras.layers.Dense(3, activation=None))

    model.compile(optimizer='adam', loss='mse', metrics=[keras.metrics.MeanSquaredLogarithmicError(),r_square])

model.fit(X_train_scaled, y_train_scaled, batch_size=32, epochs=100, shuffle=True, validation_data=(X_test_scaled, y_test_scaled))
model.save('model')
