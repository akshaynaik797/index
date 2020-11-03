from flask import *
import sqlite3
import datetime
import codecs
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
from itertools import chain
import time
import imaplib
import sys
import email
import os
from os import path
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
import base64
import foldercheck
from email.header import decode_header
from apscheduler.schedulers.background import BackgroundScheduler
import json
from flask_cors import CORS, cross_origin


#from apscheduler.schedulers.background import BackgroundScheduler

global s_r
global b
global mail_ids
global mail
global row_count_1
 
sheduler_count =0

b=0
s_r=0
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
fo = open("defualt_time_read.txt", "r")
t = fo.read()
tg = t.split()

# print(today)


# mail.id_list_1
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def hello():
    with sqlite3.connect("database1.db") as con:
        cur = con.cursor()
        q = "SELECT id,name FROM hospital"
        cur.execute(q)
        r = cur.fetchall()
    return render_template("index.html", r=r, len=len(r))


@app.route("/api/testapi")
def testapi():
    return render_template("test1.html")
  

@app.route("/api/testpostapi")
def testpostapi():
    return render_template("testpostmethod.html")
  

# @app.route("/api/postUdateDeatilsLogs",methods=["POST"])
# def postUpdateLog():
#     preauthid='' 
#     amount=''
#     status=''
#     lettertime=''
#     policyno=''
#     memberid=''
      
#     if request.method !='POST':
#         return jsonify(
#             {
#             'status' : 'failed',
#             'message':'inavlid request method.Only Post method Allowed'
#             }
#         ) 
       
#     if request.form.get('preauthid') !=None:
#         preauthid = request.form['preauthid']
       
#     if request.form.get('amount') !=None:
#         amount = request.form['amount']
       
#     if request.form.get('status') !=None:
#         status = request.form['status']  
        
#     if request.form.get('lettertime') !=None:
#         lettertime = request.form['lettertime']    
       
#     if request.form.get('policyno') !=None:
#         policyno = request.form['policyno'] 

#     if request.form.get('memberid') !=None:
#         memberid = request.form['memberid']        

#     if runno == '' :
#         return jsonify(
#               {
#               'status' : 'failed',
#               'message':'Parameter Field Are Empty'
#               }
#           )  
    
# try:
  
#   subprocess.run(["python", "test_api.py",hg[0],hg[1],hg[2],'',status,sys.argv[6],sys.argv[1],'',hg[3]])
  
# except Exception as e:
#   print(e.__str__())



@app.route("/api/getupdateDetailsLog",methods=["POST"])
def getUpdateLog():
   
    if request.method !='POST':
          return jsonify(
              {
              'status' : 'failed',
              'message':'inavlid request method.Only Post method Allowed'
              }
          ) 
    runno=''   
    if request.form.get('runno') !=None:
        runno = request.form['runno']

    if runno == '' :
          return jsonify(
              {
              'status' : 'failed',
              'message':'Parameter Field Are Empty'
              }
          )  
    try:  
      data=None           
      con = sqlite3.connect("database1.db")
      cur = con.cursor()
      query="""SELECT runno,insurerid,process,emailsubject,`date`,file_path,hos_id,preauthid,amount,`status`, \
        lettertime,policyno,memberid,apiparameter from updation_detail_log WHERE runno=%s"""%runno
      print(query)
      cur.execute(query)
      data=cur.fetchall()
      if data:
            myList=[]
            for row in data:
                  localDic={}
                  localDic['runno']=row[0]
                  localDic['insurerid']=row[1]
                  localDic['process']=row[2]
                  localDic['emailsubject']=row[3]
                  localDic['date']=str(row[4])
                  localDic['file_path']=row[5]
                  localDic['hos_id']=row[6]
                  localDic['preauthid']=row[7]
                  localDic['amount']=row[8]
                  localDic['status']=row[9]
                  localDic['lettertime']=row[10]
                  localDic['policyno']=row[11]
                  localDic['memberid']=row[12]
                  # x=row[13]
                  # print(x)
                  # localDic['apiparameter']=json.loads(row[13])
                  myList.append(localDic)
            # return render_template("detailview.html",updateList=myList)

            return jsonify(myList)
      else:
          localDic={}
          localDic['runno']=''
          localDic['insurerid']=''
          localDic['process']=''
          localDic['emailsubject']=''
          localDic['date']=''
          localDic['file_path']=''
          localDic['hos_id']=''
          localDic['preauthid']=''
          localDic['amount']=''
          localDic['status']=''
          localDic['lettertime']=''
          localDic['policyno']=''
          localDic['memberid']=''
          return jsonify(localDic)

            
    except Exception as e:
      print(e) 
      return jsonify({
        'status':'failure',
        'reason':e.__str__()
      })     



@app.route("/files")
def get_file():
    """Download a file."""
    if request.args['filepath'] != None:
        filepath=request.args['filepath']
        print("path=",filepath)
        # filepath1=r"C:\Users\91798\Desktop\trial_shikha-master2\hdfc\attachments_pdf_denial\PreAuthDenialLe_RC-HS19-10809032_1_202_20200129142830250_19897.pdf"
        filepath=filepath.replace("\\", "/")
        mylist=filepath.split('/')
        filename=mylist[-1]
        index=0
        dirname=''
        for x in mylist:
            index=index+1
            if index != len(mylist):
                dirname=dirname+x+'/'
                
        # return send_from_directory(r"C:\Users\91798\Desktop\download\templates", filename='ASHISHKUMAR_IT.pdf', as_attachment=True)
        return send_from_directory(dirname, filename=filename, as_attachment=True)
       

@app.route('/add', methods=["POST", "GET"])
def add():
    formparameter={}
    formparameter['interval'] =( request.form["intervel"])
    formparameter['fromtime'] = request.form["fromtime"]
    formparameter['totime'] = request.form["totime"]
    formparameter['id'] = request.form["id"]
    formparameter['hid'] = request.form["hid"]
    formparameter['count'] = request.form["count"]
    formparameter['pid'] = request.form["pid"]
    if formparameter['interval'] != '':
      print("Scheduler is called.")
      sched = BackgroundScheduler(daemon=False)
      sched.add_job(add1,'interval',seconds=int(formparameter['interval']), args=[formparameter], max_instances =1)
      sched.start()
    else:
      add1(formparameter)
    return "success"
      

          


# @app.route('/add', methods=["POST", "GET"])
def add1(formparameter):
    intervel = formparameter["interval"]
    if intervel == '':
      fromtime = formparameter["fromtime"]
      totime = formparameter["totime"]
      id = formparameter["id"]
      hid = formparameter["hid"]
      cou = formparameter["count"]
      proces = formparameter["pid"]
    # intervel = request.form["intervel"]
    # if intervel == '':
    #   fromtime = request.form["fromtime"]
    #   totime = request.form["totime"]
    #   id = request.form["id"]
    #   hid = request.form["hid"]
    #   cou = request.form["count"]
    #   proces = request.form["pid"]
    now = datetime.datetime.now()
    today = datetime.date.today()
    today = today.strftime('%d-%b-%Y')
    with sqlite3.connect("database1.db") as con:
      cur = con.cursor()
      b="SELECT COUNT (*) FROM updation_log"
      cur.execute(b)
      r=cur.fetchall()
      print(r)
      max_row=r[0][0]
      row_count_1=max_row + 1
    subprocess.run(["python", "updation.py","0","max1","1",str(row_count_1)])
    subprocess.run(["python", "updation.py","0","max","2",str(today)])
    subprocess.run(["python", "updation.py","0","max","3",str(now)])

    
    if intervel == '':
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
    else:
        mode = "intervel" 
        a = mode+"|"+intervel
        hid='all'

    file = open("sample.txt", "w")
    file.write(a)
    file.close()

    with sqlite3.connect("database1.db") as con:
        cur = con.cursor()
        if hid == 'all':
          q= "SELECT * FROM hospital"
        else:
          q = "SELECT * FROM hospital WHERE id=="+hid

        cur.execute(q)
        r_credentials = cur.fetchall()
        for i in range(0,len(r_credentials)):
            #print(r_credentials)
            email = r_credentials[i][2]
            password = r_credentials[i][3]
            server = r_credentials[i][4]
            inbox = r_credentials[i][5]
            mail = imaplib.IMAP4_SSL(server)
            hid=  r_credentials[i][1]
            
            f = None
            f = open(hid+".txt", "r")
            c = f.read()
            fg = c.split()
            f = open(hid+".txt", "a+")
            f.close()
            try:
                mail.login(email, password)
                #print(mail.list_folders())
                subprocess.run(["python", "updation.py","0","max","6",'YES'])
            except Exception as e:
                subprocess.run(["python", "updation.py","0","max","6",'NO'])


            #arrayemail = []
            #subjectemail = []
            mail.select(inbox, readonly=True)

            if(mode == "intervel"):
              type, mail.data = mail.search(None, '(since '+str(tg[-1])+')')
              mail.ids = mail.data[0]  # data is a list.
              mail.id_list = mail.ids.split()  # ids is a space separated string
            elif mode == "RANGE":
              q = "SELECT * FROM email_ids WHERE IC=="+id
              templist = ['preauth','query','final']
              if proces == 'all':
                tempidlist = []
                icidlist = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
                for id in icidlist:
                  id = str(id)
                  for i in templist:
                    b = "SELECT email_master.subject ,email_master.table_name, email_ids.email_ids, email_ids.IC FROM email_master JOIN email_ids  ON email_master.ic_id=email_ids.IC WHERE email_master.table_name = '"+i+"' and email_master.ic_id= '"+id+"' "
                    print(b)
                    cur.execute(b)
                    r = cur.fetchall()
                    mail.id_list_1 = []
                    for row in r:
                      ic_email = row[2]
                      ic_subject = row[0]
                      if (mode == "RANGE"):
                          print(ic_email+fromtime+totime)
                          type,mail.data = mail.search(None, '(FROM ' + ic_email + ' since '+fromtime+' before '+totime+' (SUBJECT "%s"))'  %ic_subject)
                          mail.ids = mail.data[0]  # data is a list.
                          mycount = len(mail.data[0].split())
                          #mail.id_list_2=mail.ids.split()
                          #mail.ids = mail.data[0]
                          if mycount > 0:
                            mail.id_list_1.append(mail.ids.split())
                            #print("mail_id=",mail.id_list_1)
                            coun = int(cou)
                            try:
                              mail.id_list_1 = list(chain.from_iterable(mail.id_list_1))
                            except TypeError:
                              pass
                            mail.id_list = mail.id_list_1
                            if (len(mail.id_list) > coun):
                                mail.id_list = mail.id_list[len(mail.id_list) - coun - 1:-1]
                                for i in mail.id_list:
                                    tempidlist.append(i)
                  mail.id_list = tempidlist
              elif id =='17':
                    
                    b = "SELECT * FROM email_ids  WHERE IC= '" + id + "' "
                    print(b)
                    cur.execute(b)
                    r = cur.fetchall()
                    mail.id_list_1 = []
                    for row in r:
                          ic_email = row[1]
                    print(ic_email+fromtime+totime)
                    type,mail.data = mail.search(None, '(FROM ' + ic_email + ' since '+fromtime+' before '+totime+')')
                    mail.ids = mail.data[0]  # data is a list.
                    mycount = len(mail.data[0].split())
                    if mycount > 0:
                            mail.id_list_1.append(mail.ids.split())
                            coun = int(cou)
                            mail.id_list_1 = list(chain.from_iterable(mail.id_list_1))
                            mail.id_list = mail.id_list_1
                            if (len(mail.id_list) > coun):
                                mail.id_list = mail.id_list[len(mail.id_list) - coun - 1:-1]
                            print("mail.id_list")
                            print(mail.id_list)    

             
              else:
                  b = "SELECT email_master.subject ,email_master.table_name, email_ids.email_ids, email_ids.IC FROM email_master JOIN email_ids  ON email_master.ic_id=email_ids.IC WHERE email_master.table_name = '" + proces + "' and email_master.ic_id= '" + id + "' "
                  print(b)
                  cur.execute(b)
                  r = cur.fetchall()
                  mail.id_list_1 = []
                  for row in r:
                      ic_email = row[2]
                      ic_subject = row[0]
                      if (mode == "RANGE"):
                          print(ic_email + fromtime + totime)
                          type, mail.data = mail.search(
                              None,
                              '(FROM ' + ic_email + ' since ' + fromtime + ' before ' + totime + ' (SUBJECT "%s"))' % ic_subject)
                          mail.ids = mail.data[0]  # data is a list.
                          mycount = len(mail.data[0].split())
                          if mycount > 0:
                            # mail.id_list_2=mail.ids.split()
                            # mail.ids = mail.data[0]
                            mail.id_list_1.append(mail.ids.split())
                            # print("mail_id=",mail.id_list_1)
                  coun = int(cou)
                  if (mode == "RANGE"):
                      mail.id_list_1 = list(chain.from_iterable(mail.id_list_1))
                      mail.id_list = mail.id_list_1
                      if (len(mail.id_list) > coun):
                         mail.id_list = mail.id_list[len(mail.id_list) - coun - 1:-1]
            print("mail.id_list")
            print(mail.id_list)


            if len(mail.id_list) > 0:
                #print(int(mail.id_list[-1].decode()),fg[-1],int(mail.id_list[-1].decode()) > int(fg[-1]))
                if len(fg) == 0 or int(mail.id_list[-1].decode()) > int(fg[-1]):
                    subprocess.run(["python", "updation.py", "0",
                                      "max", "7", str(len(mail.id_list))])
                      
                    print('new_mail')
                    for j in range(0, len(mail.id_list)):
                      if len(fg) == 0 or int(mail.id_list[j].decode()) > int(fg[-1]):
                                  temp=str(mail.id_list[j])
                                  f = open(hid+".txt", "a+")
                                  f.write(temp[2:-1]+'\n')
                                  f.close()
                    if id =="17":
                          proces_park(now,today,mail,row_count_1,hid,fg)
                    else:          
                          process(now,today,mail,row_count_1,hid,fg)
                    
                else:
                    subprocess.run(["python", "updation.py", "0", "max", "7", '0'])
                subprocess.run(
                    ["python", "updation.py", "0", "max", "8", str(s_r)])

    fo=open("defualt_time_read.txt", "a+")
    if(str(today)!=str(tg[-1])):
    	fo.write(str(today)+'\n')
    now = datetime.datetime.now()
    today = datetime.date.today()
    today = today.strftime('%d-%b-%Y')
    subprocess.run(["python", "updation.py","0","max","4",str(today)])
    subprocess.run(["python", "updation.py","0","max","5",str(now)])
    # return str(msg)
    print(f"----Job is scheduled for every "+intervel+" seconds")



def proces_park(now,today,mail,row_count_1, hid, fg):
  for i in range(0, len(mail.id_list)):
                if len(fg) == 0 or int(mail.id_list[i].decode()) > int(fg[-1]):
                                temp=str(mail.id_list[i])
                                # f = open("unread_mail.txt", "a+")
                                # f.write(temp[2:-1]+'\n')
                                # f.close()
                                mail.latest_email_id = mail.id_list[i]  # get the latest
                                print(mail.latest_email_id)
                                mail.latest_email_id=mail.latest_email_id
                                print("________________")
                                print(mail.latest_email_id)
                                try:
                                  mail.result, mail.data1 = mail.fetch(mail.latest_email_id, "(RFC822)")
                                except Exception as e:
                                  continue
                                mail.raw_email = mail.data1[0][1].decode('utf-8')
                                mail.email_message = email.message_from_string(mail.raw_email)
                                from_email = mail.email_message['From']
                                print(from_email)
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
                                temp_email=from_email
                                if temp_email.find("<")!=-1:
                                  temp_w=temp_email.find("<")
                                  temp_w=temp_w+1
                                  from_email=temp_email[temp_w:-1]
                                else:
                                  from_email=temp_email
                                subject = mail.email_message['Subject']
                                print(subject)
                                subprocess.run(["python", "foldercheck.py",("Park")])
                                download_pdf(s_r,mail,"Park","General",row_count_1,subject,hid)

      

def process(now,today,mail,row_count_1, hid, fg):
        for i in range(0, len(mail.id_list)):
                if len(fg) == 0 or int(mail.id_list[i].decode()) > int(fg[-1]):
                                temp=str(mail.id_list[i])
                                # f = open("unread_mail.txt", "a+")
                                # f.write(temp[2:-1]+'\n')
                                # f.close()
                                mail.latest_email_id = mail.id_list[i]  # get the latest
                                print(mail.latest_email_id)
                                mail.latest_email_id=mail.latest_email_id
                                print("________________")
                                print(mail.latest_email_id)
                                try:
                                  mail.result, mail.data1 = mail.fetch(mail.latest_email_id, "(RFC822)")
                                except Exception as e:
                                  continue
                                mail.raw_email = mail.data1[0][1].decode('utf-8')
                                mail.email_message = email.message_from_string(mail.raw_email)
                                from_email = mail.email_message['From']
                                print(from_email)
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
                                temp_email=from_email
                                if temp_email.find("<")!=-1:
                                  temp_w=temp_email.find("<")
                                  temp_w=temp_w+1
                                  from_email=temp_email[temp_w:-1]
                                else:
                                  from_email=temp_email
                                subject = mail.email_message['Subject']
                                print(subject)
                                if subject.find('UTF')!=-1:
                                  subject = decode_header(mail.email_message['Subject'])
                                  subject = subject[0]
                                  subject = subject[0].decode()
                                elif subject.find('utf')!=-1:
                                  subject = decode_header(mail.email_message['Subject'])
                                  subject = subject[0]
                                  subject = subject[0].decode()
                                print(subject)
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
                                                                                                    subprocess.run(["python", "foldercheck.py",(ic_name)])
                                                                                                    ic_emal_id = r[0][2]
                                                                                                    b = "SELECT * FROM email_master WHERE ic_id = " + id
                                                                                                    cur.execute(b)
                                                                                                    r=cur.fetchall()
                                                                                                    flag="false"
                                                                                                    if(len(r)>0):
                                                                                                        for row in r:
                                                                                                            subject_result=row[1]
                                                                                                            table_name=row[2]
                                                                                                            if subject.find(subject_result)!=-1 and ic_name!='star' :
                                                                                                                if subject.find('Denial')!=-1 or subject.find('REJECTED')!=-1:
                                                                                                                  table_name='denial'
                                                                                                                download_pdf(s_r,mail,ic_name,table_name,row_count_1,subject,hid)
                                                                                                                flag="true"
                                                                                                                break
                                                                                                            
                                                                                                            elif subject.find(subject_result)!=-1 and ic_name=='star':
                                                                                                                if subject.find('Rejection')!=-1:
                                                                                                                  table_name = 'denial'
                                                                                                                if subject.find('Query')!=-1:
                                                                                                                  table_name = 'query'
                                                                                                                if table_name == 'query' or table_name=='denial':
                                                                                                                  download_pdf(s_r,mail,ic_name,table_name,row_count_1,subject,hid)
                                                                                                                  flag="true"
                                                                                                                  break
                                                                                                                subprocess.run(["python", "updation.py","1","max1","4",str(row_count_1)]])
                                                                                                                subprocess.run(["python", "updation.py","1","max","1",str(row_count_1)])
                                                                                                                subprocess.run(["python", "updation.py","1","max","2",'star'])
                                                                                                                subprocess.run(["python", "updation.py","1","max","3",'preauth'])
                                                                                                                subprocess.run(["python", "updation.py","1","max","7",subject])
                                                                                                                #subprocess.run(["python", "updation.py","1","max","15",'error while downloading'])
                                                                                                                star_subject=mail.email_message['Subject']
                                                                                                                w=star_subject.find('-')
                                                                                                                ccn=star_subject[:w-1]
                                                                                                                subprocess.run(["python", "star_download.py",ccn,mail.email_message['Subject'],l_time,str(row_count_1),table_name,hid])

                                                                                                        if (flag=="true"):
                                                                                                            print(subject)
                                                                                                        else:
                                                                                                            print(subject,"=",subject_result)

                                                                                                            # NEED to raise error subject not known
                                                                                                            subprocess.run(["python", "updation.py","2","max1","1",str(row_count_1)])
                                                                                                            subprocess.run(["python", "updation.py","2","max","8",l_time])
                                                                                                            subprocess.run(["python", "updation.py","2","max","7", subject])
                                                                                                            subprocess.run(["python", "updation.py","2","max","17",str(mail.email_message['From'])])
                                                                                                            subprocess.run(["python", "updation.py","2","max","15",str('subject not known')])
                                                                                                            subprocess.run(["python", "updation.py","2","max","20",str(mail.latest_email_id)[2:-1]])
                                                                                                            subprocess.run(["python", "updation.py","1","max","21",hid])
                                                                                                            subprocess.run(["python", "sms_api.py",str('Updation failed for '+mail.email_message['Subject'])])
                                                                                                    else:
                                                                                                        # need to raise error if no subject
                                                                                                        print(subject)
                                                                                                        subprocess.run(["python", "updation.py","2","max1","1",str(row_count_1)])
                                                                                                        subprocess.run(["python", "updation.py","2","max","8",l_time])
                                                                                                        subprocess.run(["python", "updation.py","2","max","7", subject])
                                                                                                        subprocess.run(["python", "updation.py","2","max","17",str(mail.email_message['From'])])
                                                                                                        subprocess.run(["python", "updation.py","2","max","20",str(mail.latest_email_id)[2:-1]])
                                                                                                        subprocess.run(["python", "updation.py","2","max","15",str('No subject found in database ')])
                                                                                                        subprocess.run(["python", "updation.py","1","max","21",hid])
                                                                                                        subprocess.run(["python", "sms_api.py",str('No subject found in database '+mail.email_message['Subject'])])

                                                else:
                                                    # need to raise error for invalid email id
                                                    print("invalid email "+from_email)
                                                    subprocess.run(["python", "updation.py","2","max1","1",str(row_count_1)])
                                                    subprocess.run(["python", "updation.py","2","max","8",l_time])
                                                    subprocess.run(["python", "updation.py","2","max","7", subject])
                                                    subprocess.run(["python", "updation.py","2","max","17",str(mail.email_message['From'])])
                                                    subprocess.run(["python", "updation.py","2","max","15",str('No email id found in database ')])
                                                    subprocess.run(["python", "updation.py","2","max","20",str(mail.latest_email_id)[2:-1]])
                                                    subprocess.run(["python", "sms_api.py",str('No email id found in database  '+subject)])
                                                    subprocess.run(["python", "updation.py","1","max","21",hid])

        fo=open("defualt_time_read.txt", "a+")
        if(str(today)!=str(tg[-1])):
            fo.write(str(today)+'\n')
            now = datetime.datetime.now()
            today = datetime.date.today()
            today = today.strftime('%d-%b-%Y')

            subprocess.run(["python", "updation.py","0","max","4",str(today)])
            subprocess.run(["python", "updation.py","0","max","5",str(now)])
            print ('done1')


def download_html(s_r,mail,ins,ct,row_count_1,subject,hid):
  now = datetime.datetime.now()
  # wbkName = 'log file.xlsx'
  subprocess.run(["python", "foldercheck.py",(ins+'/attachments_'+ct)])
  dirFiles = os.listdir(ins+'/attachments_'+ct)
  mail.detach_dir=(os.getcwd()+'/'+ins+'/attachments_'+ct+'/')
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
      if mail.part.get_content_type() == "text/html" or mail.part.get_content_type() == "text/plain":
        mail.body = mail.part.get_payload(decode=True)
        mail.file_name = ins+'/email.html'
        mail.output_file = open(mail.file_name, 'w')
        try:
          mail.output_file.write("Body: %s" %(mail.body.decode('utf-8')))
        except Exception as e:
          continue
        
        mail.output_file.close()

        pdfkit.from_file(ins+'/email.html', ins+'/attachments_'+ct+'/'+str(b)+'.pdf',configuration=config)
  subprocess.run(["python", "updation.py","0","max","11",str(row_count_1)])
  mail.filePath=os.path.join(mail.detach_dir, str(b)+'.pdf')
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
  try:
    if(ct=='settlement'):
      start_date = datetime.date.today().strftime("%d-%b-%Y")
      end_date = datetime.date.today().strftime("%d-%b-%Y")
      uid=mail.latest_email_id.decode()
      subprocess.run(["python", "main.py",start_date,end_date,ins,hid,uid])
    else:
      fp2 =open(ins+"_"+ct+".py", "r")
      fp2.close()
      subprocess.run(["python", ins+"_"+ct+".py",ins+'/attachments_'+ct+'/'+str(b)+'.pdf',str(row_count_1),ins,ct,subject,l_time])
  except Exception as e:
    subprocess.run(["python", "updation.py","0","max","11",str(row_count_1)])
      #wbk.save(wbkName)
    s_r+=1
    subprocess.run(["python", "updation.py","1","max1","1",str(row_count_1)])
    subprocess.run(["python", "updation.py","1","max","2",str(ins)])
    subprocess.run(["python", "updation.py","1","max","3",str(ct)])
    subprocess.run(["python", "updation.py","2","max","8",l_time])
    subprocess.run(["python", "updation.py","2","max","7", subject])
    subprocess.run(["python", "updation.py","1","max","15",'python file doesnot exist- '+ins+'_'+ct+'.py'])
    #print(e)  
  subprocess.run(["python", "updation.py","1","max","19",mail.filePath])
  subprocess.run(["python", "updation.py","1","max","20",str(mail.latest_email_id)[2:-1]])
  subprocess.run(["python", "updation.py","1","max","21",hid])
  #print("s_r = " s_r)
  subprocess.run(["python", "updation.py","1","max","3",str(ct)])
  s_r=s_r+1

  subprocess.run(["python", "updation.py","1","max","4",str(now)])
def download_pdf(s_r,mail,ins,ct,row_count_1,subject,hid):
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
      if mail.part.get('Content-Disposition') is None and mail.part.get_filename() is None:
        #print part.as_string()
        continue
      mail.fileName = mail.part.get_filename()
      subprocess.run(["python", "foldercheck.py",(os.getcwd()+'/'+ins+'/attachments_pdf_'+ct)])
      mail.detach_dir=(os.getcwd()+'/'+ins+'/attachments_pdf_'+ct+'/')
      if bool(mail.fileName):
        if(mail.fileName.find('MDI')!=-1):
          continue
        if(mail.fileName.find('KYC')!=-1):
          continue
        if(mail.fileName.find('image')!=-1):
          continue
        if(mail.fileName.find('DECLARATION')!=-1):
          continue
        if(mail.fileName.find('Declaration')!=-1):
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
                                                      fil = mail.fileName
                                                      if fil.find("\r" or "\\r" or "\n" or "\\n")!=-1:
                                                        re.sub(r'\\r\\n', '', fil)
                                                        if ins == 'Max_Bupa':
                                                          fil =  fil[:-11]
                                                      fil = fil[:-4]
                                                      mail.fileName=fil+'_'+str(mail.latest_email_id)[2:-1]+'.pdf'
                                                      mail.filePath = os.path.join(mail.detach_dir, mail.fileName)
          if ins == 'Raksha':
            filename = mail.fileName
            subprocess.run(["python", "raksha_test.py", str(filename), str(ct), subject])
          else:
            fp = open(mail.filePath, 'wb')
            fp.write(mail.part.get_payload(decode=True))
            fp.close()
    dol=1

  except Exception as e:

    subprocess.run(["python", "updation.py","0","max","11",str(row_count_1)])
    #wbk.save(wbkName)
    s_r+=1
    subprocess.run(["python", "updation.py","1","max1","1",str(row_count_1)])
    subprocess.run(["python", "updation.py","1","max","2",str(ins)])
    subprocess.run(["python", "updation.py","1","max","3",str(ct)])
    subprocess.run(["python", "updation.py","1","max","15",'error while downloading'])
    # print(e)
  if (t_p==0):
    # print(mail.email_message['Subject'])
    download_html(s_r,mail,ins,ct,row_count_1,subject,hid)
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
    try:
      if(ct=='settlement'):
        start_date = datetime.date.today().strftime("%d-%b-%Y")
        end_date = datetime.date.today().strftime("%d-%b-%Y")
        uid=mail.latest_email_id.decode()
        subprocess.run(["python", "main.py",start_date,end_date,ins,hid,uid])
      else:
        fp1 = open(ins+"_"+ct+".py","r")
        fp1.close()
        subprocess.run(["python", ins+"_"+ct+".py", mail.filePath,str(row_count_1),ins,ct,subject,l_time])
    except Exception as e:
      subprocess.run(["python", "updation.py","0","max","11",str(row_count_1)])
      #wbk.save(wbkName)
      s_r+=1
      subprocess.run(["python", "updation.py","1","max1","1",str(row_count_1)])
      subprocess.run(["python", "updation.py","1","max","2",str(ins)])
      subprocess.run(["python", "updation.py","1","max","3",str(ct)])
      subprocess.run(["python", "updation.py","2","max","8",l_time])
      subprocess.run(["python", "updation.py","2","max","7", subject])
      subprocess.run(["python", "updation.py","1","max","15",'python file doesnot exist- '+ins+'_'+ct+'.py'])
      print(e)
    subprocess.run(["python", "updation.py","1","max","19",mail.filePath])
    subprocess.run(["python", "updation.py","1","max","21",hid])
    subprocess.run(["python", "updation.py","1","max","20",str(mail.latest_email_id)[2:-1]])


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
    # return render_template("viewdetaillog.html",log_head=log_head,log_row = log_row,row_len=row_len)


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

    return "hello"



@app.route('/openpdf', methods=["POST", "GET"])
def openPdf():
  if request.method == "GET" :
    if request.args['path'] != '':
      filepath=request.args['path']
      print("path=",filepath)
      # filepath1=r"C:\Users\91798\Desktop\trial_shikha-master2\hdfc\attachments_pdf_denial\PreAuthDenialLe_RC-HS19-10809032_1_202_20200129142830250_19897.pdf"
      filepath=filepath.replace("\\", "/")
      subprocess.Popen(filepath,shell=True)
      # window.open(newpath,'_blank')
  return "success"
  #  filepath1=r"C:\Users\91798\Desktop\trial_shikha-master2\hdfc\attachments_pdf_denial\PreAuthDenialLe_RC-HS19-10809032_1_202_20200129142830250_19897.pdf"
  #  filepath12=filepath1.replace("\\", "/")
  #  subprocess.Popen(filepath12,shell=True)
  #  return "success"

if __name__ == '__main__':
    # app.run(host="0.0.0.0")
  app.run()  
