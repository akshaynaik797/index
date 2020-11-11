import sys

import camelot
import openpyxl
import pdftotext

from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions

with open(sys.argv[1], "rb") as f:
	pdf = pdftotext.PDF(f)

with open('Cholamandalam/output.txt', 'w') as f:
	f.write(" ".join(pdf))     
with open('Cholamandalam/output.txt', 'r') as myfile:
 	f = myfile.read()
tables = camelot.read_pdf(sys.argv[1])#,line_scale=10)
tables.export('Cholamandalam/foo1.xlsx', f='excel')
loc = ("Cholamandalam/foo1.xlsx")
wb= openpyxl.load_workbook(loc)
s1_t=wb.worksheets[0]
s2_t=wb.worksheets[1]
row_count_t = s2_t.max_row
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