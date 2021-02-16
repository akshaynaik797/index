import re
import subprocess

import mysql.connector
import pandas as pd
import pdfplumber

from custom_parallel import conn_data
from make_log import log_exceptions

def param():
    with mysql.connector.connect(**conn_data) as con:
        df = pd.read_sql_query("SELECT * from pdf_lables", con)
        return df

def get_pdf_ins_process(current_pdf_file):
    d = {'status': 'fail',
         'insurer': "",
         'process': ""}
    json_data = param()
    Insurance_company = json_data['ins']
    Process = json_data['process']
    Insurance_company_label_1 = json_data['ins_pdf']
    Process_label_2 = json_data['process_pdf']
    p1, p2 = "", ""
    with pdfplumber.open(current_pdf_file) as my_pdf:
        pages = my_pdf.pages
        res1 = []
        for i, pg in enumerate(pages):
            tbl = [pages[i].extract_text()]
            test = [tbl[0]]
            for sub in test:
                res1.append(re.sub('\n', ' ', sub))
            res = ' '.join(res1)
            for i, j in zip(Insurance_company_label_1, Process_label_2):
                if len(i) > 0:
                    if str(i) in res:
                        p1 = i
                        if len(j) > 0:
                            if str(j) in res:
                                p2 = j
    try:
        l2 = (json_data['process_pdf'].str.contains(p2))
    except:
        p2 = 'not defined'
        l2 = (json_data['process_pdf'].str.contains(p2))
    try:
        l1 = (json_data['ins_pdf'].str.contains(p1))
    except:
        p1 = 'not defined'
        l1 = (json_data['ins_pdf'].str.contains(p1))

    locate = json_data[l2 & l1]['process']
    p2 = locate.to_string(index=False)
    if '\n' in p2:
        p2 = p2.split('\n')[0]
    if p2 == 'Series([], )':
        p2 = 'not defined'
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select ins, process from pdf_lables where ins_pdf=%s and process=%s limit 1"
        cur.execute(q, (p1, p2))
        result = cur.fetchone()
        if result is not None:
            d = {'status': 'success',
                 'insurer': result[0],
                 'process': result[1]}
    return d

def process_p_flag_mails():
    mails_dict = {}
    fields = ("id","subject","date","sys_time","attach_path","completed","sender","sno","folder","process")
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select table_name, batch_size, sno from p_flag_process_tables where active=1"
        cur.execute(q)
        result = cur.fetchall()
        for table, batch, sno in result:
            q = f"select * from {table} where completed='p' and sno > {sno} order by sno desc limit {batch}"
            cur.execute(q)
            records = []
            result1 = cur.fetchall()
            for i in result1:
                t = {}
                for k, v in zip(fields, i):
                    t[k] = v
                records.append(t)
            mails_dict[table] = records
    for hosp in mails_dict:
        for row in mails_dict[hosp]:
            try:
                row_count_1 = 1
                filepath = row['attach_path']
                temp = get_pdf_ins_process(filepath)
                ins, ct = temp['insurer'], temp['process']
                subject, l_time, hid, mail_id = row['subject'], row['date'], hosp, row['id']
                subject = subject + '_' + mail_id
                if '_' in hid:
                    hid = hid.split('_')[0]
                if ins != '' and ct != '':
                    subprocess.run(
                        ["python", ins + "_" + ct + ".py", filepath, str(row_count_1), ins, ct, subject, l_time, hid,
                         mail_id])
                    with mysql.connector.connect(**conn_data) as con:
                        cur = con.cursor()
                        q = f"update {hosp} set completed = 'DDD' where id=%s"
                        cur.execute(q, (mail_id,))
                        con.commit()
            except:
                log_exceptions(row=row)
if __name__ == '__main__':
    #get p flag mails
    #process
    #subject as subject+id
    #save in updation
    #change flag to X
    process_p_flag_mails()
    pass