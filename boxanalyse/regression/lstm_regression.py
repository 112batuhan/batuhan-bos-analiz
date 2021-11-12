import pandas as pd
import numpy as np
import datetime as dt
from pickle import dump

import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.layers import Dense, LSTM, Input, concatenate, Flatten

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler


def r_square(y_true, y_pred):
    from tensorflow.keras import backend as K
    SS_res =  K.sum(K.square(y_true - y_pred)) 
    SS_tot = K.sum(K.square(y_true - K.mean(y_true))) 
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )


###TODO: Predivide the file and load them seperately to get consistent test data.

df = pd.read_csv(r'C:\borsa\boxanalyse\regression\box_data_with_previous_data.csv', header=0, parse_dates=[1])
df.dropna(axis=0, inplace=True)

#datetime as individual metrics (better results)
df["year"] = df["start_date"].dt.year
df["month"] = df["start_date"].dt.month
df["week"] = df["start_date"].dt.week
df["dayofmonth"] = df["start_date"].dt.day
df["hour"] = df["start_date"].dt.hour
df["minute"] = df["start_date"].dt.minute
df["dayofweek"] = df["start_date"].dt.dayofweek

y_labels = ["pip", "box_duration", "transactions"]
X_time_labels = ["year","month", "week", "dayofmonth", "hour", "minute" , "dayofweek" ,"box_size"]
X_prev_labels = [f"data_before_box_{i}" for i in range(50)]

final_test = df.sample(frac = 0.1)
final_test_y = final_test[y_labels]
final_test_X_time = final_test[X_time_labels]
final_test_X_prev = final_test[X_prev_labels]

df_test = df.drop(final_test.index).sample(frac = 0.1)
X_test_time = df_test[X_time_labels]
X_test_prev = df_test[X_prev_labels]
y_test = df_test[y_labels]

df_train = df.drop(df_test.index)
X_train_time = df[X_time_labels]
X_train_prev = df[X_prev_labels]
y_train = df[y_labels]

print(X_train_time.info())
print(X_train_prev.info())
print(y_train.info())
print(X_train_time.info())
print(X_train_prev.info())
print(y_test.info())
print(final_test_X_time.info())
print(final_test_X_prev.info())
print(final_test_y.info())

X_train_time = X_train_time.to_numpy()
X_train_prev = X_train_prev.to_numpy()
y_train = y_train.to_numpy()
X_test_time = X_test_time.to_numpy()
X_test_prev = X_test_prev.to_numpy()
y_test = y_test.to_numpy()
final_test_X_time = final_test_X_time.to_numpy()
final_test_X_prev = final_test_X_prev.to_numpy()
final_test_y = final_test_y.to_numpy()


X_time_scaler = RobustScaler()
X_time_scaler.fit(X_train_time)  #fit only on training data
X_train_time_scaled = X_time_scaler.transform(X_train_time)
X_test_time_scaled = X_time_scaler.transform(X_test_time)
X_final_test_time_scaled = X_time_scaler.transform(final_test_X_time)


X_prev_scaler = RobustScaler()
X_prev_scaler.fit(X_train_prev)  #fit only on training data
X_train_prev_scaled = X_prev_scaler.transform(X_train_prev)
X_test_prev_scaled = X_prev_scaler.transform(X_test_prev)
X_final_test_prev_scaled = X_prev_scaler.transform(final_test_X_prev)

'''
X_train_prev_scaled = np.reshape(X_train_prev_scaled, (-1, X_train_prev_scaled.shape[1], 1))
X_test_prev_scaled = np.reshape(X_test_prev_scaled, (-1, X_test_prev_scaled.shape[1], 1))
X_final_test_prev_scaled = np.reshape(X_final_test_prev_scaled, (-1, X_final_test_prev_scaled[1], 1))
'''


y_scaler = RobustScaler()
y_scaler.fit(y_train)  #fit only on training data
y_train_scaled = y_scaler.transform(y_train)
y_test_scaled = y_scaler.transform(y_test)
y_final_test_scaled = y_scaler.transform(final_test_y)

dump(X_time_scaler, open('X_time_scaler.pkl', 'wb'))
dump(X_prev_scaler, open('X_prev_scaler.pkl', 'wb'))
dump(y_scaler, open('y_scaler.pkl', 'wb'))

inputA = Input(shape=(8,))
x = Dense(50, activation="relu")(inputA)
x = keras.Model(inputs=inputA, outputs=x)

inputB = Input(shape=(50,1))
y = LSTM(50, return_sequences=False)(inputB)
y = Flatten()(y)
y = keras.Model(inputs=inputB, outputs=y)


combinedInput = concatenate([x.output, y.output])
z = Dense(100, activation="relu")(combinedInput)
z = Dense(3, activation="linear")(z)

model = keras.Model(inputs=[x.input, y.input], outputs=z)

model.compile(optimizer='adam', loss='mse', metrics=[keras.metrics.MeanSquaredLogarithmicError(),r_square])

model.fit(x=[X_train_time, X_train_prev], y=y_train, 
            validation_data=([X_test_time, X_test_prev], y_test),	
            epochs=80, batch_size=32)

model.save('model')