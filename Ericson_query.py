import sys

import pdftotext

from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions

with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('Ericson/output.txt', 'w', encoding="utf-8") as f:
    f.write(" ".join(pdf))
with open('Ericson/output.txt', 'r', encoding="utf-8") as myfile:
    f = myfile.read()
try:
    datadict = make_datadict(f)
    data = [i for i in sys.argv[1:]]
    data2 = [datadict[i] for i in datadict]
    data.extend(data2)
    data3 = str(datadict).replace('{', '\{').replace('}', '\}')
    data.append(data3)
    write(data)
except:
    log_exceptions()