import datetime
import sys
import re

import pdftotext

from custom_app import set_flag_graphapi
from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions

set_flag_graphapi(sys.argv[5], sys.argv[6], 'E',sys.argv[7])

start = datetime.datetime.now()
with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('bajaj/output.txt', 'w', encoding='utf-8') as f:
    f.write(" ".join(pdf))
with open('bajaj/output.txt', 'r', encoding='utf-8') as myfile:
    f = myfile.read()

try:
    subject = sys.argv[5]
    datadict = make_datadict(f)
    pattern = r"(?P<polno>(?<=Policy No).*?(?=ID Card No))(?:.*)(?P<memid>(?<=ID Card No).*?(?=Ptn Name))(?:.*)(?P<pname>(?<=Ptn Name).*?(?=Claim ID))(?:.*)(?P<preid>(?<=Claim ID).*?(?=cashless))"
    if tmp := re.search(pattern, subject):
        tmp = tmp.groupdict()
        for k, v in tmp.items():
            tmp[k] = v.replace(':', '').strip()
        for i, j in zip(datadict, tmp):
            datadict[j] = tmp[j]
    if datadict['amount'] == "":
        try:
            from word2number import w2n
            if tmp := re.search(r"(?<=Total Authorized amount).*", f):
                tmp = tmp.group().replace(':', '').strip()
                datadict['amount'] = str(w2n.word_to_num(tmp))
        except:
            pass
    data = [i for i in sys.argv[1:]]
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
    ####for test purpose
    # write(data)
    # set_flag_graphapi(sys.argv[5], sys.argv[6], 'X',sys.argv[7])

except:
    log_exceptions()