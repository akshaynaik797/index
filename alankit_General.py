import pdfkit
import os
import sys
import re
import struct, time
import subprocess
from datetime import date
import datetime
import openpyxl
import pdftotext
import time
import requests
import html2text
from make_log import log_exceptions
now = datetime.datetime.now()
try:
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    # config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
    subprocess.run(["python", "updation.py","1","max1","1",sys.argv[2]])
    subprocess.run(["python", "updation.py","1","max","2",sys.argv[3]])
    subprocess.run(["python", "updation.py","1","max","3",sys.argv[4]])
    subprocess.run(["python", "updation.py","1","max","5",str(now)])
    subprocess.run(["python", "updation.py","1","max","7",sys.argv[5]])
    subprocess.run(["python", "updation.py","1","max","8",sys.argv[6]])

    pdfkit.from_file(sys.argv[1], 'alankit/out.pdf', configuration=config)
    with open('alankit/out.pdf', "rb") as f:
        pdf = pdftotext.PDF(f)
    with open('alankit/output.txt', 'w') as f:
        f.write(" ".join(pdf))
    with open('alankit/output.txt', 'r') as myfile:
        f = myfile.read()

    if 'Query' in sys.argv[1] or 'Denial' in sys.argv[1]:
        badchars = ('/', ',', ':', '-')
        datadict = {}
        regexdict = {'preid': [r"(?<=Our CCN.).*", r"(?<=CCN:)[ \w-]+"]}

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
        if 'Query' in sys.argv[1]:
            status = 'Information Awaiting'
        else:
            status = 'Denial'
        subprocess.run(["python", "updation.py", "1", "max", "9", 'Yes'])
        subprocess.run(["python", "updation.py", "1", "max", "10", 'NA'])
        try:
            subprocess.run(
                ["python", "test_api.py", datadict['preid'], ' ', ' ', ' ', status, sys.argv[6], sys.argv[1], ' ', ' ',
                 ' '])
            subprocess.run(["python", "updation.py", "1", "max", "11", 'Yes'])
        except Exception as e:
            subprocess.run(["python", "updation.py", "1", "max", "11", 'No'])

    elif 'ADDITIONAL AUTHORISED' in sys.argv[1] or 'Authorised' in sys.argv[1]:
        badchars = ('/', ',', ':', '-')
        datadict = {}
        regexdict = {'preid': [r"(?<=Claim Control No :)[\w -]+"],
                     'amount': [r"\d+(?=\r?\nRoom rent)"],
                     'mem_id': [r"\w+(?=\r?\nProvisional Diagnosis )"],
                     'pol_no': [r"[\w \/]+(?=AITL ID Card No.)"],
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
        a = 1
        subprocess.run(["python", "updation.py", "1", "max", "9", 'Yes'])
        subprocess.run(["python", "updation.py", "1", "max", "10", 'NA'])
        status = 'Approved'
        try:
            subprocess.run(
                ["python", "test_api.py", datadict['preid'], datadict['amount'], datadict['pol_no'], ' ', status, sys.argv[6], sys.argv[1], ' ',
                 datadict['mem_id']])
            subprocess.run(["python", "updation.py", "1", "max", "11", 'Yes'])
        except Exception as e:
            subprocess.run(["python", "updation.py", "1", "max", "11", 'No'])
except:
    log_exceptions()