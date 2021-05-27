import datetime
import re
import sys
import os
import random

import mysql.connector
import pdftotext

from bad_pdf import text_from_pdf
from custom_app import set_flag_row
from custom_datadict import make_datadict
from custom_parallel import write, conn_data
from make_log import log_exceptions

set_flag_row(sys.argv[9], 'E', sys.argv[7])

flag = 0

identifier = str(random.randint(99999,999999))
start = datetime.datetime.now()

with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open(f'star/{identifier}.txt', 'w') as f:
    f.write(" ".join(pdf))
num_lines = sum(1 for line in open(f'star/{identifier}.txt'))
if num_lines < 2:
    text_from_pdf(sys.argv[1], f'star/{identifier}.txt')

with open(f'star/{identifier}.txt', 'r') as myfile:
    f = myfile.read()
if os.path.exists(f'star/{identifier}.txt'):
    os.remove(f'star/{identifier}.txt')
try:
    datadict = make_datadict(f)
    preid = re.compile(r"^.*(?= -)").search(sys.argv[5])
    if preid is not None:
        preid = preid.group()
    else:
        preid = ''

    datadict['preid'] = preid

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
