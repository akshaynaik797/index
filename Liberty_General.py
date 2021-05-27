import datetime
import re
import sys

import pdftotext

from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions
from custom_app import set_flag_row
try:
    set_flag_row(sys.argv[9], 'E', sys.argv[7])

    start = now = datetime.datetime.now()
    with open(sys.argv[1], "rb") as f:
        pdf = pdftotext.PDF(f)

    with open('liberty/output.txt', 'w') as f:
        f.write(" ".join(pdf))
    with open('liberty/output.txt', 'r') as myfile:
        f = myfile.read()

    datadict = make_datadict(f)
    status = ''
    if "Additional information required towards hospitalization" in f:
        status = 'Information Awaiting'
    elif 'Cashless final authorization' in f or 'pre-authorization request submitted':
        status = 'Approved'
    sys.argv[4] = sys.argv[4] + ',' + status
    # datadict['status'] = status
    data = [i for i in sys.argv[1:9]]
    data2 = [datadict[i] for i in datadict]
    data.extend(data2)
    data3 = str(datadict)
    data.append(datadict)
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
