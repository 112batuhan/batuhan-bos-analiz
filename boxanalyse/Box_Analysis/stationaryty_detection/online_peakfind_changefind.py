import numpy as np
import numpy as np
from numpy.lib.function_base import append
import pandas as pd
import matplotlib.pyplot as plt 
from statsmodels.tsa.stattools import adfuller
from arch.unitroot import ZivotAndrews, DFGLS, KPSS, ADF
from arch.utility.exceptions import InfeasibleTestException

import time

from helpers import thresholding_algo

def find_changes(data):

    change_points = []

    dual_data = data[1:], data[:-1]
    for idx, (current, prev) in enumerate(zip(*dual_data)):
        if current != prev:
            change_points.append(idx)

    return change_points


def draw_that_shit(result, change_points):

    plt.figure(figsize=(7, 4))
    plt.scatter(change_points, y[change_points],color="red",s=20)
    plt.plot(np.arange(1, len(y)+1), y)
    plt.plot(np.arange(1, len(y)+1-500)+500, result["avgFilter"][500:], color="cyan", lw=2)
    plt.plot(np.arange(1, len(y)+1-500)+500, result["avgFilter"][500:] + threshold * result["stdFilter"][500:], color="green", lw=1)
    plt.plot(np.arange(1, len(y)+1-500)+500, result["avgFilter"][500:] - threshold * result["stdFilter"][500:], color="green", lw=1)
    




DATA_PATH = r"C:\borsa\boxanalyse\Box_Analysis\inputs\DAX_from_2020.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())

i = -1
indexxx = 150
check_threshhold = 10


for idx, day in df.groupby(df.datetime.dt.date):
    i += 1
    if len(day)<200 or i != indexxx:
        continue
    print(i)
    print(idx)

    lag = 500
    check_count = 0
    change_points = []

    for i in range(lag, len(day), 10):

        data_part = day.iloc[i-lag:i]
        prices = data_part["Price"].to_numpy()
        dates = (data_part["datetime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')  
        dates = dates.to_numpy()

        '''
        if len(slope_calculating_prices) > 10:

            m, b = np.polyfit(slope_calculating_dates, slope_calculating_prices, 1)
            if np.abs(m) > np.abs(np.average(slope_calculating_prices) / 1000):
                slope_points.append(i)
        '''

        ZA_result = ZivotAndrews(prices)
        ADF_result = ADF(prices)
        KPSS_result = KPSS(prices)
        DFGLS_result = DFGLS(prices)
        try:
            if KPSS_result.pvalue > 0.01:
                check_count += 1
            else:
                check_count -= 1
            if DFGLS_result.pvalue <0.01:
                check_count += 1
            if ZA_result.pvalue > 0.9:
                check_count -= 2
            if ADF_result.pvalue > 0.9:
                check_count -= 2
            if check_count > check_threshhold + 5:
                check_count = check_threshhold + 5
            elif check_count < 0:
                check_count = 0
            
        except InfeasibleTestException:
            pass
            
        if  check_count > check_threshhold:
            change_points += list(range(i-lag, i))


        #KPSS>0.01 ZA<0.9
    
        print(f"ZA:{ZA_result.pvalue}, ADF:{ADF_result.pvalue}, KPSS:{KPSS_result.pvalue}, DFGLS:{DFGLS_result.pvalue}")
        plt.plot(prices)
        plt.show()
   


    '''
    lag = 245
    threshold = 3 
    influence = 0.06

    lag = int(lag)
    result = thresholding_algo(y, lag=lag, threshold=threshold, influence=influence)
    change_points = find_changes(result["signals"])

    draw_that_shit(result, change_points)
    plt.title(f"Influence: {lag}") 
        
    plt.show()
    
    
    change_points = find_changes(signal)
    '''
    data = day["Price"].to_numpy()

    change_points = np.unique(change_points).astype(int)

    #print(np.average(slopes))

    plt.plot(data)
    plt.scatter(change_points, data[change_points],color="red",s=20)
    plt.show()
    '''
    ax2.plot(signal)
    ax2.set_title("signals")
    plt.show()
    '''
