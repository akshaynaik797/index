import datetime
import sys
import re

import pdftotext

from bad_pdf import text_from_pdf
from custom_app import set_flag_row
from custom_datadict import make_datadict
from custom_parallel import write
from make_log import log_exceptions

# path = '/home/akshay/temp/20210110104258_abe28993-ad94-4787-a332-c4fa9fa5582c_Authorization_75757.pdf'
# with open(path, "rb") as f:
#     pdf = pdftotext.PDF(f)
#
# with open('/home/akshay/temp/output.txt', 'w') as f:
#     f.write(" ".join(pdf))
# with open('/home/akshay/temp/output.txt', 'r') as myfile:
#     f = myfile.read()
#
# text_from_pdf(path, '/home/akshay/temp/output.txt')
with open('/home/akshay/temp/output.txt', 'r') as myfile:
    f = myfile.read()

datadict = make_datadict(f)
temp = re.compile(r"(?<=sa)").search(f)
if temp is not None:
    preid = temp.group().strip()
pass