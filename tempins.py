import pdftotext
import re


fpath = "/home/akshay/Downloads/8_Query_EAL_SHANU_AHLUWALIA__1603192980_Query.pdf"
with open(fpath, "rb") as f:
    pdf = pdftotext.PDF(f)

with open('liberty/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('liberty/output.txt', 'r') as myfile:
    f = myfile.read()

preid_reg_list = [r"", r"(?<=Claim Number).*(?=Member)"]

pname_reg_list = [r"", r"(?<=Patient Name).*(?=Branch)"]

polno_reg_list = [r"", r"(?<=Policy Number).*"]

memid_reg_list = [r"", r"(?<=Member ID Number).*"]

amount_reg_list = [r"", r"(?<=Total Authorized amount).*(?=\()"]

diagno_reg_list = [r"", r"(?<=Provisional Diagnosis).*(?=Member)"]

insname_reg_list = [r"",]

doa_reg_list = [r"", r"(?<=Expected Date of Admission).*"]

dod_reg_list = [r"", r"(?<=Expected Date of Discharge).*"]

corp_reg_list = [r"",]

polhol_reg_list = [r"", r'(?<=Proposer / Insured"s Name).*']

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
pass
