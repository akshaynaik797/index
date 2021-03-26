import sys
import datetime
import sys
import re

import pdftotext

from custom_app import set_flag_graphapi
from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions

set_flag_graphapi(sys.argv[5], sys.argv[6], 'E',sys.argv[7])

start = datetime.datetime.now()
with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('health_heritage/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('health_heritage/output.txt', 'r') as myfile:
    f = myfile.read()

try:
    datadict = make_datadict(f)
    if datadict['amount'] == '':
        with open('health_heritage/output.txt', 'r') as myfile:
            f_list = myfile.readlines()
            for i, j in enumerate(f_list):
                if 'Amount' in j:
                    temp = re.split(r" {2,}", f_list[i+1])
                    datadict['amount'] = temp[2]
                    break
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
    set_flag_graphapi(sys.argv[5], sys.argv[6], 'X',sys.argv[7])

except:
    log_exceptions()
