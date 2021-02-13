import datetime
import sys

import pdfkit
import pdftotext

from custom_app import set_flag_graphapi
from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions

set_flag_graphapi(sys.argv[5], sys.argv[6], 'E',sys.argv[7])

start = now = datetime.datetime.now()
try:
    for i in ['.pdf', '.PDF']:
        sys.argv[1] = sys.argv[1].replace(i, '.htm')
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
    pdfkit.from_file(sys.argv[1], 'alankit/out.pdf', configuration=config)
    with open('alankit/out.pdf', "rb") as f:
        pdf = pdftotext.PDF(f)
    with open('alankit/output.txt', 'w') as f:
        f.write(" ".join(pdf))
    with open('alankit/output.txt', 'r') as myfile:
        f = myfile.read()
    datadict = make_datadict(f)
    data = [i for i in sys.argv[1:]]
    data2 = [datadict[i] for i in datadict]
    data.extend(data2)
    data3 = str(datadict)
    data.append(data3)
    end = datetime.datetime.now()
    data.append(str(start))
    data.append(str(end))
    diff = end-start
    diff = str(diff.total_seconds())
    data.append(diff)
    write(data)
    set_flag_graphapi(sys.argv[5], sys.argv[6], 'X',sys.argv[7])
except:
    log_exceptions()