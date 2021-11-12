from datetime import datetime
import numpy as np
from numpy.lib.function_base import median
import pandas as pd
from pandas.io.formats.format import set_eng_float_format
import xlwings as xw
import ruptures as rpt
import matplotlib.pyplot as plt 
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

from box import Box
from visualisation import draw_daily_plot
from helpers import format_for_pandas

DATA_PATH = r"C:\borsa\boxanalyse\Box Analysis\inputs\DAX_from_2020.csv"
EXCEL_PATH = r""
CSV_PATH = r"C:\borsa\boxanalyse\Box Analysis\outputs\segments.csv"


print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())
print("Started analysing.")

segment_data = []
box_data = []

for idx, day in df.groupby(df.datetime.dt.date):
    print(idx)
    if len(day)<200 or idx<pd.Timestamp('2021-01-01'):
        continue
    
  

    points = day["Price"].to_numpy()

    #breakpoint algorithm
    algo = rpt.Pelt(model="l2", min_size=500, jump=10).fit(points)
    #play with this to figure good parameters pen=np.log(n)*dim*sigma**2 or epsilon=3*n*sigma**2
    breakpoints = algo.predict(pen=1*np.log(len(points))*np.std(points)**2) 

    offsets = [0] + breakpoints[:-1], breakpoints
    horizontals = []
    for current, next in zip(*offsets):
        data_part = day.iloc[current:next]

        #storing parameters to use in excel
        start_date = data_part.iloc[0]["datetime"]
        end_date = data_part.iloc[-1]["datetime"]
        duration_seconds = (end_date - start_date).total_seconds()
        duration_for_excel = duration_seconds / 86400

        dates_in_segment = (data_part["datetime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')  
        dates_in_segment = dates_in_segment.to_numpy()
        prices_in_segment = data_part["Price"].to_numpy()

        #plot to draw to show breakpoints
        plot1 = plt.figure(1)
        plt.plot(dates_in_segment,prices_in_segment)
        
        #offset is to reduce start and end of the segments to get more accurate averages and regressions
        off = 200
        m, b = np.polyfit(dates_in_segment[off:-off], prices_in_segment[off:-off], 1)

        standart_deviation = np.std(prices_in_segment[off:-off])
        max = np.max(prices_in_segment[off:-off])
        min = np.min(prices_in_segment[off:-off])
        difference = max - min
        average = np.mean(prices_in_segment[off:-off])

        #the condition and segmentation parameters could be tweaked
        if np.abs(np.arctan(m)) < average*0.00349066/13325: #0.2 degrees in radian / baseline
            plt.plot(dates_in_segment, m*dates_in_segment + b)
            #print(current,next, np.max(prices_in_segment[off:-off]),np.min(prices_in_segment[off:-off]),np.max(prices_in_segment[off:-off])-np.min(prices_in_segment[off:-off]), np.std(prices_in_segment[off:-off]))

            ###sheesh this algorithm took long to develop 

            #convolutional derivative with 1st derivative gaussian filter
            df_after_horizontal = day.iloc[next-200:-1]
            values_for_peak = df_after_horizontal["Price"].to_numpy()
            smoothing_width = 75    
            padded_values_for_peak = np.pad(values_for_peak, (smoothing_width//2,smoothing_width//2 -1), mode="edge")
            smoothed_values_for_peak = np.convolve(padded_values_for_peak, np.ones(smoothing_width)/smoothing_width, mode='valid')
            negative_values_for_peak = -smoothed_values_for_peak
            #print(values_for_peak.shape,padded_values_for_peak.shape,smoothed_values_for_peak.shape)

            #finding peaks with scipy package
            positive_peaks, _ = find_peaks(smoothed_values_for_peak, prominence=[2, None])
            negative_peaks, _ = find_peaks(negative_values_for_peak, prominence=[2, None])
    
            max_wait = 3600
            combined_peaks = np.concatenate((positive_peaks, negative_peaks), axis=None)
            filtered_peaks = combined_peaks[combined_peaks < max_wait]

            peak_duration_for_excel = None
            pip = None

            if len(combined_peaks) > 0:
  
                if len(filtered_peaks) > 0:
                    peak_values = values_for_peak[filtered_peaks]
                    peaks_to_compare = np.abs(peak_values - average)
                    max_peak = np.max(peaks_to_compare)
                    peak_index_in_filtered = np.where(peaks_to_compare == max_peak)
                    peak_index_in_day = filtered_peaks[peak_index_in_filtered]
                else:
                    peak_index_in_day = combined_peaks.sort()[0]

                peak_data = df_after_horizontal.iloc[peak_index_in_day]
                peak_date, peak_value = peak_data.iloc[0]["datetime"], peak_data.iloc[0]["Price"]
                peak_duration_seconds = (peak_date - start_date).total_seconds()
                peak_duration_for_excel = peak_duration_seconds / 86400
                pip = np.abs(peak_value - average)


            '''
            plot2 = plt.figure(2)
            plt.plot(values_for_peak)
            plt.plot(smoothed_values_for_peak)
            plt.plot(positive_peaks, values_for_peak[positive_peaks], "x")
            plt.plot(positive_peaks, smoothed_values_for_peak[positive_peaks], "x")

                    
            plot3 = plt.figure(3)
            plt.plot(negative_values_for_peak)
            plt.plot(-values_for_peak)
            plt.plot(negative_peaks, -values_for_peak[negative_peaks], "x")
            plt.plot(negative_peaks, negative_values_for_peak[negative_peaks], "x")
            

            plot4 = plt.figure(4)
            plt.plot(day["datetime"],day["Price"])
            plt.plot(peak_date, peak_value, "x")

            plt.show()
            '''

            data_to_store = {"start_index":current,
                             "start_date":start_date,
                             "end_date":end_date,
                             "horizontal_duration":duration_seconds,
                             "horizontal_duration_excel":duration_for_excel,
                             "max_point":max,
                             "min_point":min,
                             "difference":difference,
                             "average":average,
                             "standart_deviation":standart_deviation,
                             "pip":pip,
                             "peak_date":peak_date,
                             "peak_value":peak_value,
                             "preak_duration":peak_duration_seconds,
                             "peak_duration_excel":peak_duration_for_excel
                             }
                             
            horizontals.append(data_to_store)
            segment_data.append(data_to_store)

    plt.show()

    box_list = []
    box_horizontal_data = []

    index_for_day = 0
    horizontal_pointer = 0

    last_date = day.iloc[-1]["datetime"] + pd.DateOffset(minutes=60)

    for (_ ,date, value) in day.itertuples():
        if horizontal_pointer < len(horizontals) and index_for_day == horizontals[horizontal_pointer]["start_index"]+200 and date < last_date:
            boxes_to_add = [Box(horizontals[horizontal_pointer]["average"] , x , date, 0.5 ,0.3, 1, 0.05, custom_start_value=value) 
                            for x in range(round(horizontals[horizontal_pointer]["difference"]) - 3, round(horizontals[horizontal_pointer]["difference"]) + 3)]
            
            box_list += boxes_to_add
            box_horizontal_data += [horizontals[horizontal_pointer] for _ in range(len(boxes_to_add))]
            horizontal_pointer += 1
        index_for_day += 1

        for box in box_list:
            if not box.finished:
                box.analyse_step(value,date)

        
    for box, current_horizontal_data in zip(box_list, box_horizontal_data):
        box_result = box.finish_box()
        box_result["box_size_relation"] = box_result["box_size"] - current_horizontal_data["difference"]
        combined_result = box_result | current_horizontal_data #this only works in python 3.9+
        box_data.append(combined_result)
        #print(combined_result)
        #draw_daily_plot(day, **box_result)


##TODO: handle excel output
print("Analysis Finished. Started writing to excel.")

segments_headers = ["start_date", "end_date", "horizontal_duration", "horizontal_duration_excel", "average", "max_point", "min_point", 
                    "difference", "standart_deviation", "peak_date", "peak_value", "peak_duration", "peak_duration_excel"]
segment_formatted_data = format_for_pandas(segments_headers, segment_data)
segments_df = pd.DataFrame(segment_formatted_data)
segments_df.to_csv(CSV_PATH, mode='w', header=True)

box_headers = segments_headers + ["start_date", "box_median", "upper_limit", "lower_limit", "box_duration_excel", 
                                  "direction", "lot_amount", "transactions", "peak", "peak_date",
                                  "pip","profit","pip_percentage","profit_percentage", "box_percentage", "peak_duration_excel"]

box_formatted_data = format_for_pandas(box_headers, box_data)
box_df = pd.DataFrame(box_formatted_data)

