import pandas as pd
import os



DATA_PATH = r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USDJPY-2020_10_27-2021_10_26.csv"

print("Started reading the file.")
df = pd.read_csv(DATA_PATH, parse_dates=[0], header=0)
df = df.drop(["ask","ask_volume","bid_volume"], axis=1)
df = df.rename(columns={"bid":"Price", "time":"datetime"})
df["Price"] *= 100 #changes, check real values.
df.set_index("datetime",inplace=True)
df = df.resample('1S').last()
df.dropna(inplace=True)

print(df)
print(df.info())

symbol = "USDJPY"
output_folder = f"C:\\borsa\\boxanalyse\\Box_Analysis\\outputs\\labeling_data\\{symbol}"
current_month = None
current_folder = None

for day_idx, day in df.groupby(df.index.date):

    if day_idx.month != current_month:
        current_month = day_idx.month
        folder_name = f"{day_idx.year}-{day_idx.month}"
        current_folder = os.path.join(output_folder,folder_name)
        os.makedirs(current_folder)

    file_name = f"Labeling-{symbol}-{day_idx}.csv"
    file_path = os.path.join(current_folder,file_name)
    day.to_csv(file_path, header=True, mode="w")
