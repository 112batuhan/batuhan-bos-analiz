import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt 

from statsmodels.graphics import tsaplots
from statsmodels.tsa.stattools import adfuller

DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\inputs\DAX_from_2020.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser,nrows=500000)
print(df)
print(df.info())

with open(r"Box Analysis\peak_find_datas\offline_data_all.pickle", "rb") as f:
    offline_data_all = pickle.load(f)

with open(r"Box Analysis\peak_find_datas\offline_data.pickle", "rb") as f:
    offline_data_stationary = pickle.load(f)

for idx, day in df.groupby(df.datetime.dt.date):

    if len(day)<200:
       continue
   
    print(idx)

    
    plt.plot(day["Price"])
    plt.show()

    start = 21690
    end = 23332

    lag = 450

    start = 10250
    end = 11250

    for i in range(start + lag, end+1000, 50):
        print(i-start)

        data_part = day.iloc[i-lag:i]["Price"]

        result = adfuller(data_part)
        print('ADF Statistic: %f' % result[0])
        print('p-value: %f' % result[1])
        print('Critical Values:')
        for key, value in result[4].items():
            print('\t%s: %.3f' % (key, value))


        fig, ax = plt.subplots()
        plt.plot(data_part)
        fig = tsaplots.plot_acf(data_part, lags=lag-10)
        plt.show()

                
        



    '''

    breakpoints_all = offline_data_all[idx]
    breakpoints_stationary = offline_data_stationary[idx]

    offsets = [0] + breakpoints_all[:-1], breakpoints_all

    for current, next in zip(*offsets):

        if current in breakpoints_stationary and next in breakpoints_stationary:
            print("this is stationary")

        data_part = day.iloc[current:next]
        rolled_part = data_part["Price"].rolling(20).mean().dropna()

        fig, ax = plt.subplots()
        plt.plot(data_part["Price"])
        plt.plot(rolled_part)

        fig = tsaplots.plot_acf(rolled_part, lags=470)
        plt.show()

    '''