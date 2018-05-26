import time
#时间戳13转10位
def timestamp_to_timestamp10(time_stamp):
    time_stamp = int (time_stamp* (10 ** (10-len(str(time_stamp)))))
    return time_stamp
#10位时间戳转时间字符串
def timestamp_to_date(time_stamp, format_string="%Y-%m-%d %H:%M:%S"):
    time_array = time.localtime(time_stamp)
    str_date = time.strftime(format_string, time_array)
    return str_date
if __name__=='__main__':
    print(timestamp_to_date(timestamp_to_timestamp10(1513562157849)))