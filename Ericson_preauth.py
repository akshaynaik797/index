import datetime
import re
import subprocess
import sys

import pdftotext

from make_log import log_exceptions
from patient_name_fun import pname_fun

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
    badchars = ('/', ',', ':', '-')
    datadict = {}
    regexdict = {'preid': [r"(?<=Claim number).*(?=\(Please)"],
                 'amount': [r"(?<=Total Authorised Amount).*"],
                 'memid': [r"(?<=ID/TPA/insurer Id of the Patient).*"],
                 'polno': [r"(?<=Policy Number).*(?=Expected)"]
                 }
    for i in regexdict:
        for j in regexdict[i]:
            data = re.compile(j).search(f)
            if data is not None:
                temp = data.group().strip()
                for k in badchars:
                    temp = temp.replace(k, "")
                datadict[i] = temp.strip()
                break
            datadict[i] = ""
    hg = datadict
    subprocess.run(["python", "updation.py", "1", "max", "9", 'Yes'])
    subprocess.run(["python", "updation.py", "1", "max", "10", 'NA'])
    regex_list = [r"(?<=Patient Name).*(?=Age)"]
    pname = pname_fun(f, regex_list)

    try:
        status = 'Approved'
        subprocess.run(["python", "test_api.py", hg["preid"], hg["amount"], hg["polno"], ' ',
                        status, sys.argv[6], sys.argv[1], ' ', hg["memid"], pname])
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
