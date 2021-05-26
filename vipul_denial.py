import datetime
import sys
import re

import pdftotext

from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions
from custom_app import set_flag_row

set_flag_row(sys.argv[9], 'E', sys.argv[7])

start = datetime.datetime.now()

with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('vipul/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('vipul/output.txt', 'r') as myfile:
    f = myfile.read()

try:
    # datadict = make_datadict(f)

    preid_val = r"^\S+$"
    pname_val = r"^[a-zA-Z.]+(?: [a-zA-Z.]+)*$"
    polno_val = r"^\S+$"
    memid_val = r"^\S+$"
    amount_val = r"^[\d.]+$"
    diagno_val = r"^\S+(?: \S+)*$"
    insname_val = r"^\S+(?: \S+){2,}$"
    doa_val = r"^\S+(?: \S+)*$"
    dod_val = r"^\S+(?: \S+)*$"
    corp_val = r"^\S+(?: \S+)*$"
    polhol_val = r"^[a-zA-Z.]+(?: [a-zA-Z.]+)*$"

    black_list = ['Details', 'Ltd', 'mpany Ltd,', 'or TPA reserves right to raise queries for any other']

    datadict = {}
    try:
        regexdict = {'preid': [[r"\S+(?=\n.*File No :)"], preid_val, [':', '.']],
                     'pname': [[r"(?<=Sub: Cashless Facility for).*"], pname_val, ['-', ':', 'MR.', 'Mr.']],
                     'polno': [[r"\S+(?=\n*.*Sub:)"], polno_val, [':', '.', '-', '(', ')']],
                     'memid': [[r"(?<=MAX BALAJI HOSPITAL)\s*\S+"], memid_val, [':', '-']],
                     'amount': [[r""], amount_val, ['(Rs)', '-', ':', 'Rs.', '/', ',', 'Rs', '(INR)']],
                     'diagno': [[r""], diagno_val, [':', '-']],
                     'insname': [[r""], insname_val, [':', '.', '-']],
                     'doa': [[r""], doa_val, [':', '000000']],
                     'dod': [[r""], dod_val, [':', '000000']],
                     'corp': [[r""], corp_val, [':', '-']],
                     'polhol': [[r""], polhol_val, ['-', ':', 'MR.', 'Mr.']], }

        for i in regexdict:
            for j in regexdict[i][0]:
                data = re.compile(j).search(f)
                if data is not None:
                    temp = data.group().strip()
                    for k in regexdict[i][2]:
                        temp = temp.replace(k, "")
                    temp = temp.strip()
                    if bool(re.compile(regexdict[i][1]).match(temp)):
                        if temp not in black_list:
                            datadict[i] = temp
                            break
                datadict[i] = ""
    except:
        log_exceptions()

    temp = re.compile(r"(?<=File No).*\n.*").search(f)
    if temp is not None:
        temp1 = temp.group().strip()
        preid = temp1.split(' ')[-1]
        datadict['preid'] = preid
    data = [i for i in sys.argv[1:9]]
    data2 = [datadict[i] for i in datadict]
    data.extend(data2)
    data3 = str(datadict)
    data.append(data3)
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
