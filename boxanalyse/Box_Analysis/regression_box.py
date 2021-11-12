import pandas as pd
import numpy as np

from box import Box
from visualisation import draw_daily_plot

def format_for_pandas(headers, data):
    
    formated_data = {}
    for header in headers:
        formated_data[header] = []
        for row in data:
            formated_data[header].append(row[header])

    return formated_data


#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_CashIndex_Tick_052011-052021.csv"
DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_3_year.csv"
#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\smallerDAX.csv"
OUTPUT_PATH = r"C:\borsa\boxanalyse\Box Analysis\box_data_for_regression.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())

'''
header_list = ["start_date",  "box_duration", "transactions", "pip","profit","pip_percentage","profit_percentage", "box_percentage", "box_size"] + [f"data_before_box_{i}" for i in range(50)]
formated_data = format_for_pandas(header_list, [])
analysis_df = pd.DataFrame(formated_data)
analysis_df["box_size"] = []
analysis_df.to_csv(OUTPUT_PATH, mode='w', header=True)
'''

for box_size in range(5,31):
    print(f"Analysing for box size {box_size}")
    result_data = []
    data_before_box = []

    for idx, day in df.groupby(df.datetime.dt.date):
        time_to_pass = day.iloc[0]["datetime"] + pd.DateOffset(minutes=1)
        box_list = []

        index = 0
        for (i ,date, value) in day.itertuples():

            if date >= time_to_pass:
                data_before_box.append(day.iloc[index-49:index+1]["Price"].to_numpy())
                new_box = Box(value, box_size, date, 1.5, 0.2, 1, 0.05)
                box_list.append(new_box)
                time_to_pass += pd.DateOffset(minutes=5)
            
            index +=1

            for box in box_list:
                if not box.finished:
                    box.analyse_step(value, date) 

        for box in box_list:
            box_result = box.finish_box()
            result_data.append(box_result)
            #draw_daily_plot(day ,**box_result) 

        print(f"finished looping the day {idx}. Box Size {box_size}")
        
    print(f"Finished analysing, outputting the excel file")

    data_before_box = np.stack( data_before_box, axis=0 )
    data_before_box_columns = [f"data_before_box_{i}" for i in range(50)]
    data_before_box_pd = pd.DataFrame(data_before_box, columns=data_before_box_columns)

    header_list = ["start_date",  "box_duration", "transactions", "pip","profit","pip_percentage","profit_percentage", "box_percentage"]
    formated_data = format_for_pandas(header_list, result_data)
    analysis_df = pd.DataFrame(formated_data)
    analysis_df["box_size"] = [box_size] * len(result_data)
    
    dataset_df = pd.concat([analysis_df, data_before_box_pd],axis=1)
    print(dataset_df.info())
    dataset_df.to_csv(OUTPUT_PATH, mode='a', header=False)