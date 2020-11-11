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
from custom_datadict import make_datadict
from custom_parallel import write

with open(sys.argv[1], "rb") as f:
	pdf = pdftotext.PDF(f)

# For Dennial pdf is written to output1.txt and for ack pdf is written to output.txt
with open('fgh/output1.txt', 'w', encoding='utf-8') as f:
	f.write(" ".join(pdf))     
with open('fgh/output1.txt', 'r', encoding='utf-8') as myfile:
 	f = myfile.read()

# with open('fgh/output.txt', 'w', encoding='utf-8') as f:
# 	f.write(" ".join(pdf))     
# with open('fgh/output.txt', 'r', encoding='utf-8') as myfile:
#  	f = myfile.read()

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