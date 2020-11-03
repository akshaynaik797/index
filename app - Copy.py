from flask import *
import sqlite3
import datetime

from datetime import datetime
from email.mime.text import MIMEText
import smtplib
import time
import imaplib
import sys
import email
import os
import struct
import time
import subprocess
from datetime import date
from datetime import datetime
from itertools import chain
import datetime
import openpyxl
import re
import pdfkit
import foldercheck


global s_r
global b
global mail_ids
global mail
global row_count_1
with sqlite3.connect("database1.db") as con:
    cur = con.cursor()
    b="SELECT COUNT (*) FROM updation_log"
    cur.execute(b)
    r=cur.fetchall()
    print(r)
    max_row=r[0][0]
    row_count_1=max_row + 1

b=0
s_r=0
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
f = open("unread_mail.txt", "r")
fo = open("defualt_time_read.txt", "r")
t = fo.read()
tg = t.split()
c = f.read()
fg = c.split()
# print(today)
f = open("unread_mail.txt", "a+")

# mail.id_list_1
app = Flask(__name__)


@app.route('/')
def hello():
    with sqlite3.connect("database1.db") as con:
        cur = con.cursor()
        q = "SELECT id,name FROM hospital"
        cur.execute(q)
        r = cur.fetchall()
    return render_template("index.html", r=r, len=len(r))


@app.route('/add', methods=["POST", "GET"])
def add():
    intervel = request.form["intervel"]
    fromtime = request.form["fromtime"]
    totime = request.form["totime"]
    id = request.form["id"]
    hid = request.form["hid"]
    now = datetime.datetime.now()
    today = datetime.date.today()
    today = today.strftime('%d-%b-%Y')
    subprocess.run(["python", "updation.py","0","max1","1",str(row_count_1)])
    subprocess.run(["python", "updation.py","0","max","2",str(today)])
    subprocess.run(["python", "updation.py","0","max","3",str(now)])


    datetimeobject = datetime.datetime.strptime(fromtime, '%Y-%m-%d')
    fromtime = str(datetimeobject.strftime('%d-%b-%Y'))
    datetimeobject = datetime.datetime.strptime(totime, '%Y-%m-%d')
    totime = str(datetimeobject.strftime('%d-%b-%Y'))

    msg = fromtime+" TO "+totime
    if(intervel != '' and fromtime == '' and totime == ''):
        mode = "intervel"
    elif(intervel == '' and fromtime != '' and totime != ''):
        mode = "RANGE"

    else:
        mode = "ERROR"
    a = mode+"|"+intervel+"|"+fromtime+"|"+totime+"|"+id+"|"+hid
    file = open("sample.txt", "w")
    file.write(a)
    file.close()

    with sqlite3.connect("database1.db") as con:
        cur = con.cursor()
        q = "SELECT * FROM hospital WHERE id=="+hid
        cur.execute(q)
        r = cur.fetchall()
        email = r[0][2]
        password = r[0][3]
        server = r[0][4]
        inbox = r[0][5]
        mail = imaplib.IMAP4_SSL(server)
        try:
            mail.login(email, password)
            subprocess.run(["python", "updation.py","0","max","6",'YES'])
        except Exception as e:
            subprocess.run(["python", "updation.py","0","max","6",'NO'])


        arrayemail = []
        subjectemail = []
        mail.select(inbox, readonly=True)
        q = "SELECT * FROM email_ids WHERE IC=="+id
        cur.execute(q)
        r = cur.fetchall()
        ic_email = r[0][1]
        mail.id_list_1 = []
        if (mode == "RANGE"):
            # +' before 5-Apr-2020'+')' )#
            #temp_email=ic_email
            #temp_w=temp_email.find("<")
            #temp_w=temp_w+1
            #ic_email=temp_email[temp_w:-1]
            print(ic_email+fromtime+totime)
            mail.data = mail.search(
                None, '(FROM ' + ic_email + ' since '+fromtime+' before '+totime+')')
            mail.ids = mail.data[1]  # data is a list.
            #print(mail.ids[0])
            temp=str(mail.ids[0])
            temp=temp[2:-1]
            print("temp = "+temp)
            # ids is a space separated string


            mail.id_list_1=temp.split(" ")
            #mail.ids = mail.data[0]
            #mail.id_list_1.append((mail.ids.split()))

            print(mail.id_list_1)
            temp_len=len(mail.id_list_1)
            for i in range (temp_len):
                mail.id_list_1[i]=str("b"+mail.id_list_1[i])

            mail.id_list = mail.id_list_1

            print("mail.id_list")
            print(mail.id_list)

        elif(mode == "intervel"):
            # +' before 5-Apr-2020'+')' )#
            mail.data = mail.search(None, '(since '+str(tg[-1])+')')
            mail.ids = mail.data[0]  # data is a list.
            mail.id_list = mail.ids.split()  # ids is a space separated string

        if len(mail.id_list) > 0:
            if len(fg) == 0 or str(mail.id_list[-1]) > fg[-1]:
                if(len(fg) == 0):

                    subprocess.run(["python", "updation.py", "0",
                                   "max", "7", str(len(mail.id_list))])
                else:
                    temp = re.findall(r'\d+', fg[-1])

                    m_c = int(mail.id_list[-1].decode())-int(temp[0])
                    print(m_c)
                    subprocess.run(
                        ["python", "updation.py", "0", "max", "7", str(m_c)])
                print('new_mail')
                f.write(str(mail.id_list[-1])+'\n')
                f.close()
                process(now,today,mail)
            else:
                subprocess.run(["python", "updation.py", "0", "max", "7", '0'])
            subprocess.run(
                ["python", "updation.py", "0", "max", "8", str(s_r)])

		# mail.id_list = list(chain.from_iterable(mail.id_list_1))

        # type, data = mail.search(None, 'ALL')
        # mail_ids = data[0]

        #id_list = mail_ids.split()
        #first_email_id = int(id_list[0])
        #latest_email_id = int(id_list[-1])
    #    for i in range(latest_email_id,first_email_id, -1):
    #    typ, data = mail.fetch(str("0"), '(RFC822)' )
    fo=open("defualt_time_read.txt", "a+")
    if(str(today)!=str(tg[-1])):
    	fo.write(str(today)+'\n')
    now = datetime.datetime.now()
    today = datetime.date.today()
    today = today.strftime('%d-%b-%Y')
    subprocess.run(["python", "updation.py","0","max","4",str(today)])
    subprocess.run(["python", "updation.py","0","max","5",str(now)])
    return str(msg)


if __name__ == '__main__':
    app.run(host="0.0.0.0")


def process(now,today,mail):
        for i in range(0, len(mail.id_list)):
                if len(fg) == 0 or str(mail.id_list[i]) > fg[-1]:
                                mail.latest_email_id = mail.id_list[i]  # get the latest
                                print(mail.latest_email_id)
                                mail.latest_email_id=mail.latest_email_id[1:]
                                print("________________")
                                print(mail.latest_email_id)
                                mail.result, mail.data1 = mail.fetch(mail.latest_email_id, "(RFC822)")
                                mail.raw_email = mail.data1[0][1].decode('utf-8')
                                mail.email_message = email.message_from_string(mail.raw_email)
                                from_email = mail.email_message['From']
                                print(from_email)
                                temp_email=from_email
                                temp_w=temp_email.find("<")
                                temp_w=temp_w+1
                                from_email=temp_email[temp_w:-1]
                                subject = mail.email_message['Subject']
                                print("++++++++++++")
                                print(from_email)
                                with sqlite3.connect("database1.db") as con:
                                                xyz = 10
                                                cur = con.cursor()
                                                b = "SELECT IC_name.IC ,IC_name.IC_name, email_ids.email_ids FROM IC_name JOIN email_ids  ON IC_name.IC=email_ids.IC WHERE email_ids.email_ids = '"+from_email+"'"
                                                print(b)
                                                cur.execute(b)
                                                r = cur.fetchall()
                                                if (len(r) > 0):
                                                                                                    id = str(r[0][0])
                                                                                                    ic_name = r[0][1]
                                                                                                    b = "SELECT * FROM email_master WHERE ic_id = " + id
                                                                                                    cur.execute(b)
                                                                                                    r=cur.fetchall()
                                                                                                    flag="false"
                                                                                                    if(len(r)>0):
                                                                                                        for row in r:
                                                                                                            subject_result=row[1]
                                                                                                            table_name=row[2]
                                                                                                            if subject.find(subject_result)!=-1 :
                                                                                                                download_pdf(s_r,mail,ic_name,table_name)
                                                                                                                flag="true"
                                                                                                                break
                                                                                                        if (flag=="true"):
                                                                                                            print(subject)
                                                                                                        else:
                                                                                                            print(subject,"=",subject_result)

                                                                                                            # NEED to raise error subject not known
                                                                                                            #subprocess.run(["python", "updation.py","2","max","1",str(row_count_1)])
                                                                                                            subprocess.run(["python", "updation.py","2","max","8",str(mail.email_message['Date'])])
                                                                                                            subprocess.run(["python", "updation.py","2","max","7",str(mail.email_message['Subject'])])
                                                                                                            subprocess.run(["python", "updation.py","2","max","17",str(mail.email_message['From'])])
                                                                                                            subprocess.run(["python", "updation.py","2","max","15",str('subject not known')])
                                                                                                            subprocess.run(["python", "sms_api.py",str('Updation failed for '+mail.email_message['Subject'])])
                                                                                                    else:
                                                                                                        # need to raise error if no subject
                                                                                                        print(subject)
                                                                                                        subprocess.run(["python", "updation.py","2","max","1",str(row_count_1)])
                                                                                                        subprocess.run(["python", "updation.py","2","max","8",str(mail.email_message['Date'])])
                                                                                                        subprocess.run(["python", "updation.py","2","max","7",str(mail.email_message['Subject'])])
                                                                                                        subprocess.run(["python", "updation.py","2","max","17",str(mail.email_message['From'])])
                                                                                                        subprocess.run(["python", "updation.py","2","max","15",str('No subject found in database ')])
                                                                                                        subprocess.run(["python", "sms_api.py",str('No subject found in database '+mail.email_message['Subject'])])

                                                else:
                                                    # need to raise error for invalid email id
                                                    print("invalid email"+from_email)
                                                    subprocess.run(["python", "updation.py","2","max","1",str(row_count_1)])
                                                    subprocess.run(["python", "updation.py","2","max","8",str(mail.email_message['Date'])])
                                                    subprocess.run(["python", "updation.py","2","max","7",str(mail.email_message['Subject'])])
                                                    subprocess.run(["python", "updation.py","2","max","17",str(mail.email_message['From'])])
                                                    subprocess.run(["python", "updation.py","2","max","15",str('No email id found in database ')])
                                                    subprocess.run(["python", "sms_api.py",str('No email id found in database  '+mail.email_message['Subject'])])



        fo=open("defualt_time_read.txt", "a+")
        if(str(today)!=str(tg[-1])):
            fo.write(str(today)+'\n')
            now = datetime.datetime.now()
            today = datetime.date.today()
            today = today.strftime('%d-%b-%Y')

            subprocess.run(["python", "updation.py","0","max","4",str(today)])
            subprocess.run(["python", "updation.py","0","max","5",str(now)])
            print ('done1')


def download_html(s_r,mail,ins,ct):
  now = datetime.datetime.now()
  # wbkName = 'log file.xlsx'
  subprocess.run(["python", "foldercheck.py",(ins+'/attachments_'+ct)])
  dirFiles = os.listdir(ins+'/attachments_'+ct)

  dirFiles.sort(key=lambda l: int(re.sub('\D', '', l)))
  # print(dirFiles[-1])
  if(len(dirFiles)>0):
    m=dirFiles[-1].find('.')
    b=int(dirFiles[-1][:m])
  else:
    b=0
  b+=1
  # print(b)
  for mail.part in mail.email_message.walk():
      if mail.part.get_content_type() == "text/html":
        mail.body = mail.part.get_payload(decode=True)
        mail.file_name = ins+'/email.html'
        mail.output_file = open(mail.file_name, 'w')
        mail.output_file.write("Body: %s" %(mail.body.decode('utf-8')))
        mail.output_file.close()

        pdfkit.from_file(ins+'/email.html', ins+'/attachments_'+ct+'/'+str(b)+'.pdf',configuration=config)
  subprocess.run(["python", "updation.py","0","max","11",str(row_count_1)])
  # print(mail.email_message['Date'])
  l_time=mail.email_message['Date']
  w=l_time.find(',')+1
  g=l_time[w:]
  u=g.find('+')+w
  s=l_time[w:u]
  s=s.split(' ')
  while("" in s) :
      s.remove("")
  # print(s)
  if(len(s)==4):
    t=s[0]+' '+s[1]+' '+s[2]+' '+s[3]

    d = datetime.datetime.strptime(t, '%d %b %Y %H:%M:%S')
    l_time=d.strftime('%d/%m/%Y %H:%M:%S')
  else:
    l_time=mail.email_message['Date']
  subprocess.run(["python", ins+"_"+ct+".py",ins+'/attachments_'+ct+'/'+str(b)+'.pdf',str(row_count_1),ins,ct,mail.email_message['Subject'],l_time])
  subprocess.run(["python", "updation.py","1","max","19",ins+'/attachments_'+ct+'/'+str(b)+'.pdf'])
  subprocess.run(["python", "updation.py","1","max","20",mail.latest_email_id])
  #print("s_r = " s_r)
  subprocess.run(["python", "updation.py","1","max","3",str(ct)])
  s_r=s_r+1

  subprocess.run(["python", "updation.py","1","max","4",str(now)])
def download_pdf(s_r,mail,ins,ct):
  print("pdf downloading")
  now = datetime.datetime.now()
  # wbkName = 'log file.xlsx'
  dol=0
  # try:
  try:
    t_p=0
    for mail.part in mail.email_message.walk():
      if mail.part.get_content_maintype() == 'multipart':
      # print part.as_string()
        continue
      # if mail.part.get('Content-Disposition') is None:
      # print part.as_string()
      #	continue
      mail.fileName = mail.part.get_filename()
      subprocess.run(["python", "foldercheck.py",(os.getcwd()+'/'+ins+'/attachments_pdf_'+ct)])
      mail.detach_dir=(os.getcwd()+'/'+ins+'/attachments_pdf_'+ct+'/')
      if bool(mail.fileName):
        if(mail.fileName.find('MDI')!=-1):
          continue
        if(mail.fileName.find('KYCForm')!=-1):
          continue
        if(mail.fileName.find('DECLARATION')!=-1):
          continue
        else:
          t_p=1
          if ins.find("Cholamandalam")!= -1:
                                                      w=mail.email_message['Subject'].find(':')+2
                                                      jk=str(now)
                                                      jk=jk.replace(' ','_')
                                                      filename=mail.email_message['Subject'][w:]
                                                      # print(filename)
                                                      mail.filePath=os.path.join(mail.detach_dir, filename+'.pdf')
                                                      ter=1
                                                      # print(mail.filePath)
                                                      while(path.exists(mail.filePath)):

                                                             mail.filePath=os.path.join(mail.detach_dir, filename+'('+str(ter)+').pdf')
                                                             # print(mail.filePath)
                                                             ter+=1
          # if not os.path.isfile(mail.filePath) :


          else:
                                                      mail.filePath = os.path.join(mail.detach_dir, mail.fileName)
          fp = open(mail.filePath, 'wb')
          fp.write(mail.part.get_payload(decode=True))
          fp.close()
    dol=1

  except Exception as e:

    subprocess.run(["python", "updation.py","0","max","11",str(row_count_1)])
    #wbk.save(wbkName)
    s_r+=1
    subprocess.run(["python", "updation.py","1","max","1",str(row_count_1)])
    subprocess.run(["python", "updation.py","1","max","2",str(ins)])
    subprocess.run(["python", "updation.py","1","max","3",str(ct)])
    subprocess.run(["python", "updation.py","1","max","15",'error while downloading'])
    # print(e)
  if (t_p==0):
    # print(mail.email_message['Subject'])
    download_html(s_r,mail,ins,ct)
    return 0
  if(dol==1):
    subprocess.run(["python", "updation.py","0","max","11",str(row_count_1)])
    # print(mail.email_message['Date'])
    l_time=mail.email_message['Date']
    w=l_time.find(',')+1
    g=l_time[w:]
    u=g.find('+')+w
    s=l_time[w:u]
    s=s.split(' ')
    while("" in s) :
        s.remove("")
    # print(s)
    if(len(s)==4):
      t=s[0]+' '+s[1]+' '+s[2]+' '+s[3]

      d = datetime.datetime.strptime(t, '%d %b %Y %H:%M:%S')
      l_time=d.strftime('%d/%m/%Y %H:%M:%S')
    else:
      l_time=mail.email_message['Date']
    subprocess.run(["python", ins+"_"+ct+".py", mail.filePath,str(row_count_1),ins,ct,mail.email_message['Subject'],l_time])
    subprocess.run(["python", "updation.py","1","max","19",mail.filePath])
    subprocess.run(["python", "updation.py","1","max","20",mail.latest_email_id])


    s_r+=1
    subprocess.run(["python", "updation.py","1","max","4",str(now)])

#------------------------------

@app.route('/viewlog')
def viewlog():
    con = sqlite3.connect("database1.db")
    cur = con.cursor()
    cur.execute("SELECT * from updation_log")
    log_row = cur.fetchall()
    #print(log_row)
    row_len=len(log_row)
    cur.execute("PRAGMA table_info('updation_log') ")
    log_head = cur.fetchall()
    return render_template("viewlog.html",log_head=log_head,log_row = log_row,row_len=row_len)

@app.route('/viewdetaillog/<id>')
def viewdetaillog(id):
    con = sqlite3.connect("database1.db")
    cur = con.cursor()
    cur.execute("SELECT * from updation_detail_log WHERE runno="+id)
    log_row = cur.fetchall()
    #print(log_row)
    row_len=len(log_row)
    cur.execute("PRAGMA table_info('updation_detail_log') ")
    log_head = cur.fetchall()
    return render_template("viewdetaillog.html",log_head=log_head,log_row = log_row,row_len=row_len)


@app.route('/apirun', methods=["POST", "GET"])
def apirun():
    api_value = request.form["api_value"]
    x = api_value.replace("'", '"')

    res = json.loads(x)
    print(res)
    with sqlite3.connect("database1.db") as con:
        cur = con.cursor()
        q = 'SELECT file_path FROM updation_detail_log WHERE apiparameter== "'+api_value+'"'
        print(q)
        cur.execute(q)
        r = cur.fetchall()
        file_path=r[0][0]
    subprocess.run(["python", "test_api.py",res["preauthid"],res["amount"],res["policyno"],res["process"],res["status"],res["lettertime"],file_path,"NULL",res["comment"]])

    return "helloe"
