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
import re
from make_log import log_exceptions
from datetime import datetime as akdatetime


badchars = ("'",)

for i, j in enumerate(sys.argv):
    for k in badchars:
        sys.argv[i] = j.replace(k, '')

with open('updation_log.log', 'a+', encoding='utf-8') as fp:
    entry = ('===================================================================================================\n'
                 f'{str(akdatetime.now())}\n'
                 # '---------------------------------------------------------------------------------------------------\n'
                 f'{str(sys.argv)}\n')
    fp.write(entry)

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
  17: "emailid",
  19: "file_path",
  20: "mail_id",
  21: "hos_id",
  22: "preauthid",
  23: "amount",
  24: "status",
  25: "lettertime",
  26: "policyno",
  27: "memberid",
  28: "comment",

}
updation_log_dict = {
  1: "runno",
  2: "start_date",
  3: "start_time",
  4: "end_date",
  5: "end_time",
  6: "connection_successful",
  7: "count_of_new_mails",
  8: "script_run_for_insurers",
  9: "successful_call_to_API",
  10: "result_of_API",
  11: "log_no",

}



while global_lock.locked():
	#continue
	print('lock in updation')
global_lock.acquire()
#wbkName = 'log file.xlsx'
#wbk= openpyxl.load_workbook(wbkName)
#sys.argv1 - sheet number   0(updation_log) 1,2,3,4(updation_detail_log)
#sys.argv 2 - row number by max / max 1
#sys.argv 3 - column number
#sys.argv 4 - value
col_index=int(sys.argv[3])
print(col_index)

if (sys.argv[1]=="0"):
	table="updation_log"
	col= updation_log_dict.get(col_index)

else:
	table="updation_detail_log"
	col= updation_detail_log_dict.get(col_index)
print(col)
print(sys.argv)


with sqlite3.connect("database1.db") as con:
    cur = con.cursor()
    q="SELECT COUNT (*) FROM "+table
    print(q)
    try:
        cur.execute(q)
    except:
        log_exceptions
    r=cur.fetchall()
    max_row=r[0][0]
    print(max_row)
    #col=sys.argv[3]
    val=sys.argv[4]
    if(col == 'runno' and table == 'updation_detail_log'):
        q="SELECT max(runno) FROM "+table
        print(q)
        try:
            cur.execute(q)
        except:
            log_exceptions
        r=cur.fetchall()
        if(r[0][0] != int(val) and sys.argv[2]=='max'):
            sys.argv[2]='max1'
            print("max changed to max1")
    if (sys.argv[2]=='max1'):
        print("NEW")
        row_count = str(max_row+1) #new reord
        q="INSERT INTO "+table+"("+col+",row_no) VALUES ("+val+","+row_count+")"
        print(q)
        try:
            cur.execute(q)
        except:
            log_exceptions

    elif (sys.argv[2]=='max'):
        print("UPDATE")
        print(max_row)
        if(col == 'runno'):
            print(val)

        row_count = max_row # existing recodrd update
        row_no=str(max_row)
        #val = re.sub(r'[?|$|.|!]',r'',val)
        if(val == '{"msg":"Can\'t Understand Data"}'):
            val = '{"msg":"Cant Understand Data"}'
        if(col == "apiparameter"):
            q="UPDATE "+table+" SET "+col+ ' = "'+val+'" WHERE row_no = '+row_no
        else:
            q="UPDATE "+table+" SET "+col+ " = '"+val+"' WHERE row_no = "+row_no

        print(q)
        file = open("sample.txt", "a", encoding='utf-8')
        file.write("\n")
        file.write(q)
        file.close()
        try:
            cur.execute(q)
        except:
            with open('updation_log_fail.log', 'a+', encoding='utf-8') as fp:
                entry = ('===================================================================================================\n'
                         f'{str(akdatetime.now())}\n'
                        '---------------------------------------------------------------------------------------------------\n'
                         f'{q}\n'
                        '---------------------------------------------------------------------------------------------------\n'
                        f'{str(sys.argv)}\n')
                fp.write(entry)
            log_exceptions(query=q)
            pass

            

    else:
        row_count = int(sys.argv[2])
        row_no=sys.argv[2]


global_lock.release()
if(sys.argv[3]=='11' and sys.argv[4]=='No' and sys.argv[1]=='1' ):
	#subj=cell(row_count, column=7).value
    a=str(max_row)
    subprocess.run(["python", "sms_api.py",str('API not called for row no '+a)])