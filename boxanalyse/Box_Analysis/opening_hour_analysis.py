from datetime import datetime
import pandas as pd
import xlwings as xw


DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_CashIndex_Tick_052011-052021.csv"
#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_3_year.csv"
#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\smallerDAX.csv"
#EXCEL_PATH = r'C:\borsa\boxanalyse\Box Analysis\StartAnalyse.xlsx'
#EXCEL_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_2018-2021_box_open_hour.xlsx"
EXCEL_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_2011_2021_first_hour_analysis.xlsx"


print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())
print("Started analysing.")
data = []
for idx, day in df.groupby(df.datetime.dt.date):

    first_date = day.iloc[0]["datetime"]
    first_value = day.iloc[0]["Price"]
    data_row = [first_date, first_value]
    for minutes in range(0, 60, 30):

        start_date = first_date + pd.DateOffset(minutes=minutes)
        end_date = first_date + pd.DateOffset(minutes=minutes+30)
        data_segment = day.loc[(day['datetime'] >= start_date) & (day['datetime'] < end_date)]
        
        max_value = data_segment["Price"].max()
        min_value = data_segment["Price"].min()
        average = data_segment["Price"].mean()
        stdeviation = data_segment["Price"].std()

        max_percent = (max_value - first_value) / first_value * 100
        min_percent = (min_value - first_value) / first_value * 100
        average_percent = (average - first_value) / first_value * 100
        total_percent_play = max_percent - min_percent



        data_row += [max_value, max_percent, min_value, min_percent, average, average_percent, stdeviation, total_percent_play]
    
    ##0-60 analizi
    end_date = first_date + pd.DateOffset(minutes=60)
    data_segment = day.loc[(day['datetime'] >= start_date) & (day['datetime'] < end_date)]
    
    max_value = data_segment["Price"].max()
    min_value = data_segment["Price"].min()
    average = data_segment["Price"].mean()
    stdeviation = data_segment["Price"].std()

    max_percent = (max_value - first_value) / first_value * 100
    min_percent = (min_value - first_value) / first_value * 100
    average_percent = (average - first_value) / first_value * 100
    total_percent_play = max_percent - min_percent

    data_row += [max_value, max_percent, min_value, min_percent, average, average_percent, stdeviation, total_percent_play]


    data.append(data_row)

print("Analysis Finished. Started writing to excel.")

headers = ["date", "start value", 
           "0-30 max", "0-30 max%","0-30 min", "0-30 min%", "0-30 avg", "0-30 avg%", "0-30 std", "0-30 play%",
           "30-60 max", "30-60 max%","30-60 min", "30-60 min%", "30-60 avg", "30-60 avg%", "30-60 std", "30-60 play%",
           "0-60 max", "0-60 max%","0-60 min", "0-60 min%", "0-60 avg", "0-60 avg%", "0-60 std", "0-60 play%"]

excel_df = pd.DataFrame(data, columns=headers)

wb = xw.Book(EXCEL_PATH)
wb.sheets["DATA"].range("A1").value = excel_df
wb.save()
wb.close()