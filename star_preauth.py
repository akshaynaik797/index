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
    temp = re.compile(r"^[\w\/]+").search(sys.argv[5])
    if temp is not None:
        preid = temp.group().strip()
    else:
        preid = ""
    subprocess.run(["python", "updation.py","1","max","9",'Yes'])
    subprocess.run(["python", "updation.py","1","max","10",'NA'])

    try:
        subprocess.run(
            ["python", "test_api.py", preid, datadict['amount'], datadict['polno'], 'Pa',
             'Approved', sys.argv[6], sys.argv[1], '', datadict['memid'], datadict['pname']])
        subprocess.run(["python", "updation.py","1","max","11",'Yes'])
    except Exception as e:
        log_exceptions()
        subprocess.run(["python", "updation.py","1","max","11",'No'])
except Exception as e:
    log_exceptions()
    subprocess.run(["python", "updation.py","1","max","9",'Yes'])
    subprocess.run(["python", "updation.py","1","max","11",'No'])
now = datetime.datetime.now()
subprocess.run(["python", "updation.py","1","max","6",str(now)])
