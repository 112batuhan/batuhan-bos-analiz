setup = {

    "EURUSD":{
        "multiplier":1,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\EURUSD-2020_10_27-2021_10_31.csv",
        "start_hour":time(1,15,0),
        "end_hour":time(23,45,0),
        "big_number_roundness": 2,
        "extra_parse":True,
        "hour_shift":3
    },
    "GBPJPY":{
        "multiplier":1,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USDJPY-2020_10_27-2021_10_26.csv",
        "start_hour":time(1,15,0),
        "end_hour":time(23,45,0),
        "big_number_roundness": 0,
        "extra_parse":False,
        "hour_shift":1
    },
    "USDJPY":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USDJPY-2020_10_27-2021_10_26.csv",
        "start_hour":time(1,15,0),
        "end_hour":time(23,45,0),
        "big_number_roundness": 0,
        "extra_parse":True,
        "hour_shift":3
    },
    "DAX":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\DEUIDXEUR-2020_10_27-2021_10_26.csv",
        "start_hour":time(10,0,0),
        "end_hour":time(18,30,0),
        "big_number_roundness": -2,
        "extra_parse":True,
        "hour_shift":3
    },
    "DOW":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USA30IDXUSD-2020_10_27-2021_10_26.csv",
        "start_hour":time(16,30,0),
        "end_hour":time(23,00,0),
        "big_number_roundness": -2,
        "extra_parse":True,
        "hour_shift":3
    },
    "NASDAQ":{
        "multiplier":100,
        "path":r"C:\borsa\boxanalyse\Box_Analysis\inputs\pivotdata\USATECHIDXUSD-2020_10_27-2021_10_26.csv",
        "start_hour":time(16,30,0),
        "end_hour":time(23,0,0),
        "big_number_roundness": -2,
        "extra_parse":True,
        "hour_shift":3
    },

}