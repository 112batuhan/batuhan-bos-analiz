import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt 
from arch.unitroot import ZivotAndrews, DFGLS, KPSS, ADF, PhillipsPerron
from arch.utility.exceptions import InfeasibleTestException
from tensorflow import keras
from datetime import datetime
import random

import sys
sys.path.append(r"C:\borsa\boxanalyse\Box_Analysis")
from box import Box
from helpers import format_for_pandas

DATA_PATH = r"C:\borsa\boxanalyse\Box_Analysis\inputs\DAX_from_2020.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())


percent_path = r"C:\borsa\boxanalyse\Box_Analysis\outputs\stationarity_backtest_percent.csv"
new_box_strategy_path = r"C:\borsa\boxanalyse\Box_Analysis\outputs\stationarity_new_box_strategy.csv"
old_box_strategy_path = r"C:\borsa\boxanalyse\Box_Analysis\outputs\stationarity_old_box_strategy.csv"

dummy_box = Box(5,5,datetime.now()).finish_box()
headers = dummy_box.keys()

#uncomment this when you want to reset the data
#new_box_df = pd.DataFrame(columns=headers).to_csv(new_box_strategy_path, mode='w', header=True)
#old_box_df = pd.DataFrame(columns=headers).to_csv(old_box_strategy_path, mode='w', header=True)


with open(r"C:\borsa\boxanalyse\Box_Analysis\stationaryty_detection\models\400_epoch_100x3_dropout_CV\X_scaler.pickle", "rb") as f:
    X_scaler = pkl.load(f)

model = keras.models.load_model(r"C:\borsa\boxanalyse\Box_Analysis\stationaryty_detection\models\400_epoch_100x3_dropout_CV\model.h5")

indexes_to_analyse = random.sample(range(len(df.groupby(df.datetime.dt.date))), 26)

i = -1
for idx, day in df.groupby(df.datetime.dt.date):
    i += 1
    if len(day)<1000 or i not in indexes_to_analyse:
        continue
    print(i)
    print(idx)

    lag = 400
    change_points = []
    sliding_window = []
    new_box = None
    percent_list = []
    new_box_strategy_data = []
    last_index = 0

    old_box = None
    old_box_strategy_data = []

    for index_in_day in range(lag, len(day), 5):

        data_part = day.iloc[index_in_day - lag : index_in_day]
        prices = data_part["Price"].to_numpy()

        results = [ZivotAndrews(prices), ADF(prices), KPSS(prices), DFGLS(prices), PhillipsPerron(prices)]
        
        features = [np.std(prices)/np.mean(prices)]

        try: #sometimes pvalue calculation throws InfeasibleTestException for statistic number being outside of p table range
            features += ([result.pvalue for result in results] + [result.stat for result in results])
            test = True #error correction 
        except InfeasibleTestException:
            test = False #error correction
            
        if test: #error correction
            scaled_features = X_scaler.transform([features])
            result = model.predict(scaled_features)

            if result[0][0] > 0.95:
                sliding_window.append(1)
                if np.sum(sliding_window) > 5 and index_in_day - lag > last_index:
                    ###---new stationarity detected---###

                    if new_box is not None:
                        if not new_box.finished:
                            current_mean = np.mean(prices)
                            if box_mean > current_mean:
                                percent = (new_box.lower_limit - current_mean) / prices[-1] * 100
                            else:
                                percent = (current_mean - new_box.upper_limit) / prices[-1] * 100

                            percent_list.append(percent)

                        new_box_strategy_data.append(new_box.finish_box())

                    box_mean = np.mean(prices)
                    box_max = np.max(prices) + 1
                    box_min = np.min(prices) - 1
                    box_size = box_max - box_min
                    box_start_date = data_part.iloc[-1]["datetime"]

                    new_box = Box(box_mean, box_size, box_start_date, custom_start_value=prices[-1], custom_limits=(box_min, box_max))

                    if old_box is None:
                        old_box = Box(box_mean, box_size, box_start_date, custom_start_value=prices[-1], custom_limits=(box_min, box_max))
                    if old_box is not None and old_box.finished:
                        old_box_strategy_data.append(old_box.finish_box())
                        old_box = Box(box_mean, box_size, box_start_date, custom_start_value=prices[-1], custom_limits=(box_min, box_max))

                    ###---/new stationarity detected---###
                    last_index = index_in_day
                    sliding_window = []
            else:
                sliding_window.append(0)

            if len(sliding_window) > 15:
                sliding_window.pop(0)

        current_data = data_part.iloc[-1]
        if new_box is not None and not new_box.finished:
            new_box.analyse_step(current_data["Price"], current_data["datetime"])
        if old_box is not None and not old_box.finished:
            old_box.analyse_step(current_data["Price"], current_data["datetime"])

    print(new_box_strategy_data)

    formatted_new_box_data = format_for_pandas(headers, new_box_strategy_data)
    formatted_old_box_data = format_for_pandas(headers, old_box_strategy_data)

    pd.DataFrame(formatted_new_box_data).to_csv(new_box_strategy_path, mode='a', header=False)
    pd.DataFrame(formatted_old_box_data).to_csv(old_box_strategy_path, mode='a', header=False)
    pd.DataFrame(percent_list).to_csv(percent_path, mode='a', header=False)