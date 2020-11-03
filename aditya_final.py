import datetime
import subprocess
import sys

import pdftotext

from custom_datadict import make_datadict
from make_log import log_exceptions

now = datetime.datetime.now()

subprocess.run(["python", "updation.py", "1", "max1", "1", sys.argv[2]])
subprocess.run(["python", "updation.py", "1", "max", "2", sys.argv[3]])
subprocess.run(["python", "updation.py", "1", "max", "3", sys.argv[4]])
subprocess.run(["python", "updation.py", "1", "max", "5", str(now)])
subprocess.run(["python", "updation.py", "1", "max", "7", sys.argv[5]])
subprocess.run(["python", "updation.py", "1", "max", "8", sys.argv[6]])

with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)
with open('aditya/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('aditya/output.txt', 'r') as myfile:
    f = myfile.read()
try:
    datadict = make_datadict(f)
    try:
        subprocess.run(
            ["python", "test_api.py", datadict['preid'], datadict['amount'], datadict['polno'], '',
             'Approved', sys.argv[6], sys.argv[1], '', datadict['memid'], datadict['pname']])
        subprocess.run(["python", "updation.py", "1", "max", "11", 'Yes'])
    except Exception as e:
        log_exceptions()
        subprocess.run(["python", "updation.py", "1", "max", "11", 'No'])
except Exception as e:
    log_exceptions()
    subprocess.run(["python", "updation.py", "1", "max", "9", 'Yes'])
    subprocess.run(["python", "updation.py", "1", "max", "11", 'No'])

now = datetime.datetime.now()
subprocess.run(["python", "updation.py", "1", "max", "6", str(now)])
