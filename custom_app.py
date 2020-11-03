import sqlite3
import os
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
    fp.write(str(int(num)+1))
  return num


def check_if_sub_and_ltime_exist(subject, l_time):
    try:
        subject = subject.replace("'", '')
        with sqlite3.connect("database1.db") as con:
            xyz = 10
            cur = con.cursor()
            b = f"select * from updation_detail_log where emailsubject like '%{subject}%' and date='{l_time}'"
            cur.execute(b)
            r = cur.fetchone()
            if r is not None:
                return True
            return False
    except:
        False

if __name__ == "__main__":
    l_time = '05/10/2020 13:01:02'
    subject = "Cashless Letter From Raksha Health Insurance TPA Pvt.Ltd. (O55611157790,212200/48/2021/54,PRAKHATI MEHANI.)"
    print(check_if_sub_and_ltime_exist(subject, l_time))