import os
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


# added by ashish
with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('Universal_Sompo/output2.txt', 'w') as f:
    f.write(" ".join(pdf))     
with open('Universal_Sompo/output2.txt', 'r') as myfile:
    f = myfile.read()

# with open("132226_94518_ClaimRejection.pdf", "rb") as f:
#   pdf = pdftotext.PDF(f)

# with open('hdfc/output2.txt', 'w') as f:
#   f.write(" ".join(pdf))     
# with open('hdfc/output2.txt', 'r') as myfile:
#   f = myfile.read()


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