import pandas as pd
import matplotlib.pyplot as plt

columns = ["timestamp", "ask", "bid", "ask_volume", "bid_volume"]

df = pd.read_csv("2021-08-02.csv", names=columns)
df.drop(columns=["ask","ask_volume","bid_volume"],inplace=True)
df['timestamp'] = pd.to_datetime(df['timestamp'],unit="ms")
df.set_index("timestamp",inplace=True)
df = df.resample('1S').last()
df.dropna(inplace=True)


print(df)
print(df.info())

df.to_csv("processed_2021-08-02.csv",header=True, mode="w")

plt.plot(df)
plt.show()