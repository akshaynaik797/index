import sqlite3
import subprocess
import pdftotext
from custom_datadict import make_datadict

ins = "icici_lombard"
process = "preauth"
attach_path = "/home/akshay/PycharmProjects/index/icici_lombard/attachments_preauth/15.pdf"
subject = "a"
date = "20/10/2020 05:43:00"

with open(attach_path, "rb") as f:
    pdf = pdftotext.PDF(f)
with open('aditya/output1.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('aditya/output1.txt', 'r') as myfile:
    f = myfile.read()


data = make_datadict(f)
pass


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