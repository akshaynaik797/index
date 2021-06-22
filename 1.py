#######################
import pdftotext
import re

from bad_pdf import text_from_pdf
from custom_datadict import make_datadict
fpath = '/home/akshay/Downloads/7175_Claim_Authorization_Letter_4172380.pdf'
with open(fpath, "rb") as f:
    pdf = pdftotext.PDF(f)
with open('fhpl/output1.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('fhpl/output1.txt', 'r') as myfile:
    f = myfile.read()

# text_from_pdf(fpath, 'aditya/output1.txt')
# with open('aditya/output1.txt', 'r') as myfile:
#     f = myfile.read()

data = make_datadict(f)
if tmp := re.search(r"(?<=Details of Approval for Cashless Request are given below:\n).*", f):
    tmp = tmp.group().replace('RS.', '').strip()
    try:
        data['amount'] = re.split(r" +", tmp)[1]
    except:
        pass

pass
