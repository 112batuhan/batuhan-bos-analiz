import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt 
from arch.unitroot import ZivotAndrews, DFGLS, KPSS, ADF, PhillipsPerron
from arch.utility.exceptions import InfeasibleTestException
from tensorflow import keras
from datetime import datetime, time, timedelta, date
import random

import sys
sys.path.append(r"C:\borsa\boxanalyse\Box_Analysis")
from box import Box
from helpers import format_for_pandas
from visualisation import draw_daily_plot

DATA_PATH = r"C:\borsa\boxanalyse\Box_Analysis\inputs\usa30idxusd_2021-08-01_2021-08-31.csv"

print("Started reading the file.")
df = pd.read_csv(DATA_PATH, parse_dates=[0], names=["datetime","ask", "Price", "vol1", "vol2"])
df = df.drop(["ask","vol1","vol2"], axis=1)
df["Price"] *= 100 #changes, check real values.
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

#day_start_time = time(7,0,0)
#day_end_time = time(15,0,0)

#indexes_to_analyse = random.sample(range(len(df.groupby(df.datetime.dt.date))), 22)
#custom_days = [date(2020,10,20), date(2021,1,20), date(2021,3,19), date(2021,7,7)]


i = -1
for idx, day in df.groupby(df.datetime.dt.date):
    i += 1
    #if len(day)<1000 or i not in indexes_to_analyse:
    #if idx not in custom_days:
    if len(day)<1000:
        continue
    if i < 14:
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
    next_detection_time = time(0,0)

    for index_in_day in range(lag, len(day), 5):

        data_part = day.iloc[index_in_day - lag : index_in_day]
        data_part_end_time = data_part.iloc[-1]["datetime"].time()   
        #if data_part_end_time > day_end_time or data_part_end_time < day_start_time:
        #    continue
        if data_part_end_time < next_detection_time:
            continue
        #honestly so dumb not being able to add timedelta to time
        next_detection_time = (datetime.combine(date.today(), data_part_end_time) + timedelta(seconds=5)).time() 

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

                        new_box_strategy_current_box_result = new_box.finish_box()
                        new_box_strategy_data.append(new_box_strategy_current_box_result)
                        #print(new_box_strategy_current_box_result)
                        #draw_daily_plot(day, **new_box_strategy_current_box_result)
                        

                    box_mean = np.mean(prices)
                    box_max = np.max(prices) + (box_mean * 0.00007)
                    box_min = np.min(prices) - (box_mean * 0.00007)
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