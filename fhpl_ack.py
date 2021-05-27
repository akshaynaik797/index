import datetime
import re
import subprocess
import sys

import pdftotext
import mysql.connector

from make_log import log_exceptions
from custom_parallel import write, conn_data
from custom_datadict import make_datadict
from custom_app import set_flag_row, create_settlement_folder

set_flag_row(sys.argv[9], 'E', sys.argv[7])


start = datetime.datetime.now()
with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('fhpl/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('fhpl/output.txt', 'r') as myfile:
    f = myfile.read()
try:
    datadict = make_datadict(f)
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
    if 'Authorization Letter' in f:
        data[3] = 'preauth'
    sender = ''
    if 'Cashless Claim settlement Letter' in data[4]:
        try:
            filepath = create_settlement_folder(data[6], data[2], data[5], data[0])
            with mysql.connector.connect(**conn_data) as con:
                cur = con.cursor()
                q = f"select sender from {data[6]}_mails where id=%s limit 1"
                cur.execute(q, (data[7],))
                r = cur.fetchone()
                if r is not None:
                    sender = r[0]
                q = f"insert into settlement_mails (`id`,`subject`,`date`,`sys_time`,`attach_path`,`completed`,`sender`,`hospital`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                data1 = (data[7], data[4], data[5], str(datetime.datetime.now()), filepath, '', sender, data[6])
                cur.execute(q, data1)
                set_flag_row(sys.argv[9], 'S', sys.argv[7])
        except:
            log_exceptions()
    else:
        write(data, sys.argv[9])
        set_flag_row(sys.argv[9], 'X', sys.argv[7])
except:
    log_exceptions()