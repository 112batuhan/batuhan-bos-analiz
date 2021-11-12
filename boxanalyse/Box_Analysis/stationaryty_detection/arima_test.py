import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import adfuller,kpss
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA

from pmdarima.arima import auto_arima
import statsmodels.graphics.tsaplots as tsaplot



from statsmodels.tsa.holtwinters import Holt, ExponentialSmoothing, SimpleExpSmoothing



DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\inputs\DAX_from_2020.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
df.fillna(method="bfill", inplace=True)
print(df)
print(df.info())

i = -1
indexxx = 150

for idx, day in df.groupby(df.datetime.dt.date):
    i += 1
    if len(day)<200 or i != indexxx:
        continue
    print(i)
    print(idx)

    lag = 500
    test_length = 50

    data = day["Price"].to_numpy()
    
    plt.figure(figsize=(12,5), dpi=100)
    plt.plot(data)
    
    change_points = []
    slopes = []

    for i in range(lag, len(day)-test_length,10):

        date_part = day["Price"]
        prices, prices_test = date_part[i-lag:i], date_part[i:i+test_length]



        '''
        arima_model = auto_arima(prices,
                            start_p=1, start_q=1,
                            max_p=5, max_q=5,
                            test='adf',        
                            trace=False,
                            alpha=0.05,
                            scoring='mse',
                            suppress_warnings=True,
                            seasonal = False
                            )
        '''

        try:

            fitted_model = arima_model.fit(prices) 


            forecast_values = fitted_model.predict(test_length, alpha=0.05) 
            #print(forecast_values)
            fcv_series = pd.Series(forecast_values, index=prices_test.index)
        except ValueError:
            print("problem idk why")   
           
        
        m, b = np.polyfit(list(range(test_length)), forecast_values, 1)
        #print(m)
        if np.abs(m) < 0.03: #np.abs(np.average(forecast_values) / 6500):
            change_points.append(i)
        slopes.append(m)

        '''
        plt.figure(figsize=(12,5), dpi=100)
        plt.plot(prices, label='training')
        plt.plot(prices_test, label='Actual Stock Price')
        plt.plot(fcv_series,label='Predicted Stock Price')
        plt.title('Stock Price Prediction')
        plt.xlabel('Time')
        plt.ylabel('price')
        plt.legend(loc='upper left', fontsize=8)
        plt.show()
        '''
        
    print(np.average(slopes))
    plt.figure(figsize=(12,5), dpi=100)
    plt.plot(data)
    plt.scatter(change_points, data[change_points],color="red",s=20)
    plt.show()