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

def create_settlement_folder(hosp, ins, date, filepath):
    dst = ""
    try:
        date = datetime.strptime(date, '%d/%m/%Y %H:%M:%S').strftime('%m%d%Y%H%M%S')
        today = datetime.now().strftime("%d_%m_%Y")
        folder = os.path.join(today, hosp, "letters", f"{ins}_{date}")
        dst = os.path.join(folder, os.path.split(filepath)[-1])
        Path(folder).mkdir(parents=True, exist_ok=True)
        copyfile(filepath, dst)
    except:
        log_exceptions(hosp=hosp, ins=ins, date=date, filepath=filepath)
    return os.path.abspath(dst)

if __name__ == "__main__":
    set_flag_graphapi('Welcome', '19/12/2020 13:17:22', 'sample')
