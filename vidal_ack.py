import datetime
import re
import sys

import pdftotext

from custom_app import set_flag_graphapi
from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions

set_flag_graphapi(sys.argv[5], sys.argv[6], 'E',sys.argv[7])

start = datetime.datetime.now()

with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('vidal/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('vidal/output.txt', 'r') as myfile:
    f = myfile.read()

try:
    datadict = make_datadict(f)
    start1 = re.search(r"Pre-Auth Number:", f)
    end1 = re.search(r"in your correspondence", f)
    if start1 is not None and end1 is not None:
        datadict['preid'] = f[start1.end():end1.start()].strip().replace('\n', '')

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
