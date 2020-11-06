import sqlite3
import subprocess
import pdftotext

ins = "Paramount"
process = "denial"
attach_path = "/home/akshay/temp/index/Paramount/denial/1_1.pdf"
subject = "a"
date = "20/10/2020 05:43:00"

with open(attach_path, "rb") as f:
    pdf = pdftotext.PDF(f)
with open('aditya/output1.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('aditya/output1.txt', 'r') as myfile:
    f = myfile.read()

def get_run_no():
    run_no, q = 1, "select runno from updation_detail_log order by runno desc limit 1;"
    with sqlite3.connect('database1.db') as con:
        cur = con.cursor()
        result = cur.execute(q).fetchone()
        if result is not None:
            return str(result[0] + 1)
    return str(run_no)

run_no = get_run_no()
subprocess.run(["python", ins + "_" + process + ".py", attach_path, run_no, ins, process, subject,
                            date, 'max'])