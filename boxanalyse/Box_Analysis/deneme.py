import pandas as pd

df = pd.read_csv(r"C:\borsa\boxanalyse\Box_Analysis\outputs\dropnatest.csv",header=0)



df.dropna(inplace=True, subset=["real_profit"])
print(df.head(30))
print(df.iloc[17])