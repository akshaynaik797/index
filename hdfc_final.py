import datetime
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
with open('hdfc/output.txt', 'w', encoding="utf-8") as f:
        f.write(" ".join(pdf))     
with open('hdfc/output.txt', 'r', encoding="utf-8") as myfile:
        f = myfile.read()

try:            
        datadict = make_datadict(f)
        if '_' in datadict['preid']:
            datadict['preid'] = datadict['preid'].split('_')[0]
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
