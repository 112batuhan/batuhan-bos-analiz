import numpy as np
import pandas as pd
import pickle as pkl
from datetime import datetime, time, timedelta, date
import os

from timeit import default_timer as timer

import sys
sys.path.append(r"C:\borsa\boxanalyse\Box_Analysis")
from box import Box
from backtest_classes import RandomBox, DayStartBreakout, FiboPivot, BigNumber, StartBox, format_for_pandas
from individual_result_analyser import get_backtest_result_with_df



setup = {

    "GBPJPY":{
        "multiplier":1,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\GBPJPY-2020_8_11-2021_8_11.csv",
        "start_hour":time(1,15,0),
        "end_hour":time(23,45,0),
        "big_number_roundness": 0,
        "box_breakouts":[1],
        "peak_breakouts":[1],
        "extra_parse":False,
        "hour_shift":1
    },
}


##TODO:
#- Make a general version of backtest classes.
#- fix pathing
#- remove boxes without steps before saving
#- create a loop system


for symbol, data in setup.items():

    print("Started reading the file.")
    df = pd.read_csv(data["path"], parse_dates=[0], header=0)
    if data["extra_parse"]:
        df = df.drop(["ask","ask_volume","bid_volume"], axis=1)
        df = df.rename(columns={"bid":"Price", "time":"datetime"})
    df = df.iloc[::3, :]
    df["Price"] *= data["multiplier"]
    df["datetime"] += timedelta(hours=data["hour_shift"])
    print(df)
    print(df.info())

    box_headers = Box(5,5,datetime.now()).finish_box().keys()

    breakout_start_time = (datetime.combine(date(1,1,1),data["start_hour"]) + timedelta(minutes=15)).time()
    breakout_end_time = (datetime.combine(date(1,1,1),data["start_hour"]) + timedelta(minutes=30)).time()


    root_folder = "C:\\borsa\\boxanalyse\\Box_Analysis\\outputs\\pivot_outputs_start_analyse\\"
    folder_name = symbol

    folder_names = ["fibo", "breakout", "big_number", "random"]

    folder_path = os.path.join(root_folder,folder_name)
    os.makedirs(folder_path, exist_ok=True)

    symbol_results = {}
    for name in folder_names:
        symbol_results[name] = []

    for box_percentage in np.linspace(0.01, 0.15, num=5):
        for peak_breakout in data["peak_breakouts"]:
            for box_breakout in  data["box_breakouts"]:
                for max_step in [6]:
                    
                    loop_start = timer()
                    fibo_data = []
                    breakout_data = []
                    big_number_data = []
                    random_data = []

                    previous_day_max = None
                    previous_day_min = None
                    previous_day_close = None

                    print(f"{symbol} --- box percentage: {box_percentage:.3f}, peak breakout: {peak_breakout:.3f}, box breakout: {box_breakout:.3f}, max step: {max_step}")

                    i = -1
                    for idx, day in df.groupby(df.datetime.dt.date):
                        i += 1
                        #if len(day)<1000 or i not in indexes_to_analyse:
                        #if idx not in custom_days:
                        if len(day)<1000:
                            continue
                        if i < 0:
                            continue

                        

                        day = day.loc[(day['datetime'].dt.time >= data["start_hour"]) & (day['datetime'].dt.time <= data["end_hour"])]
                        if len(day)< 50:
                            continue
                        day_start_value = day.iloc[0]["Price"]
                        
                        breakout_price_data = day.loc[(day['datetime'].dt.time >= breakout_start_time) & (day['datetime'].dt.time <= breakout_end_time)]
                        breakout_list = [np.min(breakout_price_data["Price"]), np.max(breakout_price_data["Price"])]

                        solo_fibo_bt = FiboPivot(day_start_value, box_percentage, box_breakout, peak_breakout, max_step)
                        solo_breakout_bt = DayStartBreakout(day_start_value, box_percentage, box_breakout, peak_breakout, max_step, breakout_list)
                        solo_big_number_bt = BigNumber(day_start_value, box_percentage, box_breakout, peak_breakout, max_step, data["big_number_roundness"])
                        solo_random_bt = RandomBox(day_start_value, box_percentage, box_breakout, peak_breakout, max_step)

                        if previous_day_max is not None:
                            solo_fibo_bt.set_fibonacci_pivots(previous_day_max, previous_day_min, previous_day_close)
                        
                        for day_iteration_data in zip(*day.to_dict("list").values()):
                            
                            solo_fibo_bt.iterate_tick(day_iteration_data[1], day_iteration_data[0])
                            solo_big_number_bt.iterate_tick(day_iteration_data[1], day_iteration_data[0])
                            solo_random_bt.iterate_tick(day_iteration_data[1], day_iteration_data[0])

                            if day_iteration_data[0].time() > breakout_end_time:
                                solo_breakout_bt.iterate_tick(day_iteration_data[1], day_iteration_data[0])

                        fibo_data += solo_fibo_bt.get_results()
                        breakout_data += solo_breakout_bt.get_results()
                        big_number_data += solo_big_number_bt.get_results()
                        random_data += solo_random_bt.get_results()

                        previous_day_max = np.max(day["Price"])
                        previous_day_min = np.min(day["Price"])
                        previous_day_close = day.iloc[-1]["Price"]


                    fibo_results_df = pd.DataFrame(format_for_pandas(headers=box_headers, data=fibo_data))
                    breakout_results_df = pd.DataFrame(format_for_pandas(headers=box_headers, data=breakout_data))
                    random_results_df = pd.DataFrame(format_for_pandas(headers=box_headers, data=random_data))
                    big_number_results_df = pd.DataFrame(format_for_pandas(headers=box_headers, data=big_number_data))

                    symbol_results["fibo"].append(get_backtest_result_with_df(fibo_results_df, box_percentage, peak_breakout, box_breakout, max_step))
                    symbol_results["random"].append(get_backtest_result_with_df(random_results_df, box_percentage, peak_breakout, box_breakout, max_step))
                    symbol_results["breakout"].append(get_backtest_result_with_df(breakout_results_df, box_percentage, peak_breakout, box_breakout, max_step))
                    symbol_results["big_number"].append(get_backtest_result_with_df(big_number_results_df, box_percentage, peak_breakout, box_breakout, max_step))

                    print(f"This loop took {timer()-loop_start:.2f} seconds")

    for key, data_list in symbol_results.items():
        headers = data_list[0].keys()

        formatted_results = format_for_pandas(headers=headers, data=data_list)
        pd.DataFrame(formatted_results).to_csv(os.path.join(folder_path, key+".csv") ,header=True, index=False)    