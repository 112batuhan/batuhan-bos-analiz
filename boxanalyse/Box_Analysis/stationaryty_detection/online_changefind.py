import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import changefinder

def draw_breakpoints(df, scores, break_points, regression_lines):

   scores = np.array(scores)
   break_points = np.array(break_points)

   data_points = df["Price"].to_numpy()
   dates = (df["datetime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')  
   dates = dates.to_numpy()

   f, (ax1, ax2) = plt.subplots(2, 1)
   f.subplots_adjust(hspace=0.4)
   ax1.plot(dates,data_points)
   ax1.scatter(dates[0] + break_points, data_points[break_points],color="red",s=20)
   ax1.set_title("data point")

   for regression_values, regression_dates in regression_lines:
      ax1.plot(regression_dates, regression_values)

   ax1.plot()

   ax2.plot(dates,scores)
   ax2.scatter(dates[0] + break_points, scores[break_points],color="red",s=20)
   ax2.set_title("anomaly score")
   plt.show() 

DATA_PATH = r"C:\borsa\boxanalyse\Box_Analysis\inputs\DAX_from_2020.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser,nrows=500000)
print(df)
print(df.info())


for idx, day in df.groupby(df.datetime.dt.date):

   if len(day)<200:
       continue
   
   print(idx)

   #r=0.005,order=2,smooth=25 seems to be the best so far. But still, Do a grid seach kind of stuff in collab to find optimal parameters.
   cf = changefinder.ChangeFinder(r=0.005,order=2,smooth=25)
   scores = []
   break_points = []
   regression_lines = []
   
   #this is to prevent getting inacurate score data for the start of the data
   index_to_concat = 5000
   day_to_add = day.iloc[:index_to_concat].copy()
   price_difference = day.iloc[0]["Price"] - day_to_add.iloc[-1]["Price"]
   day_to_add["Price"] += price_difference
   date_difference = day.iloc[0]["datetime"] - day_to_add.iloc[-1]["datetime"]
   day_to_add["datetime"] += date_difference
   padded_day = pd.concat([day_to_add,day])

   current_breakpoint = None
   #wait_before_regression should be bigger than ignore_regression
   wait_before_regression = 120
   ignore_regression = 60
   regression_fail_treshhold = 100
   segment_horizontal = False

   for i, (_ ,date, value) in enumerate(padded_day.itertuples()):

      score = cf.update(value)
      scores.append(score)
      if score > 125 and i > 5000:
         break_points.append(i)
         current_breakpoint = i
         regression_values = []
         regression_dates = []
         regress = False
         regresion_fail_count = 0
         segment_horizontal = True

      if segment_horizontal:

         if current_breakpoint is not None and i > current_breakpoint + ignore_regression:
            regression_values.append(value)
            regression_dates.append((date - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'))

         if current_breakpoint is not None and i > current_breakpoint + wait_before_regression:
            m, b = np.polyfit(regression_dates, regression_values, 1)
            
            if np.abs(np.arctan(m)) < np.mean(regression_values) * 0.00349066 / 13325: #0.2 degrees in radian / baseline
               regresion_fail_count = 0
            elif np.abs(np.arctan(m)) >= np.mean(regression_values) * 0.00349066 / 13325:
               regresion_fail_count += 1
               
            if regresion_fail_count > regression_fail_treshhold:
               segment_horizontal = False
               
               regression_line_data = m * np.array(regression_dates) + b
               regression_lines.append([regression_line_data, np.array(regression_dates)])
               ##TODO:Find the bug in the 
   
   draw_breakpoints(padded_day, scores, break_points, regression_lines)
