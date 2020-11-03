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

with open('fhpl/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('fhpl/output.txt', 'r') as myfile:
    f = myfile.read()
try:

    badchars = (',', ':', '-', '\r', '\n', '  ', '­')
    datadict = {}
    regexdict = {'preid': [r"(?<=AL No.:).*", r"(?<=Preauthorization Num ber).*(?=,)",
                           r"(?<=Preauthorization Number).*(?=,)", r"(?<=Claim No.:).*"],
                 'pname': [r"(?<=Patient Name).*(?=Corporate Name)", r"(?<=Patient Nam e).*(?=Age)",
                           r"(?<=Patient Name).*(?=Age)", r"(?<=Patient Name).*", ],
                 'memid': [r"(?<=UHID No:).*", r"(?<=UHID).*"],
                 'polno': [r'(?<=Policy No.:).*(?=Claim)', r"(?<=Policy No.:).*(?=AL No.:)"]}

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
    a = 1

    subprocess.run(["python", "updation.py", "1", "max", "9", 'Yes'])
    subprocess.run(["python", "updation.py", "1", "max", "10", 'NA'])
    try:

        subprocess.run(
            ["python", "test_api.py", datadict['preid'], '', datadict['polno'], '', 'Acknowledgement', sys.argv[6], sys.argv[1], '', datadict["memid"], datadict["pname"]])

        subprocess.run(["python", "updation.py", "1", "max", "11", 'Yes'])
    except Exception as e:
        log_exceptions()
        # s2.cell(row_count_1+1, column=11).value='NO'
        subprocess.run(["python", "updation.py", "1", "max", "11", 'No'])
except Exception as e:
    log_exceptions()
    # s2.cell(row_count_1+1, column=9).value='No'
    # s2.cell(row_count_1+1, column=11).value='NO'
    subprocess.run(["python", "updation.py", "1", "max", "9", 'Yes'])
    subprocess.run(["python", "updation.py", "1", "max", "11", 'No'])
now = datetime.datetime.now()
# s2.cell(row_count_1+1, column=6).value=now
# wbk.save(wbkName)
subprocess.run(["python", "updation.py", "1", "max", "6", str(now)])
