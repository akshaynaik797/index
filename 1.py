#######################
import pdftotext

from bad_pdf import text_from_pdf
from custom_datadict import make_datadict
fpath = '/home/akshay/temp/eastwest/attachments_pdf_preauth/authletter_702783_124833_11034.pdf'
with open(fpath, "rb") as f:
    pdf = pdftotext.PDF(f)
with open('aditya/output1.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('aditya/output1.txt', 'r') as myfile:
    f = myfile.read()

# text_from_pdf(fpath, 'aditya/output1.txt')
# with open('aditya/output1.txt', 'r') as myfile:
#     f = myfile.read()

data = make_datadict(f)
pass
