import datetime
import re
import sys

import pdftotext

from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions
from custom_app import set_flag_row
try:
    set_flag_row(sys.argv[9], 'E', sys.argv[7])

    start = now = datetime.datetime.now()
    with open(sys.argv[1], "rb") as f:
        pdf = pdftotext.PDF(f)

    with open('Park/output.txt', 'w') as f:
        f.write(" ".join(pdf))
    with open('Park/output.txt', 'r') as myfile:
        f = myfile.read()

    datadict = make_datadict(f)
    status = ''
    if "Authorisation For the Cashless request for Hospitalisation" in f:
        result = re.compile(r"(?<=Authorisation No:).*").search(f)
        if result is not None:
            preid = result.group().strip()
            preid = preid.replace(' ', '')
            datadict['preid'] = preid
        status = 'Approved'
    else:
        result = re.compile(r"(?<=Ref No-).*").search(f)
        if result is not None:
            preid = result.group().strip()
            preid = preid.replace(' ', '')
            datadict['preid'] = preid
        result = re.compile(r"(?<=Patient:-).*").search(f)
        if result is not None:
            pname = result.group().strip()
            pname = pname.replace(' ', '')
            datadict['pname'] = pname
        status = 'Information Awaiting'
    sys.argv[4] = sys.argv[4] + ',' + status
    # datadict['status'] = status
    data = [i for i in sys.argv[1:9]]
    datadict['insname'] = ''
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
    if 'Welcome' not in sys.argv[5] or 'your claim has been settled for' not in sys.argv[5]:
        write(data, sys.argv[9])
    set_flag_row(sys.argv[9], 'X', sys.argv[7])
except:
    log_exceptions()
