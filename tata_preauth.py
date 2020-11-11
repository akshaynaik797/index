import datetime
import re
import sys

import pdftotext

from make_log import log_exceptions
from mult1 import write

now = datetime.datetime.now()








with open(sys.argv[1], "rb") as f:
    pdf = pdftotext.PDF(f)

with open('tata/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('tata/output.txt', 'r') as myfile:
    f = myfile.read()
try:
    preid_reg_list = [r"", r"(?<=Claim Number).*(?=\()"]

    pname_reg_list = [r"", r"(?<=Patient Name).*(?=Age)"]

    polno_reg_list = [r"", r"(?<=Policy Number).*(?=Gender)"]

    memid_reg_list = [r"", r"(?<=Insurer Id of the Patient).*"]

    amount_reg_list = [r"", r"(?<=Total Authorized amount).*(?=\()"]

    diagno_reg_list = [r"", r"(?<=Provisional Diagnosis).*(?=Member)"]

    insname_reg_list = [r"", ]

    doa_reg_list = [r"", r"(?<=Expected Date of Admission).*"]

    dod_reg_list = [r"", r"(?<=Expected Date of Discharge).*"]

    corp_reg_list = [r"", ]

    polhol_reg_list = [r"", r"(?<=Proposer Name).*"]

    preid_val = r"^\S+$"
    pname_val = r"^[a-zA-Z.]+(?: [a-zA-Z.]+)*$"
    polno_val = r"^\S+$"
    memid_val = r"^\S+$"
    amount_val = r"^[\d.]+$"
    diagno_val = r"^\S+(?: \S+)*$"
    insname_val = r"^\S+(?: \S+){2,}$"
    doa_val = r"^\S+(?: \S+)*$"
    dod_val = r"^\S+(?: \S+)*$"
    corp_val = r"^\S+(?: \S+)*$"
    polhol_val = r"^[a-zA-Z.]+(?: [a-zA-Z.]+)*$"

    black_list = ['Details', 'Ltd', 'mpany Ltd,']

    datadict = {}
    regexdict = {'preid': [preid_reg_list, preid_val, [':', '.']],
                 'pname': [pname_reg_list, pname_val, ['-', ':', 'MR.', 'Mr.']],
                 'polno': [polno_reg_list, polno_val, [':', '.', '-', '(', ')']],
                 'memid': [memid_reg_list, memid_val, [':', '-']],
                 'amount': [amount_reg_list, amount_val, ['(Rs)', '-', ':', 'Rs.', '/', ',', 'Rs', '(INR)']],
                 'diagno': [diagno_reg_list, diagno_val, [':', '-']],
                 'insname': [insname_reg_list, insname_val, [':', '.', '-']],
                 'doa': [doa_reg_list, doa_val, [':', '000000']],
                 'dod': [dod_reg_list, dod_val, [':', '000000']],
                 'corp': [corp_reg_list, corp_val, [':', '-']],
                 'polhol': [polhol_reg_list, polhol_val, ['-', ':', 'MR.', 'Mr.']], }

    for i in regexdict:
        for j in regexdict[i][0]:
            data = re.compile(j).search(f)
            if data is not None:
                temp = data.group().strip()
                for k in regexdict[i][2]:
                    temp = temp.replace(k, "")
                temp = temp.strip()
                if bool(re.compile(regexdict[i][1]).match(temp)):
                    if temp not in black_list:
                        datadict[i] = temp
                        break
            datadict[i] = ""

    
    

    try:
        data = [i for i in sys.argv[1:]]
        data2 = [datadict[i] for i in datadict]
        data.extend(data2)
        data3 = str(datadict).replace('{', '\{').replace('}', '\}')
        data.append(data3)
        write(data)
        a = 1
        '''wbk= openpyxl.load_workbook(wbkName)
        s2=wbk.worksheets[1]
        s2.cell(row_count_1+1, column=11).value='YES'
        '''
        
    except Exception as e:
        log_exceptions()
        # s2.cell(row_count_1+1, column=11).value='NO'
        
except Exception as e:
    log_exceptions()
    # s2.cell(row_count_1+1, column=9).value='No'
    # s2.cell(row_count_1+1, column=11).value='NO'
    
    
now = datetime.datetime.now()
# s2.cell(row_count_1+1, column=6).value=now
# wbk.save(wbkName)

