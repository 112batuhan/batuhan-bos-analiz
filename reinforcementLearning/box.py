
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
                self.increment_lot()
                self.reset_peaks()
                self.last_buy = True
                self.last_sell = False
                self.upper_crossings.append((value,date))

            #lower limit crossing
            elif not self.last_sell and self.previous_value > self.lower_limit and value <= self.lower_limit:
                self.increment_lot()
                self.reset_peaks()
                self.last_buy = False
                self.last_sell = True
                self.lower_crossings.append((value,date))

            elif (self.last_buy and value > self.upper_box_breakout) or (self.last_sell and value < self.lower_box_breakout):
                self.broken = True
                self.break_value = value
                self.break_date = date

            if self.transaction_limit is not None and self.step >= self.transaction_limit:
                self.finished = True
                self.transaction_broken = True


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





