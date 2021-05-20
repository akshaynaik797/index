from pathlib import Path
from shutil import copyfile

import mysql.connector
import os
from datetime import datetime
from custom_parallel import conn_data
from make_log import log_exceptions

fpname = 'fp_seq.txt'


def fp_seq_init():
    if not os.path.isfile(fpname):
        with open(fpname, 'w') as fp:
            fp.write('1')


def get_fp_seq():
    fp_seq_init()
    with open(fpname) as fp:
        num = fp.read()
    with open(fpname, 'w') as fp:
        fp.write(str(int(num) + 1))
    return num


def check_if_sub_and_ltime_exist(subject, l_time):
    try:
        subject = subject.replace("'", '')
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            b = f"select * from updation_detail_log where emailsubject like '%{subject}%' and date='{l_time}'"
            cur.execute(b)
            r = cur.fetchone()
            if r is not None:
                return True
            return False
    except:
        return False


def set_flag_graphapi(subject, l_time, flag, hospital):
    try:
        hosp_dict = {
            'Max PPT': 'graphApi',
            'inamdar': 'inamdar_mails',
            'noble': 'noble_mails',
            'ils': 'ils_mails',
            'ils_howrah': 'ils_howrah_mails',
            'ils_agartala': 'ils_agartala_mails',
            'ils_dumdum': 'ils_dumdum_mails'
        }
        data, data1 = (subject, l_time), (flag, subject, l_time, )
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            b = f'select * from updation_detail_log where emailsubject = %s  and date = %s limit 1;'
            cur.execute(b, data)
            a = cur.fetchone()
        if a is not None:
            with mysql.connector.connect(**conn_data) as con:
                cur = con.cursor()
                b = f"update {hosp_dict[hospital]} set completed=%s where subject = %s and date = %s"
                cur.execute(b, data1)
                con.commit()
    except:
        log_exceptions(data1=data1)

def get_ins_process(subject, email):
    ins, process = "", ""
    q1 = "select IC from email_ids where email_ids=%s limit 1"
    q2 = "select subject, table_name from email_master where ic_id=%s"
    q3 = "select IC_name from IC_name where IC=%s limit 1"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor(buffered=True)
        cur.execute(q1, (email,))
        result = cur.fetchone()
        if result is not None:
            ic_id = result[0]
            cur.execute(q2, (ic_id,))
            result = cur.fetchall()
            for sub, pro in result:
                if 'Intimation No' in subject:
                    return ('big', 'settlement')
                if 'STAR HEALTH AND ALLIED INSUR04239' in subject:
                    return ('small', 'settlement')
                if sub in subject:
                    cur.execute(q3, (ic_id,))
                    result1 = cur.fetchone()
                    if result1 is not None:
                        return (result1[0], pro)
    return ins, process

def create_settlement_folder(hosp, ins, date, filepath):
    dst = ""
    try:
        date = datetime.strptime(date, '%d/%m/%Y %H:%M:%S').strftime('%m%d%Y%H%M%S')
        today = datetime.now().strftime("%d_%m_%Y")
        folder = os.path.join(today, hosp, "letters", f"{ins}_{date}")
        dst = os.path.join(folder, os.path.split(filepath)[-1])
        Path(folder).mkdir(parents=True, exist_ok=True)
        copyfile(filepath, dst)
        return os.path.abspath(dst)
    except:
        log_exceptions(hosp=hosp, ins=ins, date=date, filepath=filepath)
        return ""

def get_api_url(hosp, process):
    api_conn_data = {'host': "iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
                 'user': "admin",
                 'password': "Welcome1!",
                 'database': 'portals'}
    with mysql.connector.connect(**api_conn_data) as con:
        cur = con.cursor()
        query = 'select apiLink from apisConfig where hospitalID=%s and processName=%s limit 1;'
        cur.execute(query, (hosp, process))
        result = cur.fetchone()
        if result is not None:
            return result[0]
    return ''

def change_active_flag_mail_storage_tables(**kwargs):
    q, params = "", []
    if 'hospital' in kwargs:
        q = 'update mail_storage_tables set active=%s where hospital=%s'
        params = [kwargs['flag'], kwargs['hospital']]
    if 'table_name' in kwargs:
        q = 'update mail_storage_tables set active=%s where table_name=%s'
        params = [kwargs['flag'], kwargs['table_name']]
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, params)
        con.commit()

if __name__ == "__main__":
    change_active_flag_mail_storage_tables(table_name="noble_mails", flag=1)