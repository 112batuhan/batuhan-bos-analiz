import pandas as pd
from pprint import pprint
import os

def parse_file_name(path):

    file_name = os.path.split(path)[1][:-4]
    splited = file_name.split("-")[2:]

    value_descriptions = ["box_percentage", "peak_breakout", "box_breakout", "max_steps"]

    return_dict = {}

    for description, splited in zip(value_descriptions, splited):
        value = float(splited.split("_")[1])
        return_dict[description] = value

    return return_dict

def find_filtered_percentages(df, filter_column, value, logic):
    
    if logic == ">":
        filter_expression = df[filter_column] > value
    elif logic == "<":
        filter_expression = df[filter_column] < value

    return df.loc[filter_expression][filter_column]


def get_backtest_result_with_df(df, box_percentage=None, peak_breakout=None, box_breakout=None, max_steps=None):

    data = {"box_percentage":box_percentage,
            "peak_breakout":peak_breakout,
            "box_breakout":box_breakout,
            "max_steps":max_steps}


    data["total_initiated_boxes"] = len(df)
    df.dropna(inplace=True, subset=["real_profit"])
    df = df.loc[df["peak"]<900000]
    data["boxes_with_steps"] = len(df)

    percentage_list = ["real_profit_percentage", "real_pip_percentage", "theoretical_profit_percentage", "theoretical_pip_percentage"]

    df_percentages = df[percentage_list + ["start_date"]]
    durations = df[["box_duration_seconds","peak_duration_seconds"]]
    steps = df["transactions"]

    monthly_average_sum_data = df_percentages.groupby(pd.Grouper(key='start_date', freq='1M')).sum().mean()
    daily_average_sum_data = df_percentages.groupby(df_percentages.start_date.dt.date).sum().mean()

    df_percentages = df_percentages[percentage_list]
    averages = df_percentages.mean()
    sums = df_percentages.sum()
    
    for percentage_name in percentage_list:
        data["average_" + percentage_name] = averages.loc[percentage_name]
        data["sum_" + percentage_name] = sums.loc[percentage_name]
        data["monthly_average_sum_"+ percentage_name] = monthly_average_sum_data.loc[percentage_name]
        data["daily_average_sum_"+ percentage_name] = daily_average_sum_data.loc[percentage_name]

        if "pip" in percentage_name:
            comparasion_value = 0.01
        else:
            comparasion_value = 0.1
        data[percentage_name + f"_bigger_{comparasion_value}_count"] = len(find_filtered_percentages(df_percentages, percentage_name, comparasion_value, ">"))
        data[percentage_name + f"_bigger_{comparasion_value}_ratio"] = data[percentage_name + f"_bigger_{comparasion_value}_count"] / data["boxes_with_steps"]

    real_profit_smaller_0 = find_filtered_percentages(df_percentages, "real_profit_percentage", 0, "<")
    data["real_profit_smaller_0_count"] = len(real_profit_smaller_0)
    data["real_profit_smaller_0_average"] = real_profit_smaller_0.mean()
    data["real_profit_smaller_0_ratio"] =data["real_profit_smaller_0_count"] / data["boxes_with_steps"]

    theoretical_profit_smaller_0 = find_filtered_percentages(df_percentages, "theoretical_profit_percentage", 0, "<")
    data["theoretical_profit_smaller_0_count"] = len(theoretical_profit_smaller_0)
    data["theoretical_profit_smaller_0_average"] = theoretical_profit_smaller_0.mean()
    data["theoretical_profit_smaller_0_ratio"] =data["theoretical_profit_smaller_0_count"] / data["boxes_with_steps"]

    data["average_theoretical_pip"] = df["theoretical_pip"].mean()
    data["average_box_size"] = df["box_size"].mean()

    average_seconds = durations.mean()

    data["real_excel_time"] = average_seconds.loc["box_duration_seconds"] / 86400
    data["theoretical_excel_time"] = average_seconds.loc["peak_duration_seconds"] / 86400

    data["average_steps"] = steps.mean()

    step_distribution_string = ""
    value_counts = steps.value_counts()
    for (i,(step ,counts)) in enumerate(value_counts.iteritems()):
        step_distribution_string += f"{step},{counts}"
        if i < len(value_counts)-1:
            step_distribution_string += "_"    
    data["step_distributions"] = step_distribution_string

    return data


def get_backtest_result(path):

    df = pd.read_csv(path,header=0,parse_dates=[14,15,16])
    data = parse_file_name(path)
    return get_backtest_result_with_df(df, **data)
    
    

if __name__ == "__main__":
    get_backtest_result(r"C:\borsa\boxanalyse\Box_Analysis\outputs\pivot_outputs_limited_steps_3\DAX\big_number\bignubmer--bp_0.01-bb_0.10-bp_1.00-ms_4.csv")