from matplotlib.pyplot import disconnect
import numpy as np
import pandas as pd
import pickle
import random

from helpers import thresholding_algo, find_changes_from_thresholding_algo, format_for_pandas, real_time_peak_detection, thresholding_algo_only_break_points



def calculate_score(online_data, offline_data):
    score = 0

    if len(online_data) == 0:
        return 100000000000000
    elif len(offline_data) == 0:
        return 0

    online_data_index = 0
    for offline_data_point in offline_data:

        distances = []

        for online_data_point in online_data[online_data_index:]:
            if offline_data_point > online_data_point:
                online_data_index +=1
            else:
                break

        if online_data_index > 0:
            distance_to_lower_bound = np.power((online_data[online_data_index-1] - offline_data_point) / 100, 2)
            distances.append(distance_to_lower_bound)

        if online_data_index < len(online_data):
            distance_to_upper_bound = np.power((online_data[online_data_index] - offline_data_point) / 100, 2)
            distances.append(distance_to_upper_bound)
        
        score += np.min(distances)


    return score


DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\inputs\DAX_from_2020.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())
print("Started analysing.")


with open(r"Box Analysis\peak_find_datas\offline_data_all.pickle", "rb") as f:
    offline_data = pickle.load(f)

lag_range = [245]
treshold_range = [3]
influence_range = [0.06]

grid_search_results = []

random.seed(10)
indexes_to_analyse = random.sample(range(len(df.groupby(df.datetime.dt.date))), 25)


for lag in lag_range:
    lag = int(lag)
    for threshold in treshold_range:
        for influence in influence_range:
            
            total_score_for_current_parameters = 0
            i = -1
            for idx, day in df.groupby(df.datetime.dt.date):
                i += 1
                if len(day)<200 or i not in indexes_to_analyse:
                    continue


                y = day["Price"].to_numpy()
                algo_result = thresholding_algo_only_break_points(y, lag=lag, threshold=threshold, influence=influence)
                score = calculate_score(algo_result, offline_data[idx])
                print(f"--RESULTS--  day: {idx}, lag: {lag:.2f}, threshold: {threshold:.2f}, influence: {influence:.2f}, result: {score}")
                total_score_for_current_parameters += score
                print

            grid_search_results.append({"lag":lag,
                                        "treshhold":threshold,
                                        "influence":influence,
                                        "total_score":total_score_for_current_parameters
                                        })

            headers = ["lag", "treshhold", "influence", "total_score"]
            pandas_dict = format_for_pandas(headers, grid_search_results)
            result_df = pd.DataFrame(pandas_dict)
            print(result_df)
            result_df.to_csv(r"C:\borsa\boxanalyse\Box Analysis\peak_find_datas\grid_search_results.csv", mode='w', header=True)
