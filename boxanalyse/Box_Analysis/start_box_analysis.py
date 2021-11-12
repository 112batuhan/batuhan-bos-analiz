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


DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_CashIndex_Tick_052011-052021.csv"
#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_3_year.csv"
#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\smallerDAX.csv"
#EXCEL_PATH = r'C:\borsa\boxanalyse\Box Analysis\StartAnalyse.xlsx'
#EXCEL_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_2018-2021_box_open_hour.xlsx"
EXCEL_PATH = r"C:\borsa\boxanalyse\Box Analysis\deneme.xlsx"
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
        i=0
        start_value = day.iloc[0]["Price"]
        start_date = day.iloc[0]["datetime"]
        start_box = Box(start_value, box_size, start_date, 1.5, 0.3, 1, 0.05, 5)

        for (_ ,date, value) in day.itertuples():
            if not start_box.finished:
                start_box.analyse_step(value, date)
                i += 1
            else:
                start_box_result = start_box.finish_box()
                break

        if not start_box.finished:
            start_box_result = start_box.finish_box()
        
        result_data.append(start_box_result)
        #draw_daily_plot(day ,**start_box_result)

    print(f"Finished analysing, outputting the excel file")
    header_list = ["start_date", "box_median", "upper_limit", "lower_limit", "box_duration_excel", 
                   "direction", "lot_amount", "transactions", "peak", "peak_date","pip","profit",
                   "pip_percentage","profit_percentage", "box_percentage"]
    formated_data = format_for_pandas(header_list, result_data)

    analysis_df = pd.DataFrame(formated_data)
    try:
        data_wb.sheets.add(f'Box Size {box_size}')
    except ValueError:
        pass

    #maybe seperate analysis and formula pasting
    data_wb.sheets[f'Box Size {box_size}'].range("A1").value = analysis_df
    template_wb.sheets['template'].range('R:AW').copy(data_wb.sheets[f'Box Size {box_size}'].range("R:AW"))
    data_wb.save()

data_wb.close()       
template_wb.close()
