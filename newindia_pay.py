import datetime
import re
import sys

import mysql.connector
import pdftotext
import tabula

from custom_datadict import make_datadict
from custom_parallel import conn_data, write
from make_log import log_exceptions
from custom_app import set_flag_row

set_flag_row(sys.argv[9], 'E', sys.argv[7])

try:
    mail_id = sys.argv[8]
    mail_date = sys.argv[6]
    fpath = sys.argv[1]

    start = now = datetime.datetime.now()
    try:
        with mysql.connector.connect(**conn_data) as conn:
            cur = conn.cursor()
            file = sys.argv[1]
            table = tabula.read_pdf(file, lattice=True, pages='all', pandas_options={'header': None})
            print(table[0])
            df = table[0]
            print(df.columns)
            tempDic = {}
            for i in range(len(df)):
                key = df.loc[i, 0]
                value = df.loc[i, 1]
                tempDic[key] = value

            refrenceNo = tempDic["Transaction Reference no"]

            with open(sys.argv[1], "rb") as f:
                pdf = pdftotext.PDF(f)

            with open('newIndia/output1.txt', 'w', encoding='utf-8') as f:
                f.write(" ".join(pdf))

            with open('newIndia/output1.txt', 'r', encoding='utf-8') as myfile:
                f = myfile.read()

            temp = re.compile(r"(?<=Amount).*").search(f)
            if temp is None:
                amount = ""
            else:
                amount = temp.group().replace(',', "").strip()

            w = f.find("on") + len('on')
            k = f[w:]
            u = k.find(".") + w
            g = f[w:u]
            g = g.strip()
            g = g.replace(',', '')
            date_time_obj = datetime.datetime.strptime(g, '%d %b %Y')
            mdate = str(date_time_obj.strftime("%d-%m-%Y"))
            print('Date:', mdate)

            # query = """insert into NIC(TPA_Name,Transaction_Reference_No,Amount,Date_on_attachment) values \
            # 	('%s','%s','%s','%s')""" %(tempDic['TPA Name'],tempDic['Transaction Reference no'],tempDic['Amount'],mdate)

            query = """insert into NIC(TPA_Name,Transaction_Reference_No,Amount,Date_on_attachment,MailId,Date_Of_Mail,Amount_In_Mail, hospital) values \
                ('%s','%s','%s','%s','%s','%s','%s','%s')""" % (
            tempDic['TPA Name'], tempDic['Transaction Reference no'], tempDic['Amount'], mdate, mail_id, mail_date,
            amount, sys.argv[7])

            print(query)
            cur.execute(query)
            conn.commit()

            table = tabula.read_pdf(file, lattice=True, pages='all')
            # print(table[1])
            df = table[1]
            newcoldic = {}
            colList = []
            for col in df.columns:
                col1 = col.replace('\r', ' ')
                newcoldic[col] = col1
                colList.append(col1)

            df = table[1]
            df1 = df.rename(columns=newcoldic, inplace=False)
            print(df1.columns)
            for i in range(len(df1)):
                policyNo = df1.loc[i, "Policy Number"]
                claimNo = df1.loc[i, "Claim Number"]
                tpa = claimNo[0:5]
                patientName = df1.loc[i, "Name of Patient"]
                grossAmount = df1.loc[i, "Gross Amount"]
                tdsAmount = df1.loc[i, "TDS Amount"]
                netAmount = df1.loc[i, "Net Amount"]
                query = """insert into NIC_Records(Transaction_Reference_No,Policy_Number,Claim_Number,Name_Of_Patient,Gross_Amounts,tds,Net_Amount,tpa_No, hospital) values \
                ('%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (
                refrenceNo, policyNo, claimNo, patientName, grossAmount, tdsAmount, netAmount, tpa, sys.argv[7])
                print(query)
                cur.execute(query)
                conn.commit()

        if len(table) > 2:
            df = table[2]
        if len(table[2].columns) == len(table[1].columns):
            tempDic = {}
            tempDic1 = {}
            i = 0
            for col in df.columns:
                tempDic[colList[i]] = col
                tempDic1[col] = colList[i]
                i = i + 1
            df2 = df.rename(columns=tempDic1, inplace=False)
            df1 = df2.append(tempDic, ignore_index=True)
            print(df1)

            with mysql.connector.connect(**conn_data) as conn:
                cur = conn.cursor()
                for i in range(len(df1)):
                    policyNo = df1.loc[i, "Policy Number"]
                    claimNo = df1.loc[i, "Claim Number"]
                    tpa = claimNo[0:5]
                    patientName = df1.loc[i, "Name of Patient"]
                    grossAmount = df1.loc[i, "Gross Amount"]
                    tdsAmount = df1.loc[i, "TDS Amount"]
                    netAmount = df1.loc[i, "Net Amount"]
                    query = """insert into NIC_Records(Transaction_Reference_No,Policy_Number,Claim_Number,Name_Of_Patient,Gross_Amounts,tds,Net_Amount,tpa_No,hospital) values \
                    ('%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (
                    refrenceNo, policyNo, claimNo, patientName, grossAmount, tdsAmount, netAmount, tpa, sys.argv[7])
                    print(query)
                    cur.execute(query)
                    conn.commit()
    except Exception as e:
        log_exceptions()
        print(e.__str__())
    now = datetime.datetime.now()
    f = ''
    datadict = make_datadict(f)
    data = [i for i in sys.argv[1:9]]
    data2 = [datadict[i] for i in datadict]
    data.extend(data2)
    data3 = str(datadict)
    data.append(datadict)
    end = datetime.datetime.now()
    data.append(str(start))
    data.append(str(end))
    diff = end - start
    diff = str(diff.total_seconds())
    data.append(diff)
    write(data, sys.argv[9])
    set_flag_row(sys.argv[9], 'X', sys.argv[7])

except:
    log_exceptions()
    pass
