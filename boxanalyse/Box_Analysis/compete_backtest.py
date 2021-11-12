import numpy as np
import pandas as pd
import pickle as pkl
from datetime import datetime, time, timedelta, date
import os

import sys
sys.path.append(r"C:\borsa\boxanalyse\Box_Analysis")
from box import Box
from backtest_classes import RandomBox, DayStartBreakout, FiboPivot, BigNumber, format_for_pandas

setup = {

    "GBPJPY":{
        "multiplier":1,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\GBPJPY-2020_8_11-2021_8_11.csv",
        "start_hour":time(1,15,0),
        "end_hour":time(23,45,0),
        "big_number_roundness": 0,
        "box_breakouts":[1],
        "peak_breakouts":[1],
        "extra_parse":False
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
    df["datetime"] += timedelta(hours=3)
    print(df)
    print(df.info())

    breakout_start_time = (datetime.combine(date(1,1,1),data["start_hour"]) + timedelta(minutes=15)).time()
    breakout_end_time = (datetime.combine(date(1,1,1),data["start_hour"]) + timedelta(minutes=30)).time()

    dummy_box = Box(5,5,datetime.now()).finish_box()
    headers = dummy_box.keys()

    root_folder = "C:\\borsa\\boxanalyse\\Box_Analysis\\outputs\\pivot_outputs_limited_steps_3\\"
    folder_name = symbol

    for box_percentage in np.linspace(0.01, 0.15, num=10):
        for peak_breakout in data["peak_breakouts"]:
            for box_breakout in  data["box_breakouts"]:
                for max_step in [6]:
                    
                    folder_path = os.path.join(root_folder,folder_name, f"max_step_{max_step}")
                    os.makedirs(folder_path, exist_ok=True)

                    file_name = f"bp_{box_percentage:.3f}-pb_{peak_breakout:.3f}-bb_{box_breakout:.3f}-ms_{max_step}"
                    #############
                    #
                    # Fix and double check paths before executing again!
                    #
                    ############
                    folder_names = ["fibo", "breakout", "big_number", "random_path"]
                    for test_folder_name in folder_names:
                        os.makedirs(os.path.join(folder_path, test_folder_name), exist_ok=True)

                    fibo_path = os.path.join(folder_path, "fibo", f"fibo--{file_name}.csv")
                    breakout_path = os.path.join(folder_path, "breakout", f"breakout--{file_name}.csv")
                    big_number_path = os.path.join(folder_path, "big_number", f"bignubmer--{file_name}.csv")
                    random_path = os.path.join(folder_path, "random_path", f"random--{file_name}.csv")


                    dummy_box = Box(5,5,datetime.now()).finish_box()
                    headers = dummy_box.keys()

                    #uncomment this when you want to reset the data
                    pd.DataFrame(columns=headers).to_csv(fibo_path, mode='w', header=True)
                    pd.DataFrame(columns=headers).to_csv(breakout_path, mode='w', header=True)
                    pd.DataFrame(columns=headers).to_csv(big_number_path, mode='w', header=True)
                    pd.DataFrame(columns=headers).to_csv(random_path, mode='w', header=True)


                    fibo_data = []
                    breakout_data = []
                    big_number_data = []
                    random_data = []


                    previous_day_max = None
                    previous_day_min = None
                    previous_day_close = None

                    i = -1
                    for idx, day in df.groupby(df.datetime.dt.date):
                        i += 1
                        #if len(day)<1000 or i not in indexes_to_analyse:
                        #if idx not in custom_days:
                        if len(day)<1000:
                            continue
                        if i < 0:
                            continue

                        print(f"{i} {idx} {symbol} --- box percentage: {box_percentage:.2f}, peak breakout: {peak_breakout:.2f}, box breakout: {box_breakout:.2f}, max step: {max_step}")
                        #reduce copy pastes by moving iteration code to their respective class and implementing a sort of loop

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

                    pd.DataFrame(format_for_pandas(headers, fibo_data)).to_csv(fibo_path, mode='w', header=True)
                    pd.DataFrame(format_for_pandas(headers, breakout_data)).to_csv(breakout_path, mode='w', header=True)
                    pd.DataFrame(format_for_pandas(headers, big_number_data)).to_csv(big_number_path, mode='w', header=True)
                    pd.DataFrame(format_for_pandas(headers, random_data)).to_csv(random_path, mode='w', header=True)
                