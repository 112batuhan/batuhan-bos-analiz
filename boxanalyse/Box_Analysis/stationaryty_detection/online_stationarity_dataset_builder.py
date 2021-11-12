import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt 
from arch.unitroot import ZivotAndrews, DFGLS, KPSS, ADF, PhillipsPerron
from arch.utility.exceptions import InfeasibleTestException


DATA_PATH = r"C:\borsa\boxanalyse\Box_Analysis\inputs\DAX_from_2020.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser,nrows=100000)
print(df)
print(df.info())


i = -1

stationarty_dict = {150:[[570, 1120], [9575,10864],[12255,13500],[13843,14600],[22500,23600],[24700,25100],[25500,26780],[27300,27800],[30000,30400]],
                      1:[[]]}
stationarty_dict = {1:[[100,600],[700,1300]]}


features = []
labels = []

for idx, day in df.groupby(df.datetime.dt.date):
    i += 1
    if len(day)<200 or i not in stationarty_dict.keys():
        continue
    print(i)
    print(idx)

    lag = 500

    daily_stationarty_data = stationarty_dict[i]

    for index_in_day in range(lag, len(day)-27000, 1):

        data_part = day.iloc[index_in_day - lag : index_in_day]
        prices = data_part["Price"].to_numpy()

        results = [ZivotAndrews(prices), ADF(prices), KPSS(prices), DFGLS(prices), PhillipsPerron(prices)]
        
        feature_for_window = [np.mean(prices), np.std(prices)]


        try: #sometimes pvalue calculation throws InfeasibleTestException for statistic number being outside of p table range
            feature_for_window += ([result.pvalue for result in results] + [result.stat for result in results])
            features.append(feature_for_window)
            appended = True #error correction 
        except InfeasibleTestException:
            appended = False #error correction
            
        if appended: #error correction
            label = 0
            for start, end in daily_stationarty_data: 
                if start + lag < index_in_day < end:
                    label = 1
            labels.append(label)
            

features = np.array(features)
labels = np.array(labels)

print(features)
print(labels)

dataset = {"features":features, "labels":labels}
print(dataset)