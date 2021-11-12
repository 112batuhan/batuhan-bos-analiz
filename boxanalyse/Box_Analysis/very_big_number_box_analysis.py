import pandas as pd
import xlwings as xw #to copy and write with ease
import openpyxl as op #to hide the data, not a priority

from box import Box
from visualisation import draw_daily_plot

def format_for_pandas(headers, data):
    
    formated_data = {}
    for header in headers:
        formated_data[header] = []
        for row in data:
            formated_data[header].append(row[header])

    return formated_data


DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\inputs\DAX_from_2020.csv"
EXCEL_PATH = r"C:\borsa\boxanalyse\Box Analysis\outputs\DAX_2020-2021_very_big_number_extra_long.xlsx"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())

data_wb = xw.Book(EXCEL_PATH)

for box_size in range(20, 101, 5):
    print(f"Analysing for box size {box_size}")
    result_data = []

    box_active = False
    big_number_crossed = False

    first_value = df.iloc[0]["Price"]

    upper_big_numer = (first_value + 1000) - (first_value % 1000)
    lower_big_number = first_value - (first_value % 1000)

    for (_ ,date, value) in df.itertuples():
            
        if value > upper_big_numer or value < lower_big_number:
            current_big_number = round(value,-3)
            upper_big_numer = current_big_number + 1000
            lower_big_number = current_big_number - 1000
            big_number_crossed = True
        
        if big_number_crossed and box_active:
            current_box.finished = True

        if box_active and current_box.finished:
            start_box_result = current_box.finish_box()
            result_data.append(start_box_result)    
            box_active = False
            if not big_number_crossed:
                upper_big_numer = (value + 1000) - (value % 1000)
                lower_big_number = value - (value % 1000)

            #draw_daily_plot(df ,**start_box_result) 

        if big_number_crossed:
            #peak breakout=20 because it breaks at the other big numbers anyway
            current_box = Box(value, box_size, date, 5, 0.2, 1, 0.05)
            big_number_crossed = False
            box_active = True
        
        if box_active:
            current_box.analyse_step(value, date)



    print(f"Finished analysing, outputting the excel file")

    header_list = ["start_date", "box_median", "upper_limit", "lower_limit", "box_duration_excel", 
                   "direction", "lot_amount", "transactions", "peak", "peak_date",
                   "pip","profit","pip_percentage","profit_percentage", "box_percentage", "peak_duration_excel"]
    formated_data = format_for_pandas(header_list, result_data)

    analysis_df = pd.DataFrame(formated_data)
    try:
        data_wb.sheets.add(f'Box Size {box_size}')
    except ValueError:
        pass

    data_wb.sheets[f'Box Size {box_size}'].range("A1").value = analysis_df
    data_wb.save()


data_wb.close()       

