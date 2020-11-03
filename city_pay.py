import sqlite3
import subprocess
import sys
import re
import datetime
from dateutil import parser as date_parser
from custom_funct_city_pay import mail_body_to_text
now = datetime.datetime.now()
try:
    f= ''
    f = mail_body_to_text(sys.argv[5], sys.argv[7])
except Exception as e:
    pass
badchars = ('/',)
subprocess.run(["python", "updation.py","1","max1","1",sys.argv[2]])
subprocess.run(["python", "updation.py","1","max","2",sys.argv[3]])
subprocess.run(["python", "updation.py","1","max","3",sys.argv[4]])
subprocess.run(["python", "updation.py","1","max","5",str(now)])
subprocess.run(["python", "updation.py", "1", "max", "7", sys.argv[5]])
subprocess.run(["python", "updation.py", "1", "max", "8", sys.argv[6]])
if f!='':
    datadict = {}
    regexdict = {'transaction_reference': [r"(?<=Transaction Reference:).*"],
                 'payer_reference_no': [r"(?<=Reference No:).*"],
                 'payment_amount': [r"(?<=Payment Amount:).*"],
                 'payment_details': [r"(?<=Payment Details:)[\w\W]+(?=Kindly)"],
                 'nia_transaction_reference': [r"(?<=Payment Details: N)\d+"],
                 'claim_no': [r"(?<=CLAIM).*"],
                 'pname': [r".*(?=,ADMSN)"],
                 'adminssion_date': [r"(?<=ADMSN) ?\d+"],
                 'insurer_name': [r"(?<=behalf of).*"],
                 'tpa': [r"(?<=TPA-).*"],
                 'procesing_date': [r"(?<=Processing Date:).*"]}

    for i in regexdict:
        for j in regexdict[i]:
            data = re.compile(j).search(f)
            if data is not None:
                temp = data.group().strip()
                for k in badchars:
                    temp = temp.replace(k, "")
                datadict[i] = temp
                break
            datadict[i] = ""

    temp = re.compile(r"(?<=BCS_).*").search(sys.argv[5])
    if temp is None:
        datadict['advice_no'] = ""
    else:
        datadict['advice_no'] = temp.group()

    if datadict['adminssion_date'] != "":
        a = datadict['adminssion_date']
        a = date_parser.parse(a[0:2] + '/' + a[2:4] + '/' + a[4:])
        datadict['adminssion_date'] = a.strftime("%d-%b-%Y")

    data = (datadict['advice_no'],
            datadict['insurer_name'],
            datadict['transaction_reference'],
            datadict['payer_reference_no'],
            datadict['payment_amount'],
            datadict['procesing_date'],
            datadict['claim_no'],
            datadict['pname'],
            datadict['adminssion_date'],
            datadict['tpa'],
            datadict['payment_details'],
            datadict['nia_transaction_reference'])
    with sqlite3.connect("database1.db") as con:
        cur = con.cursor()
        sql = "insert into city_records values(?,?,?,?,?,?,?,?,?,?,?,?)"
        cur.execute(sql, data)

    subprocess.run(["python", "updation.py", "1", "max", "12", str(datadict)])
pass
