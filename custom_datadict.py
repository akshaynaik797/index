import re
from make_log import log_exceptions

preid_reg_list = [r"", r"(?<=Preauth Reference no).*", r"(?<=Claim number).*", r"(?<=Claim Number).*(?=\()",
                  r"(?<=Claim No).*(?=Date)"]
pname_reg_list = [r"", r"(?<=Patient Name).*(?=Age)", r"(?<=Patient Name).*", r"(?<=Name of Insured Patient).*(?=Age)",
                  r"(?<=Name of Insured-).*(?=Age)"]
polno_reg_list = [r"", r"(?<=Policy Number).*(?=Room)", r"(?<=Policy Number).*(?=Policy)", r"(?<=Policy Number).*(?=Expected)", r"(?<=Policy Number).*"]
memid_reg_list = [r"", r"(?<=Patient's Member UHID).*"]
amount_reg_list = [r"", r"(?<=Total Authorized amount).*", r"(?<=Approved amount).*", r"(?<=Approved Amount).*"]
diagno_reg_list = [r"", r"(?<=Ailment).*", r"(?<=Diagnosis).*", r"(?<=Diagnosis).*(?=\()"]
insname_reg_list = [r"", r"(?<=Name of Insurance Company).*", r"(?<=Insurer).*"]
doa_reg_list = [r"", r"(?<=Date of Admission).*", r"(?<=Date of admission).*(?=Diagnosis)", r"(?<=Date of admission).*"]
dod_reg_list = [r"", r"(?<=Date of Discharge).*", r"(?<=Date of discharge).*"]
corp_reg_list = [r"", ]
polhol_reg_list = [r"", r"(?<=Policy Holder).*", r"(?<=Primary Insured Name).*", r"(?<=Proposer Name).*"]

preid_val = r"^[\w-]+$"
pname_val = r"^[\w ]+$"
polno_val = r"^[\w\/-]+$"
memid_val = r"^[\w\/-]+$"
amount_val = r"^[\d.]+$"
diagno_val = r"^[\w \/]+$"
insname_val = r"^[\w ]+$"
doa_val = r"^[\w\/-]+$"
dod_val = r"^[\w\/-]+$"
corp_val = r"^\w+$"
polhol_val = r"^[\w ]+$"


def make_datadict(text_from_file):
    datadict = {}
    try:
        regexdict = {'preid': [preid_reg_list, preid_val, [':', '.']],
                     'pname': [pname_reg_list, pname_val, ['-', ':', 'MR.', 'Mr.']],
                     'polno': [polno_reg_list, polno_val, [':', ]],
                     'memid': [memid_reg_list, memid_val, [':', ]],
                     'amount': [amount_reg_list, amount_val, ['-', ':', 'Rs.']],
                     'diagno': [diagno_reg_list, diagno_val, [':', ]],
                     'insname': [insname_reg_list, insname_val, [':', '.']],
                     'doa': [doa_reg_list, doa_val, [':', '000000']],
                     'dod': [dod_reg_list, dod_val, [':', '000000']],
                     'corp': [corp_reg_list, corp_val, [':', ]],
                     'polhol': [polhol_reg_list, polhol_val, [':', ]], }

        for i in regexdict:
            for j in regexdict[i][0]:
                data = re.compile(j).search(text_from_file)
                if data is not None:
                    temp = data.group().strip()
                    for k in regexdict[i][2]:
                        temp = temp.replace(k, "")
                    temp = temp.strip()
                    if bool(re.compile(regexdict[i][1]).match(temp)):
                        datadict[i] = temp
                        break
                datadict[i] = ""
        return datadict
    except:
        log_exceptions()
        return datadict
