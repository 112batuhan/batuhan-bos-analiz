import numpy as np
import pandas as pd
from datetime import datetime, time, timedelta, date
import os

from individual_result_analyser import get_backtest_result

def format_for_pandas(headers, data):
    
    formated_data = {}
    for header in headers:
        formated_data[header] = []
        for row in data:
            formated_data[header].append(row[header])

    return formated_data

setup = {

    "EURUSD":{
        "multiplier":1,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\EURUSD-2020_10_27-2021_10_31.csv",
        "start_hour":time(1,15,0),
        "end_hour":time(23,45,0),
        "big_number_roundness": 2,
        "extra_parse":True,
        "box_breakouts":[0.5,2.5],
        "peak_breakouts":[0.1,0.4]
    },
    "USDJPY":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USDJPY-2020_10_27-2021_10_26.csv",
        "start_hour":time(1,15,0),
        "end_hour":time(23,45,0),
        "big_number_roundness": 0,
        "extra_parse":True,
        "box_breakouts":[2.5,2,1.5],
        "peak_breakouts":[0.3,0.2]
    },
    "DAX":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\DEUIDXEUR-2020_10_27-2021_10_26.csv",
        "start_hour":time(10,0,0),
        "end_hour":time(18,30,0),
        "big_number_roundness": -2,
        "extra_parse":True,
        "box_breakouts":[1,1.5],
        "peak_breakouts":[0.1,0.2]
    },
    "DOW":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USA30IDXUSD-2020_10_27-2021_10_26.csv",
        "start_hour":time(16,30,0),
        "end_hour":time(23,00,0),
        "big_number_roundness": -2,
        "extra_parse":True,
        "box_breakouts":[0.5,1],
        "peak_breakouts":[0.3,0.2]
    }
}

for symbol, data in setup.items():

    root_folder = "C:\\borsa\\boxanalyse\\Box_Analysis\\outputs\\pivot_outputs_limited_steps_3\\"
    new_root_folder ="C:\\borsa\\boxanalyse\\Box_Analysis\\outputs\\backtest_result_only\\"
    folder_name = symbol
    
    folder_names = ["fibo", "breakout", "big_number", "random_path"]
    file_extension_names =["fibo", "breakout", "bignubmer", "random"]
    new_folder_names = ["fibo", "breakout", "big_number", "random"]

    folder_path = os.path.join(root_folder,folder_name)
    new_folder_path = os.path.join(new_root_folder,folder_name)
    os.makedirs(new_folder_path, exist_ok=True)

    symbol_results = {}
    for name in new_folder_names:
        symbol_results[name] = []

    print(symbol_results)
    
    for box_percentage in np.linspace(0.01, 0.15, num=10):
        for peak_breakout in data["peak_breakouts"]:
            for box_breakout in  data["box_breakouts"]:
                for max_step in [4,5,6]:

                    file_name = f"bp_{box_percentage:.2f}-bb_{peak_breakout:.2f}-bp_{box_breakout:.2f}-ms_{max_step}"

                    for test_folder_name, extension_name, new_folder_name in zip(folder_names, file_extension_names, new_folder_names):
                        old_path = os.path.join(folder_path, test_folder_name, f"{extension_name}--{file_name}.csv")

                        print(old_path)
                        symbol_results[new_folder_name].append(get_backtest_result(old_path))

    for key, data_list in symbol_results.items():
        headers = data_list[0].keys()

        formatted_results = format_for_pandas(headers=headers, data=data_list)
        pd.DataFrame(formatted_results).to_csv(os.path.join(new_folder_path, key) ,header=True, index=False)

