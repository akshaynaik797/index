import subprocess

import psycopg2

def write(x):
    conn = psycopg2.connect(database="temp", user="akshay", password="41424344", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    q = f"begin;" \
        f"insert into updation_detail_log ( runno, insurerid, process, downloadtime, starttime, endtime, emailsubject, date, fieldreadflag, failedfields, apicalledflag, apiparameter, apiresult, sms, error, row_no, emailid, completed, file_path, mail_id, hos_id, preauthid, amount, diagno, insname, doa, dod, corp, polhol, status, lettertime, policyno, memberid, comment, time_difference) values ('{x[1]}', '{x[2]}', '{x[3]}', '', " \
        f"'', '', '{x[4]}', '{x[5]}', " \
        f"'', '', '', '', " \
        f"'', '', '', '', " \
        f"'', '', '{x[0]}', '', '{x[6]}', '{x[7]}', '{x[8]}', '{x[9]}', '{x[10]}', '{x[11]}', '{x[12]}', " \
        f"'{x[13]}', '{x[14]}', '{x[15]}', '{x[16]}', '{x[17]}', '', '', '');" \
        f"commit;"
    cur.execute(q)

def run_ins_process(data):
    ins, process, attach_path, subject, date, hospital = data[0], data[1], data[2], data[3], data[4], data[5]
    subprocess.run(["python", ins + "_" + process + ".py", attach_path, '1', ins, process, subject,
                            date, hospital])
    print(f'finished {ins} {process}')
