from pickle import NONE
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from datetime import datetime

def draw_daily_plot(df, box_size=None, transactions=None, lower_limit=None, upper_breakout=None, lower_breakout=None, start_date=None, broken=None,
                box_duration=None, upper_crossings=None, lower_crossings=None, break_date=None, break_value=None, peak_date=None, peak=None, last_date=None, last_value=None, **kwargs):

    plt.plot(df["datetime"], df["Price"])

    currentAxis = plt.gca()
    box_anchor = (start_date, lower_limit)
    currentAxis.add_patch(Rectangle(box_anchor, box_duration, box_size, fill=None, alpha=1, hatch="/", linestyle="--"))

    plt.axhline(y=upper_breakout, linestyle="--", color="r")
    plt.axhline(y=lower_breakout, linestyle="--", color="r")

    if transactions > 0:

        for value, date in upper_crossings:
            plt.scatter(date, value, s=100, c="g")
        for value, date in lower_crossings:
            plt.scatter(date, value, s=100, c="r")
        if broken:
            plt.scatter(break_date,  break_value, s=100, c="m")
        if peak_date is not None:
            plt.scatter(peak_date, peak, s=115, c="y")

    plt.scatter(last_date, last_value, s=85, c="b")
    plt.show()
