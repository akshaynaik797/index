import os
import re
import sys
import struct, time
import subprocess
from datetime import date
import datetime
import openpyxl
import pdftotext
import time
import requests

from make_log import log_exceptions
from custom_parallel import write
from custom_datadict import make_datadict

with open(sys.argv[1], "rb") as f:
	pdf = pdftotext.PDF(f)

with open('safeway/output.txt', 'w') as f:
	f.write(" ".join(pdf))     
with open('safeway/output.txt', 'r') as myfile:
 	f = myfile.read()

try:
    datadict = make_datadict(f)
    data = [i for i in sys.argv[1:]]
    data2 = [datadict[i] for i in datadict]
    data.extend(data2)
    data3 = str(datadict).replace('{', '\{').replace('}', '\}')
    data.append(data3)
    write(data)
except:
    log_exceptions()