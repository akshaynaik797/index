import re
from make_log import log_exceptions

preid_reg_list = [r"(?<=Claim Number).*(?=\(0)", r"(?<=Claim Number).*", r"(?<=Preauth Reference no).*",
                  r"(?<=Claim number).*", r"(?<=Claim Number).*(?=\()", r"(?<=CCN).*(?=MDI ID No)",
                  r"(?<=Claim No).*(?=Date)", r"(?<=CCN).*", r"(?<=Claim No).*", r"(?<=Claim No:)\S+",
                  r"(?<=Preauthorization Num ber).*(?=,)", r"(?<=Claim ID).*(?=UHID)", r"(?<=Claim ID).*",
                  r"(?<=CCN).*", r"(?<=Claim Number).*", r"(?<=claim no)\s+\S+",
                  r"(?<=AL Number).*", r"(?<=cashless request ID).*?(?=dated)"
                  r"(?<=Incidence no).*", r"(?<=Cashless Authorization no).*(?=under Policy)", r"(?<=Customer ID).*",
                  r"(?<=CCN Number).*", r"(?<=File No.).*", r"(?<=CLAIM NUMBER).*", r"(?<=FIR NO).*", r"(?<=AL No).*",
                  r"(?<=Claim Number AL).*(?=\()", r"(?<=Claim no).*(?=\()", r"(?<=UHC CASE ID).*",
                  r"(?<=Claim Registration Number).*", r"(?<=Claim Number).*(?=Date)", r"(?<=Preauth ID).*",
                  r"(?<=FIR No).*", r"(?<=Claim Control No).*", r"(?<=Cashless Authorization No).*(?=\.)",
                  r"(?<=Claim Incident).*", r"(?<=Claim number).*(?=\()", r"(?<=CCN No).*",
                  r"(?<=refer the Pre-Auth Number).*(?=in your)", r"(?<=Cashless Claim Reference Number:).*",
                  r"(?<=Cashless Authorization Letter).*", r"(?<=Our CCN.).*", r"(?<=CCN:)[ \w-]+",
                  r"(?<=Claim Control No :)[\w -]+", r"(?<=Preauthorization Number).*(?=,)", "(?<=GXL No.).*",
                  r"(?<=SHORTFALL No\.).*(?=-)", r"(?<=SHORTFALL No.).*", r"(?<=Claim).*",
                  r"(?<=Claim No:).*(?=\(Please)", r"(?<=Claim Control Number).*", r"(?<=PA.No).*"]

pname_reg_list = [r"(?<=Patient Name).*(?=Age)", r"(?<=Patient Name).*", r"(?<=Name of Insured Patient).*(?=Age)",
                  r"(?<=Name of Insured-).*(?=Age)", r"(?<=Name Of Patient).*(?=AL)", r"(?<=Patient Name =:).*",
                  r"(?<=Name of Patient).*(?=Membership)", r"(?<=Patient Nam e).*(?=, Age)",
                  r"(?<=Patient Name).*(?=Patient)", r"(?<=Patient's Name).*", r"(?<=hospitalization of).*(?=with)",
                  r"(?<=Claim of).*", r"(?<=Name of the Patient).*(?=Policy)", r"",
                  r"(?<=PATIENT NAME AND).*\n.*(?=-)",r"(?<=PATIENT NAME).*",
                  r"(?<=of).*(?=Member ID)", r"(?<=TRUST\) Name).*", r"(?<=cashless benefit for Patient).*",
                  r"(?<=PATIENT NAME AND RELATION).*(?=-)", r"(?<=Claimant Name).*", r"(?<=Denial of Pre-Auth for).*",
                  r"(?<=your Pre-authorization request for).*(?=and on)", r"(?<=Approval for Claim of).*(?=\()",
                  r"(?<=Subject: Cashless Denial Of:).*(?=with Card)", r"(?<=PATIENT NAME).*(?=-)",
                  r"(?<=Name of the patient).*", r"(?<=of).*(?=, *MemberID)", r"(?<=preauth request for).*(?=and it is being)",
                  r"(?<=PATIENT NAME & RELATION).*(?=-)", r"(?<=Cashless Request for Patient).*(?=is Approved)",
                  r"(?<=Rejection of Cashless Claim facility for).*(?=at)", r"(?<=Patient Name).*(?=and)",
                  r"(?<=information required for cashless claim facility for).*(?=at)", r"(?<=Patient Name).*(?=Policy No:)",
                  r"(?<=Patient Name).*(?=Hospitalized at)", r"[\w ]+\n(?=Patient)", r"(?<=Patient Name).*(?=\()",
                  r"(?<=regarding Hospitalization of).*(?=with claim no)", r"(?<=Patient).*(?=to hospital.)",
                  r"(?<=Name of the patient).*(?=UHID)"]

polno_reg_list = [r"(?<=Policy No).*", r"(?<=Policy Number).*(?=Room)", r"(?<=Policy Number).*(?=Policy)",
                  r"(?<=Policy Number).*(?=Expected)", r"(?<=Policy Number).*", r"(?<=Policy No).*(?=Date)",
                  r"(?<=Policy No).*(?=Expected)", r"(?<=Policy No).*(?=Policy)", r"(?<=Policy Number).*(?=Gender)",
                  r"(?<=Policy No).*", r"(?<=Policy number).*(?=Expected)",
                  r"(?<=Agent\/Dev Off:)\r?\n\s+\S+", r"(?<=policy no)\s+\S+", r"(?<=Policy No).*(?=Network)",
                  r"(?<=POLICY NO).*", r"(?<=Hospitalisation under Policy number).*",
                  r"(?<=Hospitalisation under Policy No).*",
                  r"(?<=under Policy)\s+\S+", r"(?<=Policy Number).*(?=Claim No)",
                  r"(?<=Policy Number).*(?=Date of Admission)", r"(?<=POLICY NUMBER).*",
                  r"(?<=under your policy).*(?=as per below)", r"(?<=Policy).*(?=of)", r"[\w \/]+(?=AITL ID Card No.)"]

memid_reg_list = [r"(?<=Insurer Id of the Patient).*", r"(?<=Patient's Member UHID).*",
                  r"(?<=Membership no).*(?=Employee)", r"(?<=Membership No).*",
                  r"(?<=Member ID Number).*", r"(?<=Member ID Card No).*(?=Expected)", r"(?<=UHID No).*",
                  r"(?<=Patient CardId).*", r"(?<=Patient GHID).*", r"(?<=Patient's Member).*", r"(?<=HDFC ERGO ID).*",
                  r"(?<=HI Id No.).*", r"(?<=Member ID No.).*", r"(?<=Patient’s Member UHID).*", r"(?<=UHID)\s+\d+",
                  r"(?<=UHID Number).*(?=Co-Pay)", r"(?<=MEMBER ID).*", r"(?<=, Member ID).*",
                  r"(?<=ID/TPA/Insurer Id of the Patient).*", r"(?<=MDID Number).*", r"(?<=MDI ID No.).*",
                  r"(?<=MDID Number).*(?=Claim Number)", r"(?<=Medi Assist ID).*", r"(?<=Card No.).*",
                  r"(?<=TPA MEMBERSHIP ID).*", r"(?<=PHS ID).*", r"(?<=ID/TPA/Insured Id of the Patient).*",
                  r"(?<=Member ID).*(?=Provisional Diagnosis)", r"(?<=Patient's Member ID).*",
                  r"(?<=PHS ID).*(?=has been)", r"(?<=Card no.).*", r"(?<=Patient Card ID).*",
                  r"(?<=ID Card \().*(?=\))", r"(?<=MemberID:).*", r"(?<=Member Code).*",
                  r"(?<=ID/TPA/insurer Id of the Patient).*", r"\w+(?=\r?\nProvisional Diagnosis )",
                  r"(?<=Patient Card Number:).*(?=Proposed)"]

amount_reg_list = [r"(?<=Total Authorized amount).*", r"(?<=Approved amount).*", r"(?<=Approved Amount).*",
                   r"(?<=Total Authorized Amount).*(?=\/)", r"(?<=NET Approved Amount)\S+\s+\S+",
                   r"(?<=Total Authorized amount).*(?=\()", r"\S+\r?\n.*(?=Amount to be paid by lnsured)",
                   r"(?<=Total Authorized Amount).*", r"(?<=We hereby authorize and guarantee for payment of Rs)\s+\S+",
                   r"(?<=the authorization amount approved is Rs.)\s+\S+", r"(?<=Total Authorised Amount).*",
                   r"(?<=amount upto and not excedding Rs.)\s*\S+", r"(?<=Approved Amont).*",
                   r"(?<=TOAL SANCTIONED AMOUNT).*", r"(?<=TOTAL AL ISSUED).*", r"(?<=NET Approved)\s*\S+",
                   r"\d+(?=\r?\nRoom rent)", r"(?<=Further guarantee of payment up to).*(?=\(Rs.)",
                   r"(?<=Initial Approval Amount).*(?=\()",
                   r"(?<=We hereby Authorize and Guarantee a Payment of Rs.).*(?=/-)",
                   r"(?<=We hereby authorize and guarantee for payment up to Rs.).*(?=,)",
                   r"(?<=Total Authorized).*(?=\()", r"(?<=additional amount of Rs.).*(?=/-)",
                   r"(?<=Authorized Amount).*", r"(?<=Final limit Enhanced to).*(?=after)"]

diagno_reg_list = [r"", r"(?<=Ailment).*", r"(?<=Diagnosis).*", r"(?<=Diagnosis).*(?=\()",
                   r"(?<=Diagnosis & Proposed).*", r"(?<=Diagnosis).*(?=Proposed)", r"(?<=Provisional diagnosis).*",
                   r"(?<=Provisional Diagnosis).*(?=Sub Limit)", r"(?<=Diagnos is).*(?=Treatment)",
                   r"(?<=Illness Details).*", r"(?<=DIAGNOSIS).*", r"(?<=Provisional Diagnosis/Ailment).*(?=Status)"]

insname_reg_list = [r"(?<=Insurance Co).*", r"(?<=Name of Insurance Co.).*", r"(?<=Name of Insurance Company).*",
                    r"(?<=Name of InsuranceCompany).*", r"(?<=Insurer).*",
                    r"(?<=of Insurance com pany).*", r"(?<=Insurer Name).*", r"(?<=Insurance Company).*",
                    r"(?<=Insurance Co).*(?=\()", r"(?<=INSURANCE COMPANY).*", r"(?<=INSURER :).*"]

doa_reg_list = [r"(?<=Date of Admission).*", r"(?<=Date of admission).*(?=Diagnosis)",
                r"(?<=Date of admission).*", r"(?<=Expected Admission Date).*", r"(?<=Expected Date of Admission).*",
                r"(?<=Date of Admission).*(?=Date of Discharge)", r"(?<=Probable DOA).*(?=&)",
                r"(?<=DATE OF ADMISSION).*", r"(?<=Date Of Admission).*(?=Date)", r"(?<=Expected Date Of Admission).*",
                r"(?<=Admission Date).*", r"(?<=Date of Admission).*(?=Copay)"]

dod_reg_list = [r"(?<=Date of Discharge).*", r"(?<=Date of discharge).*", r"(?<=Date Of D ischarge).*",
                r"(?<=Date of Admission).*(?=Relationship)", r"(?<=Expected Discharge Date).*",
                r"(?<=Expected Date of Discharge).*", r"(?<=Probable DOD).*"]

corp_reg_list = [r"", r"(?<=of Corporate).*(?=:)", r"(?<=Corporate Name).*(?=:)", r"(?<=Corporate Name).*",
                 r"(?<=Corporate/Product Name).*", r"(?<=Group Name).*", r"(?<=CORPORATE).*", r"(?<=CORPORATE NAME).*"]

polhol_reg_list = [r"", r"(?<=Policy Holder).*", r"(?<=Primary Insured Name).*", r"(?<=Proposer Name).*",
                   r"(?<=Name Of the Insured).*(?=Claim)", r"(?<=Name Of Insured).*(?=Claim)",
                   r"(?<=Insured’s Name).*", r"(?<=Emp/Member Name &).*(?=&)", r"(?<=Policy Holder Name).*",
                   r"(?<=Insured Name).*", r"(?<=Empl Name \/ ID).*(?=\/)", r"(?<=Employee / Insured).*",
                   r"(?<=Employee Name).*", r"(?<=Proposer Name).*(?=Hospital)", r"(?<=Insured Name).*(?=Patient Name)",
                   r"(?<=INSURED NAME).*", r"(?<=EMPLOYEE NAME).*", r"(?<=Policy Holder Name).*(?=Policy)",
                   r"(?<=INSURED NAME).*(?=-)"]

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


black_list = ['Details', 'Ltd', 'mpany Ltd,', 'or TPA reserves right to raise queries for any other']

def make_datadict(text_from_file):
    datadict = {}
    try:
        regexdict = {'preid': [preid_reg_list, preid_val, [':', '.', '(', ')', 'and']],
                     'pname': [pname_reg_list, pname_val, ['-', ':', 'MR.', 'Mr.', ',', 'B/O', '—']],
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
                data = re.compile(j).search(text_from_file)
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
        return datadict
    except:
        log_exceptions()
        return datadict
