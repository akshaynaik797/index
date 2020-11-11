import datetime
import sys

import pdftotext

from custom_datadict import make_datadict
from make_log import log_exceptions
from custom_parallel import write

now = datetime.datetime.now()

with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('aditya/output1.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('aditya/output1.txt', 'r') as myfile:
    f = myfile.read()

try:
    datadict = make_datadict(f)
    data = [i for i in sys.argv[1:]]
    data2 = [datadict[i] for i in datadict]
    data.extend(data2)
    data3 = str(datadict).replace('{', '\{').replace('}', '\}')
    data.append(data3)
    write(data)

except Exception as e:
    log_exceptions()
now = datetime.datetime.now()
