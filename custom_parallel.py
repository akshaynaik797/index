import mysql.connector
import datetime
import json

import subprocess

conn_data = {'host': "iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
             'user': "admin",
             'password': "Welcome1!",
             'database': 'python'}

changes = (('preid', 'preauthid'), ('polno', 'policyno'), ('memid', 'memberid'), ('pname', 'comment'))


def time_diff(x):
    try:
        date, endtime = datetime.datetime.strptime(x[5], "%d/%m/%Y %H:%M:%S"), \
                        datetime.datetime.strptime(x[21], "%Y-%m-%d %H:%M:%S.%f")
        diff = endtime - date
        diff = diff.total_seconds()
        x[22] = diff
    except:
        pass
    return x


def doa_dod_format(date):
    # 15 16
    formats = ["%d %b %Y", "%d-%b-%Y %I.%M %p", "%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y", "%d-%b-%y", "%d-%b, %Y",
               "%m/%d/%Y %I%M%S %p"]
    for i in formats:
        try:
            date = datetime.datetime.strptime(date, i).strftime("%d/%m/%Y")
            return date
        except:
            pass
    return date


def write(x):
    x = time_diff(x)
    jobid = 1
    with mysql.connector.connect(**conn_data) as mydb:
        cur = mydb.cursor()
        q1 = f"select job_id from jobs where subject=%s and date=%s limit 1"
        x1 = (x[4], x[5])
        cur.execute(q1, x1)
        result = cur.fetchone()
        if result is not None:
            jobid = result[0]

    run_no = 1
    with mysql.connector.connect(**conn_data) as mydb:
        cur = mydb.cursor()
        q1 = f"SELECT runno FROM python.runs order by runno desc limit 1;"
        cur.execute(q1)
        result = cur.fetchone()
        if result is not None:
            try:
                run_no = result[0]
            except:
                pass

    x[1] = run_no
    x[15] = doa_dod_format(x[15])
    x[16] = doa_dod_format(x[16])
    x = get_status(x)
    x.append(jobid)
    x.append(x[5])
    apidict = x[19]
    for i in changes:
        apidict = apidict.replace(i[0], i[1])
    apidict = json.loads(apidict)
    apidict['lettertime'] = x[5]
    apidict['process'] = ""
    x[19] = str(apidict)
    x = tuple(x)
    with mysql.connector.connect(**conn_data) as mydb:
        cur = mydb.cursor()
        q = f"insert into updation_detail_log ( file_path, runno, insurerid, process, emailsubject, date, hos_id, " \
            f"mail_id, preauthid, comment, policyno, memberid, amount, diagno, insname, doa, dod, corp, polhol, " \
            f"apiresult, starttime, endtime, time_difference, status, jobid, lettertime)" \
            f" values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        cur.execute(q, x)
        mydb.commit()


def get_status(x):
    status = ''
    if x[3] == 'preauth' or x[3] == 'final':
        status = 'Approved'
    elif x[3] == 'query':
        status = 'Information Awaiting'
    elif x[3] == 'denial':
        status = 'Denial'
    elif x[3] == 'ack':
        status = 'Acknowledgement'
    elif 'General' in x[3]:
        temp = x[3].split(',')
        x[3], status = temp[0], temp[-1]
        z = 1
    x.append(status)
    a = x[19]
    a = a.replace("'", '"')
    a = json.loads(a)
    a['status'] = status
    x[19] = json.dumps(a)
    return x
    # 19


def run_ins_process(data):
    # subprocess.run(
    #     ["python", ins + "_" + ct + ".py", filepath, str(row_count_1), ins, ct, subject, l_time, hid,
    #      mail_id])
    ins, process, attach_path, subject, date, hospital, mail_id = data[0], data[1], data[2], data[3], data[4], data[5], \
                                                                  data[6]
    subprocess.run(["python", ins + "_" + process + ".py", attach_path, '1', ins, process, subject,
                    date, hospital, mail_id])
    print(f'finished {ins} {process}')

def process_record(data_dict):
    attach_path = data_dict['attach_path']
    for i in attach_path.split(','):
        if '.pdf' in i or '.PDF' in i:
            attach_path = i
    subprocess.run(["python", data_dict['insurer'] + "_" + data_dict['process'] + ".py", attach_path, '1',
                    data_dict['insurer'], data_dict['process'], data_dict['subject'],
                    data_dict['date'], data_dict['hospital'], data_dict['id']])
    print(f"finished {data_dict['insurer']} {data_dict['process']}")
    return True

def set_x(table, subject, date):
    q = f"select completed from {table} where subject=%s and date=%s"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (subject, date))
        record = cur.fetchone()
        if record is not None:
            q = "select * from updation_detail_log where emailsubject=%s and date=%s"
            cur.execute(q, (subject, date))
            temp = cur.fetchone()
            if temp is not None:
                flag = record[0]
                flag = flag + ',' + 'X'
                q = f"update {table} set completed=%s where subject=%s and date=%s"
                cur.execute(q, (flag, subject, date))
                con.commit()

if __name__ == "__main__":
    run_ins_process(['aditya', 'preauth', '/home/akshay/temp/11-17-0048207-02-00_74811.pdf', 'asd', '05/12/2020 19:02:20',
                     'sad', 'asdas'])
