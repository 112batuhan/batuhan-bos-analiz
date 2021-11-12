from datetime import datetime
import numpy as np
from numpy.lib.function_base import median
import pandas as pd
import xlwings as xw
import ruptures as rpt
import matplotlib.pyplot as plt 
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

from box import Box
from visualisation import draw_daily_plot

DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\inputs\DAX_from_2020.csv"


print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser,nrows=500000)
print(df)
print(df.info())
print("Started analysing.")


total_derivatives = np.zeros(9*3600)

segment_data = []
box_data = []

for idx, day in df.groupby(df.datetime.dt.date):
    print(idx)
    if len(day)<200:
        continue
    
    points = day["Price"].to_numpy()
    date = (day["datetime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')  
    date = date.to_numpy()
    
    #setting up a gaussian derivative filter
    smooth_width = 300
    x1 = np.linspace(-3,3,smooth_width)
    y1 = (-2 * x1)/smooth_width * np.exp((-x1**2))
    #getting smoothed derivative with filter
    points_deriv = np.convolve(points, y1, mode="same")
    
    weighted_points_deriv = points_deriv / np.average(points)

    total_derivatives[:len(weighted_points_deriv)-smooth_width] += np.abs(weighted_points_deriv)[smooth_width//2:-smooth_width//2]

plt.plot(total_derivatives)
plt.show()