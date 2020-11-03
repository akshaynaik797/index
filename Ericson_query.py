import datetime
import re
import subprocess
import sys

import pdftotext

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

with open('Ericson/output.txt', 'w', encoding="utf-8") as f:
    f.write(" ".join(pdf))
with open('Ericson/output.txt', 'r', encoding="utf-8") as myfile:
    f = myfile.read()
try:
    temp = re.compile(r"(?<=BALAJI MEDICAL AND DIAGNOSTIC RESEARCH CENTRE)( +\d+)( +\d+)").search(f)
    if temp is not None:
        preid, memid = temp.groups()
        preid, memid = preid.strip(), memid.strip()
    else:
        preid, memid = "", ""

    temp = re.compile(r"(?<=Sh./Smt./Kumar:).*(?=with)").search(f)
    if temp is not None:
        pname = temp.group().strip()
    else:
        pname = ""
    amount, status = "", 'Information Awaiting'
    subprocess.run(["python", "updation.py", "1", "max", "9", 'Yes'])
    subprocess.run(["python", "updation.py", "1", "max", "10", 'NA'])

    try:
        status = 'Approved'
        subprocess.run(["python", "test_api.py", preid, amount, "", '',
                        status, sys.argv[6], sys.argv[1], '', memid, pname])
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
