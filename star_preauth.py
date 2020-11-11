import os
import re
import sys
import struct, time
import subprocess
from datetime import date
import datetime
import openpyxl
import pdftotext
from bad_pdf import text_from_pdf
from make_log import log_exceptions
from custom_datadict import make_datadict
from custom_parallel import write
import time
import requests

from patient_name_fun import pname_fun

now = datetime.datetime.now()

subprocess.run(["python", "updation.py","1","max1","1",sys.argv[2]])
subprocess.run(["python", "updation.py","1","max","2",sys.argv[3]])
subprocess.run(["python", "updation.py","1","max","3",sys.argv[4]])
subprocess.run(["python", "updation.py","1","max","5",str(now)])
subprocess.run(["python", "updation.py","1","max","7",sys.argv[5]])
subprocess.run(["python", "updation.py","1","max","8",sys.argv[6]])


with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('star/output.txt', 'w') as f:
    f.write(" ".join(pdf))
num_lines = sum(1 for line in open('star/output.txt'))
if num_lines < 2:
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
