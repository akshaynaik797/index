import sqlite3
import subprocess

ins = "east_west"
process = "preauth"
attach_path = "/home/akshay/temp/index/east_west/attachments_pdf_preauth/702567_authletter_702567_124732_8636.pdf"
subject = "a"
date = "20/10/2020 05:43:00"

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