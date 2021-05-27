import sys
import datetime

import camelot
import openpyxl
import pdftotext

from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions
from custom_app import set_flag_row

set_flag_row(sys.argv[9], 'E', sys.argv[7])

start = datetime.datetime.now()
with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('Cholamandalam/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('Cholamandalam/output.txt', 'r') as myfile:
    f = myfile.read()
tables = camelot.read_pdf(sys.argv[1])  # ,line_scale=10)
tables.export('Cholamandalam/foo1.xlsx', f='excel')
loc = ("Cholamandalam/foo1.xlsx")
wb = openpyxl.load_workbook(loc)
s1_t = wb.worksheets[0]
s2_t = wb.worksheets[1]
row_count_t = s2_t.max_row
try:
    datadict = make_datadict(f)
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
