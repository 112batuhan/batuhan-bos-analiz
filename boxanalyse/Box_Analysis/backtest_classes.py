from datetime import datetime, time, timedelta
import math

import sys
sys.path.append(r"C:\borsa\boxanalyse\Box_Analysis")
from box import Box

def format_for_pandas(headers, data):
    
    formated_data = {}
    for header in headers:
        formated_data[header] = []
        for row in data:
            formated_data[header].append(row[header])

    return formated_data

class BaseBacktest:
    def __init__(self, start_value, box_percentage, box_breakout, peak_breakout, max_steps):

        self.box_active = False
        self.start_value = start_value

        self.box_percentage = box_percentage
        self.box_breakout = box_breakout
        self.peak_breakout = peak_breakout
        self.max_steps = max_steps

        self.current_box = None
        self.result_data = []

    def get_results(self):

        if self.box_active:
            self.result_data.append(self.current_box.finish_box())    
        
        return self.result_data
        #if len(self.result_data)>0:
        #    return format_for_pandas(self.result_data)
        
        #return []


class BigNumber(BaseBacktest):

    def __init__(self, start_value, box_percentage, box_breakout, peak_breakout, max_steps, big_number_roundness):
        super().__init__(start_value, box_percentage, box_breakout, peak_breakout, max_steps)

        self.big_number_crossed = False
        self.big_number_roundness = big_number_roundness

        self.big_number_incrementor = math.pow(10, (-big_number_roundness))
        self.big_number_calculator(start_value)

    def big_number_calculator(self, value):
        self.upper_big_numer = (value + self.big_number_incrementor) - (value % self.big_number_incrementor)
        self.lower_big_number = value - (value % self.big_number_incrementor)

    def iterate_tick(self, value, date):

        if value > self.upper_big_numer or value < self.lower_big_number:
            current_big_number = round(value, self.big_number_roundness)
            self.upper_big_numer = current_big_number + self.big_number_incrementor
            self.lower_big_number = current_big_number - self.big_number_incrementor
            self.big_number_crossed = True
        
        if self.big_number_crossed and self.box_active:
            self.current_box.finished = True

        if self.box_active and self.current_box.finished:
            self.result_data.append(self.current_box.finish_box())    
            self.box_active = False
            if not self.big_number_crossed:
               self.big_number_calculator(value)

        if self.big_number_crossed:
            self.current_box = Box(value, value * 0.01 * self.box_percentage, date, self.box_breakout, self.peak_breakout, transaction_limit=self.max_steps)
            self.big_number_crossed = False
            self.box_active = True
        
        if self.box_active:
            self.current_box.analyse_step(value, date)


class FiboPivot(BaseBacktest):

    def __init__(self, start_value, box_percentage, box_breakout, peak_breakout, max_steps):
        super().__init__(start_value, box_percentage, box_breakout, peak_breakout, max_steps)
        
        self.last_value = start_value

        self.pivots = None
        self.pivot_value_crossed = False

    def set_fibonacci_pivots(self, daily_high, daily_low, daily_close):
        R = daily_high - daily_low
        P = (daily_high + daily_low + daily_close) / 3

        R1 = P + (R * 0.382)
        R2 = P + (R * 0.618)
        R3 = P + (R * 1.00)
        S1 = P - (R * 0.381)
        S2 = P - (R * 0.618)
        S3 = P - (R * 1.00)

        self.pivots = [R1, R2, R3, S1, S2, S3]

    def iterate_tick(self, value, date):
        
        if self.pivots:
            for pivot_value in self.pivots:
                if (self.last_value < pivot_value and value > pivot_value) or (self.last_value > pivot_value and value < pivot_value):
                    self.pivot_value_crossed = True

            if self.pivot_value_crossed and self.box_active:
                self.current_box.finished = True

            if self.box_active and self.current_box.finished:
                self.result_data.append(self.current_box.finish_box())    
                self.box_active = False

            if self.pivot_value_crossed:
                self.current_box = Box(value, value * 0.01 * self.box_percentage, date, self.box_breakout, self.peak_breakout, transaction_limit=self.max_steps)
                self.pivot_value_crossed = False
                self.box_active = True

            if self.box_active:
                self.current_box.analyse_step(value, date)
    
            self.last_value = value


class DayStartBreakout(BaseBacktest):

    def __init__(self, start_value, box_percentage, box_breakout, peak_breakout, max_steps, breakout_values):
        super().__init__(start_value, box_percentage, box_breakout, peak_breakout, max_steps)

        self.last_value = start_value
        self.breakout_values = breakout_values
        self.breakout_value_crossed = False

    def iterate_tick(self, value, date):
        
        for breakout_value in self.breakout_values:
            if (self.last_value < breakout_value and value > breakout_value) or (self.last_value > breakout_value and value < breakout_value):
                self.breakout_value_crossed = True

        if self.breakout_value_crossed and self.box_active:
            self.current_box.finished = True

        if self.box_active and self.current_box.finished:
            self.result_data.append(self.current_box.finish_box())
            self.box_active = False

        if self.breakout_value_crossed:
            self.current_box = Box(value, value * 0.01 * self.box_percentage, date, self.box_breakout, self.peak_breakout, transaction_limit=self.max_steps)
            self.breakout_value_crossed = False
            self.box_active = True

        if self.box_active:
            self.current_box.analyse_step(value, date)

        self.last_value = value


class RandomBox(BaseBacktest):
    
    def __init__(self, start_value, box_percentage, box_breakout, peak_breakout, max_steps):
        super().__init__(start_value, box_percentage, box_breakout, peak_breakout, max_steps)

    def iterate_tick(self, value, date):

        if self.current_box is None:
            self.current_box = Box(value, value * 0.01 * self.box_percentage, date, self.box_breakout, self.peak_breakout, transaction_limit=self.max_steps)
        else:
            if not self.current_box.finished:
                self.current_box.analyse_step(value, date)
            else:
                self.result_data.append(self.current_box.finish_box())
                self.current_box = Box(value, value * 0.01 * self.box_percentage, date, self.box_breakout, self.peak_breakout, transaction_limit=self.max_steps)


class StartBox(BaseBacktest):

    def __init__(self, start_value, box_percentage, box_breakout, peak_breakout, max_steps):
        super().__init__(start_value, box_percentage, box_breakout, peak_breakout, max_steps)

    def iterate_tick(self, value, date):
        
        if self.current_box is None:
            self.current_box = Box(value, value * 0.01 * self.box_percentage, date, self.box_breakout, self.peak_breakout, transaction_limit=self.max_steps)
            self.box_active = True
        else:
            if not self.current_box.finished:
                self.current_box.analyse_step(value, date)
            else:
                self.result_data.append(self.current_box.finish_box())
                self.box_active = False

                