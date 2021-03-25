import os
import re
import sys
import struct, time
import subprocess
from datetime import date
import datetime
import openpyxl
import pdftotext
import time
import requests

from make_log import log_exceptions
from custom_parallel import write
from custom_datadict import make_datadict
from custom_app import set_flag_graphapi

set_flag_graphapi(sys.argv[5], sys.argv[6], 'E',sys.argv[7])

start = datetime.datetime.now()
with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)
with open('hdfc/output1.txt', 'w',encoding="utf-8") as f:
    f.write(" ".join(pdf))
with open('hdfc/output1.txt', 'r') as myfile:
    f = myfile.read()
try:
    datadict = make_datadict(f)
    if '_' in datadict['preid']:
        datadict['preid'] = datadict['preid'].split('_')[0]
    datadict['insname'] = ''
    data = [i for i in sys.argv[1:]]
    data2 = [datadict[i] for i in datadict]
    data.extend(data2)
    data3 = str(datadict)
    data.append(data3)
    end = datetime.datetime.now()
    data.append(str(start))
    data.append(str(end))
    diff = end - start
    diff = str(diff.total_seconds())
    data.append(diff)
    write(data)
    set_flag_graphapi(sys.argv[5], sys.argv[6], 'X', sys.argv[7])

except:
    log_exceptions()
