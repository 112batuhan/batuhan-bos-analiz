import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt 

from datetime import datetime, time, timedelta, date
from visualisation import draw_daily_plot

import sys
sys.path.append(r"C:\borsa\boxanalyse\Box_Analysis")
from box import Box
from visualisation import draw_daily_plot


def format_for_pandas(headers, data):
    
    formated_data = {}
    for header in headers:
        formated_data[header] = []
        for row in data:
            formated_data[header].append(row[header])

    return formated_data


DATA_PATH = r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USDJPY-2020_10_27-2021_10_26.csv"

print("Started reading the file.")
df = pd.read_csv(DATA_PATH, parse_dates=[0], header=0)
df = df.drop(["ask","ask_volume","bid_volume"], axis=1)
df = df.rename(columns={"bid":"Price", "time":"datetime"})
print(df.info())
df = df.iloc[::3, :]
df["Price"] *= 100 #changes, check real values.
df["datetime"] += timedelta(hours=3)
print(df)
print(df.info())


day_start_time = time(1,15,0)
day_end_time = time(23,45,0)

dummy_box = Box(5,5,datetime.now()).finish_box()
headers = dummy_box.keys()

folder_name = "usdjpyRB3"

for box_percentage in np.linspace(0.06, 0.15, num=10):

    csv_path = f"C:\\borsa\\boxanalyse\\Box_Analysis\\outputs\\random_box_outputs\\{folder_name}\\random-{box_percentage:.2f}.csv"

    #uncomment this when you want to reset the data
    new_box_df = pd.DataFrame(columns=headers).to_csv(csv_path, mode='w', header=True)

    i = -1
    for idx, day in df.groupby(df.datetime.dt.date):
        i += 1
        #if len(day)<1000 or i not in indexes_to_analyse:
        #if idx not in custom_days:
        if len(day)<1000:
            continue
        if i < 0:
            continue

        print(i, box_percentage)
        print(idx)

        daily_box_data = []
        current_box = None

        for (_ ,datetime_in_day, value) in day.itertuples():
            if datetime_in_day.time() < day_start_time or datetime_in_day.time() > day_end_time:
                continue
                
            if current_box is None:
                current_box = Box(value, value * 0.01 * box_percentage, datetime_in_day, transaction_limit=6)
            else:
                if not current_box.finished:
                    current_box.analyse_step(value, datetime_in_day)
                else:
                    finished_box_data = current_box.finish_box()
                    #draw_daily_plot(day,**finished_box_data)
                    daily_box_data.append(finished_box_data)
                    current_box = Box(value, value * 0.01 * box_percentage, datetime_in_day, transaction_limit=6)


        formatted_daily_box_data = format_for_pandas(headers, daily_box_data)

        pd.DataFrame(formatted_daily_box_data).to_csv(csv_path, mode='a', header=False)

    