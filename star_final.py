import datetime
import re
import subprocess
import sys

import pdftotext

from make_log import log_exceptions
from bad_pdf import text_from_pdf
from custom_datadict import make_datadict
from custom_parallel import write


flag = 0


with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('star/output.txt', 'w') as f:
    f.write(" ".join(pdf))
num_lines = sum(1 for line in open('star/output.txt'))
if num_lines < 2:
    flag = 1
    text_from_pdf(sys.argv[1], 'star/output.txt')

with open('star/output.txt', 'r') as myfile:
    f = myfile.read()

try:
    datadict = make_datadict(f)
    preid = re.compile(r"^.*(?= -)").search(sys.argv[5])
    if preid is not None:
        preid = preid.group()
    else:
        preid = ''

    datadict['preid'] = preid

    data = [i for i in sys.argv[1:]]
    data2 = [datadict[i] for i in datadict]
    data.extend(data2)
    data3 = str(datadict).replace('{', '\{').replace('}', '\}')
    data.append(data3)
    write(data)
except:
    log_exceptions()