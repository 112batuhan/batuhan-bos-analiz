import pandas as pd


df = pd.read_csv(r'C:\borsa\boxanalyse\regression\box_data_with_previous_data.csv', header=0, parse_dates=[1])
df.dropna(axis=0, inplace=True)

outside_test = df[(df['start_date']>pd.Timestamp(year=2021, month=4, day=22))]
outside_test.to_csv(r"C:\borsa\boxanalyse\regression\divided_datasets\time_series_50_prev\outside_test.csv", mode='w', header=True)

final_test = df.drop(outside_test.index).sample(frac = 0.1)
final_test.to_csv(r"C:\borsa\boxanalyse\regression\divided_datasets\time_series_50_prev\final_test.csv", mode='w', header=True)

df_test = df.drop(final_test.index).sample(frac = 0.1)
df_test.to_csv(r"C:\borsa\boxanalyse\regression\divided_datasets\time_series_50_prev\df_test.csv", mode='w', header=True)

df_train = df.drop(df_test.index)
df_train.to_csv(r"C:\borsa\boxanalyse\regression\divided_datasets\time_series_50_prev\df_train.csv", mode='w', header=True)


#sizes doesn't match up, check later idk i'm tired.