import openpyxl
import threading
import sys
import time
import subprocess
import sqlite3
import os
import sys
from email.mime.text import MIMEText
import smtplib
import time
import imaplib
import sys
import email
import os
import struct, time
import subprocess
from datetime import date
import datetime
import openpyxl
import sqlite3

global_lock = threading.Lock()


updation_detail_log_dict = {
  1: "runno",
  2: "insurerid",
  3: "process",
  4: "downloadtime",
  5: "starttime",
  6: "endtime",
  7: "emailsubject",
  8: "date",
  9: "fieldreadflag",
  10: "failedfields",
  11: "apicalledflag",
  12: "apiparameter"  ,
  13: "apiresult",
  14: "sms",
  15: "error",
  17: "emailid"

}
updation_log_dict = {
  1: "runno",
  2: "start_date",
  3: "start_time",
  4: "end_date",
  5: "end_time",
  6: "connection_successful",
  7: "count_of_new mails",
  8: "script run for_insurers",
  9: "successful_call_to_API",
  10: "result_of_API",
  11: "log_no",

}



while global_lock.locked():
	#continue
	print('ji')
global_lock.acquire()
#wbkName = 'log file.xlsx'
#wbk= openpyxl.load_workbook(wbkName)
#sys.argv1 - sheet number   0(updation_log) 1,2,3,4(updation_detail_log)
#sys.argv 2 - row number by max / max 1
#sys.argv 3 - column number
#sys.argv 4 - value
col_index=int(sys.argv[3])
print(col_index)


temp_no=int(sys.argv[1])

if (temp_no==0):
    table="updation_log"
    print("table = updation_log" )
    col= updation_log_dict.get(col_index)


else:
	table="updation_detail_log"
	col= updation_detail_log_dict.get(col_index)

print(col)
print("table =" +sys.argv[1]+ table)
print(sys.argv)


with sqlite3.connect("database1.db") as con:
    cur = con.cursor()
    q="SELECT COUNT (*) FROM "+table
    cur.execute(q)
    r=cur.fetchall()
    max_row=r[0][0]
    print(max_row)
    #col=sys.argv[3]
    val=sys.argv[4]
    if (sys.argv[2]=='max1'):
        print("NEW")
        row_count = str(max_row+1) #new reord
        q="INSERT INTO "+table+"("+col+",row_no) VALUES ("+val+","+row_count+")"
        cur.execute(q)

    elif (sys.argv[2]=='max'):
        print("UPDATE")
        print(max_row)

        row_count = max_row # existing recodrd update
        row_no=str(max_row)
        q="UPDATE "+table+" SET "+col+ " = '"+val+"' WHERE row_no = "+row_no
        print(q)
        cur.execute(q)

    else:
        row_count = int(sys.argv[2])
        row_no=sys.argv[2]

'''
cell(row_count, column=int(sys.argv[3])).value=sys.argv[4]
wbk.save(wbkName)
wbk.close()


global_lock.release()
if(sys.argv[3]=='11' and sys.argv[4]=='No' and sys.argv[1]=='1' ):
	subj=cell(row_count, column=7).value
	subprocess.run(["python", "sms_api.py",str('API not called for '+subj)])
'''
