import sqlite3
import subprocess
import pdftotext
from custom_datadict import make_datadict
import mysql.connector

from custom_parallel import conn_data

ins = "Paramount"
process = "preauth"
mail_id = '7777'
attach_path = r"C:\Apache24\htdocs\www\myapp\app\index2\index\index\Paramount\attachments_preauth\221.pdf"
subject = "a"
date = "20/10/2020 05:43:00"

with open(attach_path, "rb") as f:
    pdf = pdftotext.PDF(f)
with open('aditya/output1.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('aditya/output1.txt', 'r') as myfile:
    f = myfile.read()


data = make_datadict(f)
z =1


def get_run_no():
    run_no, q = 1, "SELECT COUNT(*) FROM updation_log;"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q)
        result = cur.fetchone()
        if result is not None:
            return str(result[0] + 1)
    return str(run_no)


run_no = get_run_no()
subprocess.run(["python", ins + "_" + process + ".py", attach_path, run_no, ins, process, subject,
                            date, 'max', mail_id])
# d = ['python', 'aditya_query.py', 'C:\\Apache24\\htdocs\\www\\myapp\\app\\index2\\index\\index/aditya/attachments_pdf_query/11-17-0046426-03-00_16673.pdf', '11053', 'aditya', 'query', 'Additional information required', '06/11/2020 17:26:41', 'Max', 'AAMkADMwMDQ2MWEwLWZmNjgtNGU1ZS05YmIyLWViMmY0MDY5MzA5NABGAAAAAABH2uYMVCRVRratBBRFfMEGBwDDBdWtz139QJTyVusjXSMMAIgnyAxbAACzb7cgXsgfSqOzUEFTGZMcAALGZXr5AAA=']
# subprocess.run(d)