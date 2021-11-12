import numpy as np
import pandas as pd
import pickle
import ruptures as rpt

DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\inputs\DAX_from_2020.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())
print("Started analysing.")

offline_data = {}

i = -1
indexxx = 100

for idx, day in df.groupby(df.datetime.dt.date):
    i += 1
    if len(day)<200 or i != indexxx:
        continue
    
    print(idx)

    points = day["Price"].to_numpy()

    algo = rpt.Pelt(model="l2", min_size=500, jump=10).fit(points)
    breakpoints = algo.predict(pen=1*np.log(len(points))*np.std(points)**2) 
    offline_data[idx] = breakpoints


    '''
    offsets = [0] + breakpoints[:-1], breakpoints
    offline_breaks = []

  
    for current, next in zip(*offsets):
        data_part = day.iloc[current:next]

        dates_in_segment = (data_part["datetime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')  
        dates_in_segment = dates_in_segment.to_numpy()
        prices_in_segment = data_part["Price"].to_numpy()
        
        #offset is to reduce start and end of the segments to get more accurate averages and regressions
        off = 200
        m, b = np.polyfit(dates_in_segment[off:-off], prices_in_segment[off:-off], 1)
        average = np.mean(prices_in_segment[off:-off])

        #the condition and segmentation parameters could be tweaked
        if np.abs(np.arctan(m)) < average*0.00349066/13325: #0.2 degrees in radian / baseline
            offline_breaks += [current, next]
            
    offline_breaks = np.unique(offline_breaks)
    offline_data[idx] = offline_breaks
    '''

with open(r"Box Analysis\peak_find_datas\offline_data_all.pickle", "wb") as f:
    pickle.dump(offline_data, f)

