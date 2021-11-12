import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt 
from arch.unitroot import ZivotAndrews, DFGLS, KPSS, ADF, PhillipsPerron
from arch.utility.exceptions import InfeasibleTestException
from tensorflow import keras
from datetime import datetime, time, timedelta, date
import random
import os

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


def fibonacci_pivots(daily_high, daily_low, daily_close):
    R = daily_high - daily_low
    P = (daily_high + daily_low + daily_close) / 3

    R1 = P + (R * 0.382)
    R2 = P + (R * 0.618)
    R3 = P + (R * 1.00)
    S1 = P - (R * 0.381)
    S2 = P - (R * 0.618)
    S3 = P - (R * 1.00)

    return [R1, R2, R3, S1, S2, S3]

setup = {

    "EURUSD":{
        "multiplier":1,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\EURUSD-2020_10_27-2021_10_31.csv",
        "start_hour":time(1,15,0),
        "end_hour":time(23,45,0)
    },
    "USDJPY":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USDJPY-2020_10_27-2021_10_26.csv",
        "start_hour":time(1,15,0),
        "end_hour":time(23,45,0)
    },
    "DAX":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\DEUIDXEUR-2020_10_27-2021_10_26.csv",
        "start_hour":time(10,0,0),
        "end_hour":time(18,30,0)
    },
    "DOW":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USA30IDXUSD-2020_10_27-2021_10_26.csv",
        "start_hour":time(16,30,0),
        "end_hour":time(23,00,0)
    },
    "NASDAQ":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USATECHIDXUSD-2020_10_27-2021_10_26.csv",
        "start_hour":time(16,30,0),
        "end_hour":time(23,0,0)
    },

}


for symbol, data in setup.items():


    print("Started reading the file.")
    df = pd.read_csv(data["path"], parse_dates=[0], header=0)
    df = df.drop(["ask","ask_volume","bid_volume"], axis=1)
    df = df.rename(columns={"bid":"Price", "time":"datetime"})
    print(df.info())
    df = df.iloc[::3, :]
    df["Price"] *= data["multiplier"] #changes, check real values.
    df["datetime"] += timedelta(hours=3)
    print(df)
    print(df.info())

    breakout_start_time = (datetime.combine(date(1,1,1),data["start_hour"]) + timedelta(minutes=15)).time()
    breakout_end_time = (datetime.combine(date(1,1,1),data["start_hour"]) + timedelta(minutes=30)).time()

    root_folder = "C:\\borsa\\boxanalyse\\Box_Analysis\\outputs\\pivot_outputs_limited_steps_2\\"
    folder_name = symbol

    for box_percentage in np.linspace(0.05, 0.15, num=11):

        folder_path = os.path.join(root_folder,folder_name)
        os.makedirs(folder_path,  exist_ok=True)
        fibo_path = os.path.join(folder_path, f"fibo-{box_percentage:.2f}.csv")
        breakout_path = os.path.join(folder_path, f"breakout-{box_percentage:.2f}.csv")
        dummy_box = Box(5,5,datetime.now()).finish_box()
        headers = dummy_box.keys()

        #uncomment this when you want to reset the data
        new_box_df = pd.DataFrame(columns=headers).to_csv(fibo_path, mode='w', header=True)
        old_box_df = pd.DataFrame(columns=headers).to_csv(breakout_path, mode='w', header=True)

        pivot_list = None

        i = -1
        for idx, day in df.groupby(df.datetime.dt.date):
            i += 1
            #if len(day)<1000 or i not in indexes_to_analyse:
            #if idx not in custom_days:
            if len(day)<1000:
                continue
            if i < 0:
                continue

            print(i)
            print(idx)

            try:

                day = day.loc[(day['datetime'].dt.time >= data["start_hour"]) & (day['datetime'].dt.time <= data["end_hour"])]
                daily_fibo_box_list = []
                daily_fibo_box_data = []
                first_value = day.iloc[0]["Price"]
                first_datetime = day.iloc[0]["datetime"]

                daily_breakout_box_list = []
                daily_breakout_box_data = []
                breakout_data = day.loc[(day['datetime'].dt.time >= breakout_start_time) & (day['datetime'].dt.time <= breakout_end_time)]
                print(breakout_data)
                breakout_calculation_data = breakout_data["Price"]
                breakout_list = [np.min(breakout_calculation_data), np.max(breakout_calculation_data)]
                breakout_start_value = breakout_calculation_data.iloc[-1]
                breakout_start_datetime = breakout_data.iloc[-1]["datetime"]

                breakout_created = False

            except IndexError:
                continue

            if pivot_list is not None:
                    
                for fibo_pivot in pivot_list:
                    daily_fibo_box_list.append(Box(fibo_pivot, np.mean(day["Price"]) * 0.01 * box_percentage, first_datetime, custom_start_value=first_value, transaction_limit=6))
                

                for (_ ,datetime_in_day, value) in day.itertuples():
                    fibo_box_to_delete = []
                    for box in daily_fibo_box_list:
                        if not box.finished:
                            box.analyse_step(value, datetime_in_day)
                        else:
                            daily_fibo_box_data.append(box.finish_box())
                            fibo_box_to_delete.append(box)
                    daily_fibo_box_list = [box for box in daily_fibo_box_list if box not in fibo_box_to_delete]
                        
                    if datetime_in_day.time()>breakout_end_time and not breakout_created:
                        for breakout_value in breakout_list:
                            daily_breakout_box_list.append(Box(breakout_value, np.mean(day["Price"]) * 0.01 * box_percentage, breakout_start_datetime, custom_start_value=breakout_start_value, transaction_limit=6))
                        breakout_created = True

                    if breakout_created:
                        breakout_box_to_delete = []
                        for box in daily_breakout_box_list:
                            if not box.finished:
                                box.analyse_step(value, datetime_in_day)
                            else:
                                daily_breakout_box_data.append(box.finish_box())
                                breakout_box_to_delete.append(box)
                        daily_breakout_box_list = [box for box in daily_breakout_box_list if box not in breakout_box_to_delete]

                for box in daily_fibo_box_list:
                    daily_fibo_box_data.append(box.finish_box())
                for box in daily_breakout_box_list:
                    daily_breakout_box_data.append(box.finish_box())

                formatted_daily_fibo_box_data = format_for_pandas(headers, daily_fibo_box_data)
                formatted_daily_breakout_box_data = format_for_pandas(headers, daily_breakout_box_data)

                pd.DataFrame(formatted_daily_fibo_box_data).to_csv(fibo_path, mode='a', header=False)
                pd.DataFrame(formatted_daily_breakout_box_data).to_csv(breakout_path, mode='a', header=False)

            previous_day_max = np.max(day["Price"])
            previous_day_min = np.min(day["Price"])
            previous_day_close = day.iloc[-1]["Price"]

            pivot_list = fibonacci_pivots(previous_day_max, previous_day_min, previous_day_close)
        
        