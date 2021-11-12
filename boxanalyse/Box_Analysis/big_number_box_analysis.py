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

##TODO: Add sheet creation if there aren't any named like that


#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_CashIndex_Tick_052011-052021.csv"
#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_3_year.csv"
DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\smallerDAX.csv"
EXCEL_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAS.xlsx"
TEMPLATE_PATH = r"C:\borsa\boxanalyse\Box Analysis\Function Template.xlsx"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())


data_wb = xw.Book(EXCEL_PATH)
template_wb = xw.Book(TEMPLATE_PATH)

for box_size in range(5,31):
    print(f"Analysing for box size {box_size}")
    result_data = []
    for idx, day in df.groupby(df.datetime.dt.date):
        
        box_active = False
        big_number_crossed = False

        last_half_hour = day.iloc[-1]["datetime"] - pd.DateOffset(minutes=30)
        first_value = day.iloc[0]["Price"]

        upper_big_numer = (first_value + 100) - (first_value % 100)
        lower_big_number = first_value - (first_value % 100)

        for (_ ,date, value) in day.itertuples():
            
            if value > upper_big_numer or value < lower_big_number:
                current_big_number = round(value,-2)
                upper_big_numer = current_big_number + 100
                lower_big_number = current_big_number - 100
                big_number_crossed = True
            
            if big_number_crossed and box_active:
                current_box.finished = True

            if box_active and current_box.finished:
                start_box_result = current_box.finish_box()
                result_data.append(start_box_result)    
                box_active = False
                if not big_number_crossed:
                    upper_big_numer = (value + 100) - (value % 100)
                    lower_big_number = value - (value % 100)

                draw_daily_plot(day ,**start_box_result) 

            if big_number_crossed and date < last_half_hour:
                #peak breakout=20 because it breaks at the other big numbers anyway
                current_box = Box(value, box_size, date, 1.5, 0.2, 1, 0.05)
                big_number_crossed = False
                box_active = True
            
            if box_active:
                current_box.analyse_step(value, date)



    print(f"Finished analysing, outputting the excel file")

    header_list = ["start_date", "box_median", "upper_limit", "lower_limit", "box_duration_excel", 
                   "direction", "lot_amount", "transactions", "peak", "peak_date","pip","profit","pip_percentage","profit_percentage", "box_percentage"]
    formated_data = format_for_pandas(header_list, result_data)

    analysis_df = pd.DataFrame(formated_data)
    try:
        data_wb.sheets.add(f'Box Size {box_size}')
    except ValueError:
        pass

    data_wb.sheets[f'Box Size {box_size}'].range("A1").value = analysis_df
    template_wb.sheets['template'].range('R:AW').copy(data_wb.sheets[f'Box Size {box_size}'].range("R:AW"))
    data_wb.save()


data_wb.close()       
template_wb.close()
