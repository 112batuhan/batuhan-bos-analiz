import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt 
from arch.unitroot import ZivotAndrews, DFGLS, KPSS, ADF, PhillipsPerron
from arch.utility.exceptions import InfeasibleTestException
from tensorflow import keras



DATA_PATH = r"C:\borsa\boxanalyse\Box_Analysis\inputs\DAX_from_2020.csv"

print("Started reading the file.")
custom_date_parser = lambda x,y: pd.to_datetime(x+" "+y, format='%m/%d/%Y %H:%M:%S')
df = pd.read_csv(DATA_PATH, header=0, parse_dates={'datetime':[0,1]}, date_parser=custom_date_parser)
print(df)
print(df.info())


i = -1
indexxx = 200

with open(r"C:\borsa\boxanalyse\Box_Analysis\stationaryty_detection\X_scaler.pickle", "rb") as f:
    X_scaler = pkl.load(f)

model = keras.models.load_model(r"C:\borsa\boxanalyse\Box_Analysis\stationaryty_detection\models\300_epoch_100x3_dropout\model.h5")


for idx, day in df.groupby(df.datetime.dt.date):
    i += 1
    if len(day)<200 or i != indexxx:
        continue
    print(i)
    print(idx)

    lag = 400
    change_points = []
    consecutives = 0
    sliding_window = []

    for index_in_day in range(lag, len(day), 3):

        data_part = day.iloc[index_in_day - lag : index_in_day]
        prices = data_part["Price"].to_numpy()

        results = [ZivotAndrews(prices), ADF(prices), KPSS(prices), DFGLS(prices), PhillipsPerron(prices)]
        
        features = [np.std(data)/np.mean(data)]


        try: #sometimes pvalue calculation throws InfeasibleTestException for statistic number being outside of p table range
            features += ([result.pvalue for result in results] + [result.stat for result in results])
            test = True #error correction 
        except InfeasibleTestException:
            test = False #error correction
            
        if test: #error correction
            scaled_features = X_scaler.transform([features])

            result = model.predict(scaled_features)

            '''
            if result[0][0] > 0.90:
                change_points.append(index_in_day)
            '''

            if result[0][0] > 0.90:
                sliding_window.append(1)
                if np.sum(sliding_window) > 4:
                    change_points += list(range(index_in_day-lag, index_in_day))
                    sliding_window = []
            else:
                sliding_window.append(0)

            if len(sliding_window) > 75:
                sliding_window.pop(0)


            '''
            if result[0][0] > 0.90:
                consecutives += 1
            else:
                consecutives -= 1

            if consecutives > 3:
                change_points += list(range(index_in_day-lag, index_in_day))

            if consecutives > 5:
                consecutives = 5
            elif consecutives < 0:
                consecutives = 0
            '''

    data = day["Price"].to_numpy()
    change_points = np.unique(change_points).astype(int)
    #print(np.average(slopes))

    plt.plot(data)
    plt.scatter(change_points, data[change_points],color="red",s=10)

    plt.show()