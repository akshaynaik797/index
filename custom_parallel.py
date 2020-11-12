import mysql.connector

import subprocess


def write(x):
    x = tuple(x)
    mydb = mysql.connector.connect(
        host="iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
        user="admin",
        password="Welcome1!",
        database='python'
    )
    # conn = psycopg2.connect(database="temp", user="akshay", password="41424344", host="127.0.0.1", port="5432")
    cur = mydb.cursor()
    q = f"insert into updation_detail_log ( file_path, runno, insurerid, process, emailsubject, date, hos_id, " \
        f"mail_id, preauthid, comment, policyno, memberid, amount, diagno, insname, doa, dod, corp, polhol, apiresult)" \
        f" values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    cur.execute(q, x)
    mydb.commit()

def run_ins_process(data):
    ins, process, attach_path, subject, date, hospital = data[0], data[1], data[2], data[3], data[4], data[5]
    subprocess.run(["python", ins + "_" + process + ".py", attach_path, '1', ins, process, subject,
                            date, hospital])
    print(f'finished {ins} {process}')

if __name__ == "__main__":
    x = ['icici_lombard/attachments_preauth/20.pdf', '1', 'icici_lombard', 'preauth', 'Cashless Request  110201053260 is Approved at 12:16:07 PM for Amt INR 47091. Please contact hospital TPA desk for copy of approval letter', '19/10/2020 12:16:22', 'inamdar hospital', '14345', '110201053260', '', '', '', '47091', '', 'or TPA reserves right to raise queries for any other', '17-OCT-2020', '', '', '', "\\{'preid': '110201053260', 'pname': '', 'polno': '', 'memid': '', 'amount': '47091', 'diagno': '', 'insname': 'or TPA reserves right to raise queries for any other', 'doa': '17-OCT-2020', 'dod': '', 'corp': '', 'polhol': ''\\}"]
    write(x)