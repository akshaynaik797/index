import sqlite3
import subprocess
from datetime import datetime, timedelta
from pytz import timezone
from make_log import log_exceptions, log_data
from dateutil import parser as date_parser


def ifutc_to_indian(l_time):
  try:
    a = date_parser.parse(l_time)
    b = '%a %d %b %Y %H:%M:%S %z'
    with open('l_time.txt', 'a+') as temp:
        temp.write(l_time+'\n')
    india = timezone('Asia/Kolkata')
    c = a.astimezone(india)
    sysnow = datetime.now(india)
    if c > sysnow:
      c = a.replace(tzinfo=india)
    temp_t = c.replace(tzinfo=None)
    l_time = c.strftime(b)
    if temp_t > datetime.now():
      log_data(msg='l_time greater than cur time.',l_time=l_time, now_time=str(datetime.now()))
    elif temp_t < datetime.now()-timedelta(seconds=900):
      log_data(msg='l_time less than (curtime-15min).', l_time=l_time, now_time=str(datetime.now()))
    return l_time
  except Exception as e:
    log_exceptions()
    print(e)
    return l_time

def time_fun_two(l_time):
  try:
    format = "%d/%m/%Y %H:%M:%S"
    a = datetime.strptime(l_time, format)
    sysnow = datetime.now()
    if a < sysnow - timedelta(seconds=500):
      a = sysnow
    l_time = a.strftime(format)
    return l_time
  except Exception as e:
    log_exceptions()
    print(e)
    return l_time

if __name__ == "__main__":
  l_time = 'Wed, 17 Sep 2020 08:53:24 +0530'
  a = ifutc_to_indian(l_time)
  b = time_fun_two("22/09/2020 08:53:24")
  pass