import datetime
import sys
import re

import pdftotext

from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions
from custom_app import set_flag_row

set_flag_row(sys.argv[9], 'E', sys.argv[7])

start = datetime.datetime.now()

with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('Universal_Sompo/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('Universal_Sompo/output.txt', 'r') as myfile:
    f = myfile.read()

try:
    datadict = make_datadict(f)
    datadict['insname'] = ''
    data = [i for i in sys.argv[1:9]]
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
    write(data, sys.argv[9])
    set_flag_row(sys.argv[9], 'X', sys.argv[7])
except:
    log_exceptions()
