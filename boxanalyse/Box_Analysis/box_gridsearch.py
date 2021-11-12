import pandas as pd
import numpy as np
import random
from datetime import timedelta, time, datetime

from box import Box


def format_for_pandas(headers, data):
    
    formated_data = {}
    for header in headers:
        formated_data[header] = []
        for row in data:
            formated_data[header].append(row[header])

    return formated_data


setup = {

    "NASDAQ":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USATECHIDXUSD-2020_10_27-2021_10_26.csv",
        "start_hour":time(16,30,0),
        "end_hour":time(23,0,0)
    }

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

    day_start_time = data["start_hour"]
    day_end_time = data["end_hour"]

    dummy_box = Box(5,5,datetime.now()).finish_box()
    headers = dummy_box.keys()

    complete_data = []

    day_generator = df.groupby(df.datetime.dt.date)
    random.seed(10)
    indexes_to_analyse = random.sample(range(len(day_generator)),75)

    for box_percentage in np.linspace(0.01, 0.15, num=10):
        for peak_breakout in np.linspace(0.05, 0.5, num=7):
            for box_breakout in  np.linspace(0.1, 3, num=20):
                
                print(f"box percentage: {box_percentage:.2f}, peak breakout: {peak_breakout:.2f}, box breakout: {box_breakout:.2f}")
                
                #box_data = []
                score = 0
                box_seconds = []
                transaction_counts = []

                i = -1
                for idx, day in day_generator:
                    i += 1
                    #if len(day)<1000 or i not in indexes_to_analyse:
                    #if idx not in custom_days:
                    if len(day)<1000:
                        continue
                    if i < 0:
                        continue
                    if i not in indexes_to_analyse:
                        continue
                    
                    current_box = None

                    for (_ ,datetime_in_day, value) in day.itertuples():
                        if datetime_in_day.time() < day_start_time or datetime_in_day.time() > day_end_time:
                            continue
                            
                        if current_box is None:
                            current_box = Box(value, value * 0.01 * box_percentage, datetime_in_day, box_breakout=box_breakout, peak_breakout=peak_breakout, transaction_limit=6)
                        else:
                            if not current_box.finished:
                                current_box.analyse_step(value, datetime_in_day)
                            else:
                                finished_box_data = current_box.finish_box()
                                score += finished_box_data["real_profit_percentage"]
                                box_seconds.append(finished_box_data["box_duration_seconds"])
                                transaction_counts.append(finished_box_data["transactions"])
                                #draw_daily_plot(day,**finished_box_data)
                                #box_data.append(finished_box_data)
                                current_box = Box(value, value * 0.01 * box_percentage, datetime_in_day, box_breakout=box_breakout, peak_breakout=peak_breakout, transaction_limit=6)
                    if current_box is not None:
                        finished_box_data = current_box.finish_box()
                        if finished_box_data["real_profit_percentage"] is not None:
                            score += finished_box_data["real_profit_percentage"]
                            box_seconds.append(finished_box_data["box_duration_seconds"])
                            transaction_counts.append(finished_box_data["transactions"])
                        #box_data.append(finished_box_data)

                #formatted_box_data = format_for_pandas(headers, box_data)
                #box_df = pd.DataFrame(formatted_box_data)
                
                complete_data.append([box_percentage,box_breakout,peak_breakout,score, np.mean(box_seconds), np.mean(transaction_counts), len(transaction_counts)])
                print(complete_data[-1])

            pd.DataFrame(complete_data).to_csv(f"outputs\\box_grid_search\\gridsearch_{symbol}.csv")