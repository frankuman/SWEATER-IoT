import time

def adjusted_time():
    current_time = time.localtime()
    adjusted_hour = (current_time[3] + 2) % 24
    adjusted_time = (current_time[0], current_time[1], current_time[2], 
                     adjusted_hour, current_time[4], current_time[5], 
                     current_time[6], current_time[7])
    return adjusted_time

def format_date(time_tuple):
    return "{:04d}-{:02d}-{:02d}".format(time_tuple[0], time_tuple[1], time_tuple[2])

def format_time(time_tuple):
    return "      {:02d}:{:02d}:{:02d}".format(time_tuple[3], time_tuple[4], time_tuple[5])

def format_day_of_week(time_tuple):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[time_tuple[6]]
