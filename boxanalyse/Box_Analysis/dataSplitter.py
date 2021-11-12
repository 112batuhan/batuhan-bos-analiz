from datetime import datetime
from file_read_backwards import FileReadBackwards

def read_data(path):

    print("started reading the data")
    prev_day = 0
    return_lines = []
    values = []
    dates = []
    with FileReadBackwards(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            stripped_line = line.strip()
            data_line = stripped_line.split(",")
            
            if i == 0:
                first_month, first_day, first_year = [int(i) for i in data_line[0].split("/")] 
                continue
            #elif i > 10**5:
            #   break
            else:

                month ,day, year = [int(k) for k in data_line[0].split("/")] 
                return_lines.append(line)
                
                if prev_day != day:
                    print(month, day, year)
                prev_day = day

                if month == 12 and year == 2019:
                    break
                
                
                #values.append(float(data_line[2]))
                #dates.append(datetime.strptime(data_line[0]+ " " + data_line[1], '%m/%d/%Y %H:%M:%S'))
    
    print("finished reading the data")
    return list(reversed(return_lines))
    #return (values, dates)

def write_data(path, data):
    
    with open(path, 'w') as f:
        for line in data:
            f.write(line+"\n")


if __name__ == "__main__":

    INPUT_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_CashIndex_Tick_052011-052021.csv"
    OUTPUT_PATH = r"C:\borsa\boxanalyse\Box Analysis\DAX_from_2020.csv"

    data = read_data(INPUT_PATH)
    write_data(OUTPUT_PATH, data)