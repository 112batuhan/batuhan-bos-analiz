
from datetime import date
from pickle import NONE


class Box:
    
    def __init__(self, median, size, start_date, box_breakout=1, peak_breakout=0.2, lot_first_size=1, lot_input_size=0.05, peak_box_breakout=25, transaction_limit=None, custom_start_value=None, custom_limits=None):
        #some variables are redundant, maybe make them all kwargs.
        self.median = median
        self.size = size
        self.upper_limit = median + (size / 2)
        self.lower_limit = median - (size / 2)

        if custom_limits is not None:
            self.upper_limit = custom_limits[1]
            self.lower_limit = custom_limits[0]

        if custom_start_value is not None:
            self.previous_value = custom_start_value
        else:
            self.previous_value = median

        self.start_date = start_date
        self.upper_box_breakout = self.upper_limit + (size * box_breakout)
        self.lower_box_breakout = self.lower_limit - (size * box_breakout)

        self.upper_peak_breakout = self.upper_box_breakout + (peak_box_breakout * size * box_breakout)
        self.lower_peak_breakout = self.lower_box_breakout - (peak_box_breakout * size * box_breakout)

        self.peak_breakout = peak_breakout

        self.broken = False
        self.last_buy = False
        self.last_sell = False

        self.step = 0
        self.lot_first_size = lot_first_size
        self.lot_input_size = lot_input_size
        self.current_lot = 0
        self.net_lot = 0
        self.loss = 0

        self.upper_crossings = []
        self.lower_crossings = []

        self.lowest_value = 1000000
        self.highest_value = -1000000
        
        self.break_date = start_date
        self.high_peak_date = start_date
        self.low_peak_date = start_date
        self.last_date = start_date
        
        self.finished = False

        self.break_value = None

        self.transaction_limit = transaction_limit
        self.transaction_broken = False

    def increment_lot(self):
        if self.step == 0:
            self.current_lot = self.lot_first_size
            self.net_lot = self.lot_first_size
        elif self.step == 1:
            self.loss += self.current_lot * self.size
            self.current_lot = self.current_lot*3
            self.net_lot = self.current_lot - self.net_lot
        else:
            self.loss += self.current_lot * self.size
            self.current_lot = self.current_lot * (2 + self.lot_input_size)
            self.net_lot = self.current_lot - self.net_lot
        self.step += 1
    
    def calculate_profit(self, current_price):
        if self.last_sell:
            profit = (self.lower_limit - current_price) * self.net_lot - self.loss
        elif self.last_buy:
            profit = (current_price - self.upper_limit) * self.net_lot - self.loss
        else:
            profit = 0
        return profit

    def reset_peaks(self):
        self.highest_value = -1000000
        self.lowest_value = 1000000


    def analyse_step(self, value, date):

        if not self.broken:
            
            #upper limit crossing
            if not self.last_buy and self.previous_value < self.upper_limit and value >= self.upper_limit:
                if self.transaction_limit is not None and self.step >= self.transaction_limit:
                    self.finished = True
                else:
                    self.increment_lot()
                    self.reset_peaks()
                    self.last_buy = True
                    self.last_sell = False
                    self.upper_crossings.append((value,date))

            #lower limit crossing
            elif not self.last_sell and self.previous_value > self.lower_limit and value <= self.lower_limit:
                if self.transaction_limit is not None and self.step >= self.transaction_limit:
                    self.finished = True
                else:
                    self.increment_lot()
                    self.reset_peaks()
                    self.last_buy = False
                    self.last_sell = True
                    self.lower_crossings.append((value,date))

            elif (self.last_buy and value > self.upper_box_breakout) or (self.last_sell and value < self.lower_box_breakout):
                self.broken = True
                self.break_value = value
                self.break_date = date


        else:
            #these four conditions could be combined but this increases readability imo.
            if self.last_buy and (self.highest_value - value > (self.highest_value - self.median) * self.peak_breakout):
                self.finished = True
            elif self.last_sell and (value - self.lowest_value > (self.median - self.lowest_value) * self.peak_breakout):
                self.finished = True
            elif self.last_buy and (value > self.upper_peak_breakout):
                self.finished = True
            elif self.last_sell and (value < self.lower_peak_breakout):
                self.finished = True

        if value > self.highest_value:
            self.highest_value = value
            self.high_peak_date = date
        elif value < self.lowest_value:
            self.lowest_value = value
            self.low_peak_date = date

        self.previous_value = value
        self.last_date = date
    
    def finish_box(self, calculate_with_last_value=False):

        real_profit = None
        real_pip = None
        real_profit_percentage = None
        real_pip_percentage = None
        theoretical_profit = None
        theoretical_pip = None
        theoretical_profit_percentage = None
        theoretical_pip_percentage = None
        peak = None
        direction = "middle"
        peak_date = None
        box_percentage = self.size / self.median * 100

       
        if self.last_buy:
            real_profit = self.calculate_profit(self.previous_value)
            real_pip = self.previous_value - self.upper_limit
            real_profit_percentage = real_profit/ self.previous_value * 100
            real_pip_percentage = real_pip / self.previous_value * 100

            theoretical_profit = self.calculate_profit(self.highest_value)
            theoretical_pip = self.highest_value - self.upper_limit
            theoretical_profit_percentage = theoretical_profit/ self.highest_value * 100
            theoretical_pip_percentage = theoretical_pip / self.highest_value * 100

            direction = "up"
            peak = self.highest_value
            peak_date = self.high_peak_date

        elif self.last_sell:

            real_profit = self.calculate_profit(self.previous_value)
            real_pip = self.lower_limit - self.previous_value
            real_profit_percentage = real_profit/ self.previous_value * 100
            real_pip_percentage = real_pip / self.previous_value * 100

            theoretical_profit = self.calculate_profit(self.lowest_value)
            theoretical_pip = self.lower_limit - self.lowest_value
            theoretical_profit_percentage = theoretical_profit/ self.lowest_value * 100
            theoretical_pip_percentage = theoretical_pip / self.lowest_value * 100

            direction = "down"
            peak = self.lowest_value
            peak_date = self.low_peak_date

        if self.broken:
            box_duration = (self.last_date - self.start_date)
            peak_duration = peak_date - self.start_date
        else:
            box_duration = (self.last_date - self.start_date)
            peak_duration = self.last_date - self.start_date

        box_duration_seconds = box_duration.total_seconds()
        box_duration_for_excel = box_duration_seconds / 86400
        
        peak_duration_seconds = peak_duration.total_seconds()
        peak_duration_for_excel = peak_duration_seconds / 86400

        self.finished = True
        return {"real_profit":real_profit, 
                "real_pip":real_pip,
                "real_profit_percentage":real_profit_percentage,
                "real_pip_percentage":real_pip_percentage,
                "theoretical_profit":theoretical_profit, 
                "theoretical_pip":theoretical_pip,
                "theoretical_profit_percentage":theoretical_profit_percentage,
                "theoretical_pip_percentage":theoretical_pip_percentage,
                "direction":direction,
                "peak":peak,
                "broken":self.broken,
                "box_size":self.size,
                "box_percentage":box_percentage,
                "peak_date":peak_date, 
                "start_date":self.start_date,
                "last_date":self.last_date,
                "last_value":self.previous_value,
                "break_date":self.break_date,
                "break_value":self.break_value,
                "box_duration":box_duration,
                "box_duration_seconds":box_duration_seconds,
                "box_duration_excel":box_duration_for_excel,
                "peak_duration":peak_duration,
                "peak_duration_seconds":peak_duration_seconds,
                "peak_duration_excel":peak_duration_for_excel,
                "lot_amount":self.current_lot,
                "transactions":self.step,
                "upper_limit":self.upper_limit,
                "lower_limit":self.lower_limit,
                "box_median":self.median,
                "upper_breakout":self.upper_box_breakout,
                "lower_breakout":self.lower_box_breakout,
                "upper_crossings":self.upper_crossings,
                "lower_crossings":self.lower_crossings
                }




