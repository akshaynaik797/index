import datetime
import re
import sys

import pdftotext

from custom_app import set_flag_row
from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions

set_flag_row(sys.argv[9], 'E', sys.argv[7])

start = datetime.datetime.now()
with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('fhpl/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('fhpl/output.txt', 'r') as myfile:
    f = myfile.read()
try:
    datadict = make_datadict(f)
    if datadict['pname'] == '':
        if tmp := re.search(r"(?<=Patient's Name\n).*?(?=\n *PinCode)", f):
            datadict['pname'] = tmp.group().strip()
    if tmp := re.search(r"(?<=Details of Approval for Cashless Request are given below:\n).*", f):
        tmp = tmp.group().replace('RS.', '').strip()
        try:
            datadict['amount'] = re.split(r" +", tmp)[1]
        except:
            pass
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
