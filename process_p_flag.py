import re
import subprocess
from datetime import datetime

import mysql.connector
import pandas as pd
import pdftotext

from custom_app import change_active_flag_mail_storage_tables
from custom_parallel import conn_data
from make_log import log_exceptions

hosp_dict = {
            'graphApi': 'Max PPT',
            'inamdar_mails': 'inamdar',
            'noble_mails': 'noble',
            'ils_mails': 'ils',
            'ils_howrah_mails': 'ils_howrah',
            'ils_agartala_mails': 'ils_agartala',
            'ils_dumdum_mails': 'ils_dumdum'
        }


tconn_data = {'host': "database-iclaim.caq5osti8c47.ap-south-1.rds.amazonaws.com",
             'user': "admin",
             'password': "Welcome1!",
             'database': 'portals'}

def param():
    with mysql.connector.connect(**tconn_data) as con:
        df = pd.read_sql_query("SELECT * from paraClassification", con)
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
    with open(current_pdf_file, "rb") as f:
        pdf = pdftotext.PDF(f)
        res = " ".join(pdf)
        for i, j in zip(Insurance_company_label_1, Process_label_2):
            if len(i) > 0:
                if str(i) in res:
                    p1 = i
                    if len(j) > 0:
                        if str(j) in res:
                            p2 = j
    with mysql.connector.connect(**tconn_data) as con:
        cur = con.cursor()
        q = "select ins, process from paraClassification where ins_pdf=%s and process_pdf=%s limit 1"
        cur.execute(q, (p1, p2))
        result = cur.fetchone()
        if result is not None:
            d = {'status': 'success',
                 'insurer': result[0],
                 'process': result[1]}
    return d

def process_p_flag_mails():
    print('process_p_flag_mails')
    mails_dict = {}
    fields = ("id","subject","date","sys_time","attach_path","completed","sender","sno","folder","process")
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select table_name, batch_size, sno from p_flag_process_tables where active=1"
        cur.execute(q)
        result = cur.fetchall()
        try:
            with open('logs/process_p_flag_mails.log', 'a') as tfp:
                print(str(datetime.now()), cur.statement, str(result), sep=',', file=tfp)
        except:
            pass
        for table, batch, sno in result:
            q1 = f"select * from {table} where completed='p' and sno > %s order by sno limit {batch}"
            cur.execute(q1, (sno,))
            records = []
            result1 = cur.fetchall()
            for i in result1:
                t = {}
                for k, v in zip(fields, i):
                    t[k] = v
                records.append(t)
            mails_dict[table] = records
    for hosp in mails_dict:
        change_active_flag_mail_storage_tables(table_name=hosp, flag=0, process_p=1)
        for row in mails_dict[hosp]:
            try:
                with mysql.connector.connect(**conn_data) as con:
                    cur = con.cursor()
                    q = f"update {hosp} set completed='pp' where sno=%s"
                    cur.execute(q, (row['sno'],))
                    con.commit()
                row_count_1 = 1
                filepath = row['attach_path']
                temp = get_pdf_ins_process(filepath)
                ins, ct = temp['insurer'], temp['process']
                subject, l_time, hid, mail_id, sno = row['subject'], row['date'], hosp, row['id'], row['sno']
                hid = hosp_dict[hosp]
                if ins != '' and ct != '':
                    with open('logs/process_p_flag_mails.log', 'a') as tfp:
                        print(str(datetime.now()), ins, ct, sep=',', file=tfp)
                    flag = 'DDD'
                    with mysql.connector.connect(**conn_data) as con:
                        cur = con.cursor()
                        q = f"update {hosp} set completed=%s where sno=%s"
                        cur.execute(q, (flag, row['sno'],))
                        con.commit()
                    subprocess.run(
                        ["python", ins + "_" + ct + ".py", filepath, str(row_count_1), ins, ct, subject, l_time, hid,
                         mail_id, str(sno)])
                    with mysql.connector.connect(**conn_data) as con:
                        cur = con.cursor()
                        q = f"update {hosp} set process='classification', classification_time=%s where sno=%s"
                        cur.execute(q, (row['sno'], str(datetime.now())))
                        con.commit()
            except:
                log_exceptions(row=row)
        change_active_flag_mail_storage_tables(table_name=hosp, flag=1, process_p=1)


if __name__ == '__main__':
    process_p_flag_mails()
