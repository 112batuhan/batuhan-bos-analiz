import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz
import matplotlib.pyplot as plt

meta_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"
symbol = "GBPJPY"

if not mt5.initialize(meta_path):
    print(f"initialize() for meta client {meta_path} failed.")
    mt5.shutdown()
    quit()

timezone = pytz.timezone("Etc/UTC")
utc_from = datetime(2020, 11, 8, tzinfo=timezone)
utc_to = datetime(2021, 11, 8, tzinfo=timezone)
#ticks = mt5.copy_ticks_from(symbol, 0, 5000000, mt5.COPY_TICKS_INFO)
ticks = mt5.copy_ticks_range(symbol, utc_from, utc_to, mt5.COPY_TICKS_INFO)
print("Ticks received:",len(ticks))
mt5.shutdown()

ticks_frame = pd.DataFrame(ticks)
ticks_frame['time']=pd.to_datetime(ticks_frame['time'])

print("\nDisplay dataframe with ticks")
print(ticks_frame) 

ticks_frame.to_csv("GBPJPY-2020_8_11-2021_8_11.csv")