import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt 
from arch.unitroot import ZivotAndrews, DFGLS, KPSS, ADF, PhillipsPerron
from arch.utility.exceptions import InfeasibleTestException
from pandas.io.parsers import read_csv

folder_path = r"C:\borsa\boxanalyse\Box_Analysis\daily_csvs_for_labeling\labeled\\"

date_list = ["2020-01-03", "2020-04-07", "2020-05-15", "2020-07-14", "2020-09-03", "2020-09-29", "2020-12-02", "2021-01-05"]
lag = 400

features = []
labels = []

for date in date_list:

    print(f"Starting day {date}")
    complete_path = f"{folder_path}day_{date}-labeled.csv"
    daily_df = pd.read_csv(complete_path, header=0)

    label_lag_count = 0

    for index_in_day in range(lag, len(daily_df), 1):

        data_part = daily_df.iloc[index_in_day - lag : index_in_day]
        prices = data_part["value"].to_numpy()

        results = [ZivotAndrews(prices), ADF(prices), KPSS(prices), DFGLS(prices), PhillipsPerron(prices)]
        
        feature_for_window = [np.mean(prices), np.std(prices)]

        try: #sometimes pvalue calculation throws InfeasibleTestException for statistic number being outside of p table range
            feature_for_window += ([result.pvalue for result in results] + [result.stat for result in results])
            features.append(feature_for_window)
            appended = True #error correction 
        except InfeasibleTestException:
            appended = False #error correction

        if appended: #error correction
            label = data_part.iloc[-1]["label"]

            if label == 1:
                label_lag_count += 1
                if label_lag_count >= lag:
                    labels.append(1)
                else:
                    labels.append(0)
            else:
                label_lag_count = 0
                labels.append(0)


features = np.array(features)
labels = np.array(labels)

dataset_df = pd.DataFrame(features)
dataset_df.insert(12, 12, labels, False)

print(dataset_df)
print(dataset_df.info())

dataset_df.to_csv(r"C:\borsa\boxanalyse\Box_Analysis\stationaryty_detection\dataset.csv")