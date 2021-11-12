import pandas as pd
import xlwings as xw #to copy and write with ease

DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_CashIndex_Tick_052011-052021.csv"
#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_3_year.csv"
#DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\smallerDAX.csv"
#EXCEL_PATH = r'C:\borsa\boxanalyse\Box Analysis\StartAnalyse.xlsx'
#EXCEL_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_2018-2021_box_open_hour.xlsx"
EXCEL_PATH = r"C:\borsa\boxanalyse\Box Analysis\deneme.xlsx"
TEMPLATE_PATH = r"C:\borsa\boxanalyse\Box Analysis\Function Template.xlsx"

data_wb = xw.Book(EXCEL_PATH)
template_wb = xw.Book(TEMPLATE_PATH)

for box_size in range(5,31):
    print(f"currently {box_size}")
    template_wb.sheets['template'].range('R:AW').copy(data_wb.sheets[f'Box Size {box_size}'].range("R:AW"))
    data_wb.save()

data_wb.close()       
template_wb.close()
