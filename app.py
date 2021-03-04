# from flask import *
import csv
import uuid
from multiprocessing import Pool
from os.path import splitext, isfile, join
from shutil import copyfile

import mysql.connector
import requests
from flask import Flask, render_template, session, request, redirect, url_for, jsonify, send_from_directory
from flask_session import Session
import app_config
import msal
import json
import datetime
from datetime import datetime as datetime1, timedelta, timezone, date
import pytz
from dateutil import tz
import tzlocal
import sqlite3
import codecs
from email.mime.text import MIMEText
import smtplib
from itertools import chain
import time
import imaplib
import sys
import email
import os
from os import path, listdir
import struct
import subprocess
from itertools import chain
import openpyxl
import re
import pdfkit
import base64

import custom_parallel
import foldercheck
from email.header import decode_header
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from flask_cors import CORS, cross_origin

import pytz
from datetime import datetime as akdatetime
from dateutil import parser as date_parser
from make_log import log_exceptions, log_data, custom_log_data
from cust_time_functs import ifutc_to_indian, time_fun_two
from city_api import get_from_db
from update_detail_api import get_update_log
from custom_app import check_if_sub_and_ltime_exist, get_fp_seq, create_settlement_folder, get_ins_process
from custom_parallel import conn_data
from sms_alerts import send_sms

import threading

sem = threading.Semaphore()
timeout_time = 120
graph_db_location = r"../graph_api/database1.db"
# from apscheduler.schedulers.background import BackgroundScheduler

global s_r
global b
global mail_ids
global mail
global row_count_1
global datetime


sheduler_count = 0

b = 0
s_r = 0
# path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

fo = open("defualt_time_read.txt", "r")
t = fo.read()
tg = t.split()

app = Flask(__name__)

app.config.from_object(app_config)
Session(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['referrer_url'] = None


@app.route("/")
def index():
  '''
  if not session.get("user"):
    return redirect(url_for("login"))
  '''
  return render_template('index.html')#, user=session["user"], version=msal.__version__

@app.route("/download")
def download():
    import os
    aa = request.url_root
    path = request.args.get('path')
    folder, file = os.path.split(path)
    return send_from_directory(folder, filename=file, as_attachment=True)

@app.route("/get_sms_mails", methods=["POST"])
def get_sms_mails():
    link_text = request.url_root + 'api/downloadfile?filename='
    result = []
    fields = ("subject","date","completed","attach_path","sno","row_id","hospital")
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = 'select subject,date,completed,attach_path,sno,row_id,hospital from sms_mails where id is null'
        cur.execute(q)
        records = cur.fetchall()
    for i in records:
        temp = {}
        for key, value in zip(fields, i):
            temp[key] = value
        temp['attach_path'] = link_text + temp['attach_path'].replace(',', '')
        result.append(temp)
    return jsonify(result)

@app.route("/set_flag_sms_mails", methods=["POST"])
def set_flag_sms_mails():
    data = request.form.to_dict()
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "update sms_mails set id='X' where row_id=%s"
        cur.execute(q, (data['row_id'], ))
        con.commit()
    return jsonify('records updated')

def send_sms_text(mobile_no, body):
    try:
        headers = {
            'authkey': '167826ARvnR1lKl5cee8065',
            'content-type': "application/json"
        }
        API_ENDPOINT = "https://api.msg91.com/api/v2/sendsms"
        data = {
            "sender": "MAXPPG",
            "route": "4",
            "country": "91",
            "sms": [
                {
                    "message": body,
                    "to": [
                        mobile_no
                    ]
                }
            ]
        }
        # r = requests.post(url=API_ENDPOINT, data=json.dumps(data), headers=headers)
        custom_log_data(filename="sms_body", no=mobile_no, body=body)
        # return r.status_code
        return 400
    except:
        log_exceptions()

def check_date():
    from datetime import datetime
    fields = ('table_id','table_name','active','flag','id','subject','date','hospital', 'sno')
    records = []
    record_dict = {}
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = 'select * from mail_storage_tables'
        cur.execute(q)
        records = cur.fetchall()
    for i in records:
        temp = {}
        for key, value in zip(fields, i):
            temp[key] = value
        record_dict[temp['table_name']] = temp
    with mysql.connector.connect(**conn_data) as con:
        for temp, i in record_dict.items():
            cur = con.cursor()
            q = f"select subject, date, completed, attach_path, sno, sender from {i['table_name']} where completed not in ('p', 'X', '', 'S', 'DDD', 'pp') and sno > %s"
            cur.execute(q, (i['sno'],))
            result = cur.fetchall()
            for j in result:
                j = list(j)
                j.append(i['hospital'])
                j = tuple(j)
                q = "INSERT INTO sms_mails (`subject`,`date`,`completed`,`attach_path`,`sno`, `sender`, `hospital`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cur = con.cursor()
                cur.execute(q, j)
                send_sms_text('9967044874', f"{j[0]}|||{j[1]}|||{j[2]}|||{i['hospital']}")
        con.commit()
    with mysql.connector.connect(**conn_data) as con:
        for i in record_dict:
            table_name = record_dict[i]['table_name']
            cur = con.cursor()
            q = f"select id, subject, date, sno from {table_name} order by sno desc limit 2"
            cur.execute(q)
            records = cur.fetchall()
            if len(records) == 2:
                mid, subject, date, sno = records[0]
                date1 = datetime.strptime(records[0][2], '%d/%m/%Y %H:%M:%S')
                date2 = datetime.strptime(records[1][2], '%d/%m/%Y %H:%M:%S')
                flag = ''
                if date1 >= date2:
                    flag = 'VALID'
                else:
                    flag = 'INVALID'

                q = f"update mail_storage_tables set flag=%s, id=%s, subject=%s, date=%s, sno=%s where table_name=%s"
                cur.execute(q, (flag, mid, subject, date, sno, table_name))
        con.commit()

@app.route("/get_mail_storage_tables", methods=["POST"])
def get_mail_storage_tables():
    fields = ('table_id','table_name','active','flag','id','subject','date','hospital')
    result = []
    record_dict = {}
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = 'select * from mail_storage_tables'
        cur.execute(q)
        records = cur.fetchall()
    for i in records:
        temp = {}
        for key, value in zip(fields, i):
            temp[key] = value
        result.append(temp)
    return jsonify(result)

def log_api_data(varname, value):
  from datetime import datetime as akdatetime
  with open('api_data.log', 'a+') as fp:
    nowtime = str(akdatetime.now())
    entry = ('===================================================================================================\n'
             f'{nowtime}\n'
             # '---------------------------------------------------------------------------------------------------\n'
             f'{varname}->{value}\n')
    fp.write(entry)

@app.route("/get_mails", methods=["POST"])
def get_mails():
    data, records = request.form.to_dict(), []
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select table_name, hospital_name from mail_storage_tables where is_active='1'"
        cur.execute(q)
        table_list = cur.fetchall()
        table_dict = {key:value for key, value in table_list}
        for i in table_dict:
            fields = ('subject', 'date', 'attach_path', 'completed')
            q = "select subject, date, attach_path, completed from %s where completed not like '%s'" % (i, "%"+'X'+'%')
            cur.execute(q)
            mails = cur.fetchall()
            for j in mails:
                record = dict()
                for key, value in zip(fields, j):
                   record[key] = value
                record['hospital'] = table_dict[i]
                records.append(record)
    return jsonify(records)

@app.route("/set_flag", methods=["POST"])
def set_flag():
    data, records = request.form.to_dict(), []
    fields = ('subject', 'date', 'flag', 'hospital')
    for i in fields:
        if i not in data:
            return jsonify(f"{i} parameter required")
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select table_name, hospital_name from mail_storage_tables where is_active='1'"
        cur.execute(q)
        table_list = cur.fetchall()
    hospital = ''
    for i, j in table_list:
        if j == data['hospital']:
            table = i
            break
    q = f"select completed from {table} where subject=%s and date=%s"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (data['subject'], data['date'] ))
        record = cur.fetchone()
        if record is not None:
            flag = record[0]
            flag = flag + ',' + data['flag']
            q = f"update {table} set completed=%s where subject=%s and date=%s"
            cur.execute(q, (flag, data['subject'], data['date']))
            con.commit()
            return jsonify('done')
    return jsonify('record not found')

@app.route("/setsettlementflag", methods=["POST"])
def set_settlement_flag():
    data, records = request.form.to_dict(), []
    fields = ('subject', 'date', 'flag', 'hospital')
    for i in fields:
        if i not in data:
            return jsonify(f"{i} parameter required")
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select table_name, hospital from mail_storage_tables where active='1'"
        cur.execute(q)
        table_list = cur.fetchall()
    for i, j in table_list:
        if j == data['hospital']:
            table = i
            break
    q = "select * from " + table + " where subject=%s and date=%s"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (data['subject'], data['date'] ))
        record = cur.fetchone()
        if record is not None:
            mid, subject, date, sys_time, attach_path, completed, sender, sno, folder, process = record
            if attach_path == '' or attach_path is None:
                return jsonify('attachment not found')
            ins, proc = get_ins_process(subject, sender)
            if proc != 'settlement':
                return jsonify('wrong process '+proc)
            filepath = create_settlement_folder(data['hospital'], ins, data, attach_path)
            try:
                q = f"insert into settlement_mails (`id`,`subject`,`date`,`sys_time`,`attach_path`,`completed`,`sender`,`hospital`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                data1 = (mid, subject, date, str(datetime.datetime.now()), filepath, '', sender, data['hospital'])
                cur.execute(q, data1)
                q1 = "update " + table + " set completed = 'S' where date = %s and subject=%s;"
                data1 = (date, subject)
                cur.execute(q1, data1)
                con.commit()
            except:
                log_exceptions()
                return jsonify('error')
            return jsonify('done')
    return jsonify('record not found')


@app.route("/process_record", methods=["POST"])
def process_record():
    data, records = request.form.to_dict(), []
    fields = ('subject', 'date', 'insurer', 'hospital', 'process')
    for i in fields:
        if i not in data:
            return jsonify(f"{i} parameter required")
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select table_name, hospital_name from mail_storage_tables where is_active='1'"
        cur.execute(q)
        table_list = cur.fetchall()
    table = ''
    for i, j in table_list:
        if j == data['hospital']:
            table = i
            break
    if table == '':
        return jsonify(f"invalid hospital {data['hospital']}")

    q = f"select id, subject , date, attach_path from {table} where subject=%s and date=%s"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (data['subject'], data['date']))
        record = cur.fetchone()
        data_dict = dict()
        if record is not None:
            fields = ('id', 'subject', 'date', 'attach_path')
            for key, value in zip(fields, record):
                data_dict[key] = value
            data_dict['process'] = data['process']
            data_dict['insurer'] = data['insurer']
            data_dict['hospital'] = data['hospital']
            for key, value in data_dict.items():
                if value == '':
                    return jsonify(f"unable to process record, {key} is empty")
            flag = custom_parallel.process_record(data_dict)
            if flag is True:
                custom_parallel.set_x(table, data['subject'], data['date'])
            return jsonify('done')
    return jsonify('record not found')

@app.route("/api/city", methods=["GET"])
def get_id():
  key = request.args['key']
  data = get_from_db(key)
  return jsonify(data)


@app.route('/mob_app_insert')
def mob_app_insert():
  dbpath = 'database1.db'
  device_id = request.args['device_id']
  token = request.args['token']
  with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    q = f"select * from mob_app where device_id='{device_id}'"
    if cur.execute(q).fetchone() is not None:
      q1 = f"update mob_app set token='{token}' where device_id='{device_id}'"
      cur.execute(q1)
      con.commit()
      return jsonify('update query successful')
    elif cur.execute(q).fetchone() is None:
      cur.execute(f"insert into mob_app values('{device_id}', '{token}')")
      con.commit()
      return jsonify('insert query successful')
  return jsonify('query failed')


@app.route('/hello')
def hello():
  with mysql.connector.connect(**conn_data) as con:
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


@app.route("/api/postUpdateDetailsLogs", methods=["POST"])
def postUpdateLog():
  weightage = {
    'preauthid' : 0.55,
    'amount' : 0.15,
    'status' : 0.10,
    'policyno' : 0.05,
    'memberid' : 0.05,
    'comment' : 0.10,
  }
  preauthid = ''
  amount = ''
  status = ''
  lettertime = ''
  policyno = ''
  memberid = ''
  row_no = ''
  comment = ''
  completed = ''
  tagid = ''
  refno = ''
  # if request.method != 'POST':
  #   return jsonify(
  #     {
  #       'status': 'failed',
  #       'message': 'inavlid request method.Only Post method Allowed'
  #     }
  #   )
  from flask import request
  if request.form.get('row_no') != None:
    row_no = request.form['row_no']
  if request.form.get('completed') != None:
    completed = request.form['completed']  # completd = D
  if completed == 'D':
    with mysql.connector.connect(**conn_data) as con:
      cur = con.cursor()
      query = f'update updation_detail_log set completed= "D" where row_no={row_no};'
      print(query)
      log_api_data('query', query)
      cur.execute(query)
      con.commit()
      apimessage = 'Record successfully updated, and API not called'
      apimessage = 'Record successfully updated, and API not called'
      request_temp = requests.post(url_for("change_filepath_flag", _external=True), data={"row_no":row_no, "completed":"D"})
      return jsonify({
        'status': 'success',
        'message': apimessage})


  with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    q = f'select preauthid,amount,status,process,lettertime,policyno,memberid,hos_id, comment from updation_detail_log where row_no={row_no}'
    print(q)
    log_api_data('q', q)
    cur.execute(q)
    r = cur.fetchone()
    hosid = r[7]

  if request.form.get('preauthid') != None:
    preauthid = request.form['preauthid']

  if request.form.get('amount') != None:
    amount = request.form['amount']

  if request.form.get('status') != None:
    status = request.form['status']

  if request.form.get('lettertime') != None:
    lettertime = request.form['lettertime']

  if request.form.get('policyno') != None:
    policyno = request.form['policyno']

  if request.form.get('memberid') != None:
    memberid = request.form['memberid']

  if request.form.get('comment') != None:
    comment = request.form['comment']
  if request.form.get('tag_id') != None:
    tagid = request.form['tag_id']
  if request.form.get('refno') != None:
    refno = request.form['refno']
  try:
    time_diff2 = datetime.datetime.now() - datetime.datetime.strptime(lettertime, '%d/%m/%Y %H:%M:%S')
    time_diff2 = time_diff2.total_seconds()
    with mysql.connector.connect(**conn_data) as con:
      cur = con.cursor()
      cur.execute(f'update updation_detail_log set time_difference2="{time_diff2}" where row_no={row_no};')
      con.commit()
  except:
    log_exceptions()
  if (r is not None
    and preauthid == r[0]
    and amount == r[1]
    and status == r[2]
    # and process == r[3]
    and lettertime == r[4]
    and policyno == r[5]
    and memberid == r[6]):
    char = 'X'
  else:
    char = 'x'
  changed = []
  formdata = (preauthid, amount, status, policyno, memberid, comment)
  dbdata = (r[0], r[1], r[2], r[5], r[6], r[8])
  fields = ('preauthid', 'amount', 'status', 'policyno', 'memberid', 'comment')
  weight = 0
  for i, j, k in zip(formdata, dbdata, fields):
    if i != j:
      changed.append(k)
    if i == j:
      weight = weight + weightage[k]
  weight = round(weight, 2)
  with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    cur.execute(f'update updation_detail_log set weightage="{weight}" where row_no={row_no};')
    con.commit()
  if row_no == '':
    return jsonify(
      {
        'status': 'failed',
        'message': 'Parameter Field Are Empty'
      }
    )

  try:
    query = "update updation_detail_log set"
    flag = 0
    if request.form.get('preauthid') != None:
      query = query + " preauthid='%s'" % preauthid
      flag = 1

    if request.form.get('amount') != None:
      if flag == 1:
        query = query + ", "
      query = query + " amount='%s'" % amount
      flag = 1

    if request.form.get('status') != None:
      if flag == 1:
        query = query + ", "
      query = query + " status='%s'" % status
      flag = 1

    if request.form.get('lettertime') != None:
      if flag == 1:
        query = query + ", "
      query = query + " lettertime='%s'" % lettertime
      flag = 1

    if request.form.get('comment') != None:
      if flag == 1:
        query = query + ", "
      query = query + " comment='%s'" % comment
      flag = 1

    if request.form.get('policyno') != None:
      if flag == 1:
        query = query + ", "
      query = query + " policyno='%s'" % policyno
      flag = 1

    if request.form.get('memberid') != None:
      if flag == 1:
        query = query + ", "
      query = query + " memberid='%s'" % memberid
      flag = 1

    if len(query) > len("update updation_detail_log set"):
      # query=query+", completed='X'"
      query = query + " where row_no=%s" % row_no
      print(query)
      log_api_data('query', query)

      sem.acquire()
      print('Lock Acquired')
      with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(query)
        con.commit()
      sem.release()
      print('Lock Released')
      # akshay code to call API............ first, fetch file_path from local db

      with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = f'select file_path from updation_detail_log where row_no={row_no};'
        print(q)
        log_api_data('q', q)
        cur.execute(q)
        r = cur.fetchone()
        if r:
          r = r[0]
        else:
          r = ''

      if r == None:
        apimessage = "Record updated in db, but API failed due to no File"
      else:
        print(row_no)
        log_api_data('row_no', row_no)
        print(r)
        log_api_data('r', r)
        files = {'doc': open(r, 'rb')}
        # if hosid == 'Max PPT':
        #   API_ENDPOINT = "https://vnusoftware.com/iclaimmax/api/preauth/"
        # else:
        #   API_ENDPOINT = "https://vnusoftware.com/iclaimportal/api/preauth"
        API_ENDPOINT = get_api_url(hosid, 'postUpdateDetailsLogs')
        data = {
          'preauthid': preauthid,
          # 'pname': sys.argv[10],
          'amount': amount,
          'status': status,
          'process': '',
          'lettertime': lettertime,
          'policyno': policyno,
          'memberid': memberid,
          'write': 'X',
          'tagid': tagid,
          'comment': comment,
          'refno': refno,
        }

        r = requests.post(url=API_ENDPOINT, data=data, files=files)
        print(data)
        log_api_data('data', data)
        pastebin_url = r.text
        print(pastebin_url)
        log_api_data('pastebin_url', pastebin_url)

        if pastebin_url.find("Data Update Success") == -1:
          apimessage = "Record updated in db, and API failed"
          subprocess.run(["python", "sms_api.py", "api error"])
        else:
          current_time = datetime.datetime.now()
          # if char == 'X':
          #   query = f'update updation_detail_log set completed= "X" where row_no={row_no};'
          # elif char == 'x':
          #   query = f'update updation_detail_log set completed= "x" where row_no={row_no};'
          # with mysql.connector.connect(**conn_data) as con:
          #   cur = con.cursor()
          #   cur.execute(query)
          #   con.commit()
          apimessage = 'Record successfully updated, and API successfully called'
          request = requests.post(url_for("change_filepath_flag", _external=True),
                                  data={"row_no": row_no, "completed": char})

          # update completed flag in table
          # with sqlite3.connect('../mail_fetch/database1.db', timeout=timeout_time) as con:
          #   cur = con.cursor()
          #   cur.execute(f"update run_table set completed = 'D' where ref_no = '{refno}'")

      # if api call returns success message, then message = 'Record succ updated, and API succ called.
      # if not, then message = 'Record updated in db, but API failed.
      return jsonify({
        'status': 'success',
        'message': apimessage
      })
    else:
      return jsonify({
        'status': 'success',
        'message': 'Record not successfully updated'

      })

  except Exception as e:
    log_exceptions()
    sem.release()
    print(e.__str__())
    log_api_data('e.__str__()', e.__str__())
    return jsonify({
      'status': 'failure',
      'message': 'Record does not updated',
      'reason': e.__str__()
    })

@app.route('/change_filepath_flag', methods=["POST"])
def change_filepath_flag():
    fields = ['runno','insurerid','process','downloadtime','starttime','endtime','emailsubject','date',
              'fieldreadflag','failedfields','apicalledflag','apiparameter','apiresult','sms','error',
              'row_no','emailid','completed','file_path','mail_id','hos_id','preauthid','amount','status',
              'lettertime','policyno','memberid','comment','time_difference','diagno','insname','doa','dod','corp',
              'polhol','jobid','time_difference2','weightage']
    letters_folder = "letters_folder"
    if not os.path.exists(letters_folder):
        os.mkdir(letters_folder)
    data, q = request.form.to_dict(), ""
    if 'completed' not in data:
        return jsonify({"msg": "fail"})
    if 'row_no' not in data and 'hos_id' not in data:
        return jsonify({"msg": "fail"})
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        if 'hos_id' in data:
            if data['hos_id'] != 'all':
                q = "select row_no, file_path from updation_detail_log where completed is null and hos_id=%s"
                cur.execute(q, (data['hos_id'],))
            else:
                q = "select row_no, file_path from updation_detail_log where completed is null"
                cur.execute(q)
            records = cur.fetchall()
            if len(records) == 0:
                return jsonify({"msg": "fail"})
            for row_no, result in records:
                if not os.path.exists(result):
                   continue
                os.replace(result, os.path.join(letters_folder, os.path.split(result)[-1]))
                filepath = os.path.abspath(os.path.join(letters_folder, os.path.split(result)[-1]))
                q = "update updation_detail_log set completed=%s, file_path=%s where row_no=%s"
                cur.execute(q, (data['completed'], filepath, row_no))
                con.commit()
                q = "select * from updation_detail_log where row_no=%s limit 1"
                cur.execute(q, (row_no,))
                record = cur.fetchone()
                q = "insert into updation_detail_log_copy values (" + '%s,' * len(record) + ")"
                q = q.replace(',)', ')')
                cur.execute(q, record)
                con.commit()
                q = "delete from updation_detail_log where row_no=%s"
                cur.execute(q, (row_no,))
                con.commit()

            return jsonify({"msg": "success"})
        if 'row_no' in data:
            q = "select file_path from updation_detail_log where row_no=%s limit 1" % data['row_no']
            cur.execute(q)
            result = cur.fetchone()
            if result is not None:
                if os.path.exists(result[0]):
                    os.replace(result[0], os.path.join(letters_folder, os.path.split(result[0])[-1]))
                    filepath = os.path.abspath(os.path.join(letters_folder, os.path.split(result[0])[-1]))
                    q = "update updation_detail_log set completed=%s, file_path=%s where row_no=%s"
                    cur.execute(q, (data['completed'], filepath, data['row_no']))
                    con.commit()
                    q = "select * from updation_detail_log where row_no=%s limit 1"
                    cur.execute(q, (data['row_no'],))
                    record = cur.fetchone()
                    q = "insert into updation_detail_log_copy values (" + '%s,'*len(record) + ")"
                    q = q.replace(',)', ')')
                    cur.execute(q, record)
                    con.commit()
                    q = "delete from updation_detail_log where row_no=%s"
                    cur.execute(q, (data['row_no'],))
                    con.commit()
                    return jsonify({"msg": "success"})
            return jsonify({"msg": "fail"})

def get_api_url(hosp, process):
    api_conn_data = {'host': "iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
                 'user': "admin",
                 'password': "Welcome1!",
                 'database': 'portals'}
    with mysql.connector.connect(**api_conn_data) as con:
        cur = con.cursor()
        query = 'select apiLink from apisConfig where hospitalID=%s and processName=%s limit 1;'
        cur.execute(query, (hosp, process))
        result = cur.fetchone()
        if result is not None:
            return result[0]
    return ''


@app.route("/api/getupdateDetailsLog", methods=["POST"])
def getUpdateLog():
  from flask import request
  if request.method != 'POST':
    return jsonify(
      {
        'status': 'failed',
        'message': 'inavlid request method.Only Post method Allowed'
      }
    )
  runno = ''
  if request.form.get('runno') != None:
    runno = request.form['runno']

  if runno == '':
    return jsonify(
      {
        'status': 'failed',
        'message': 'Parameter Field Are Empty'
      }
    )
  try:
    data = None
    con = mysql.connector.connect(**conn_data)
    cur = con.cursor()
    if runno == '00':
      query = """SELECT runno,insurerid,process,emailsubject,date,file_path,hos_id,preauthid,amount,status,lettertime,policyno,memberid,row_no,comment, doa, dod from updation_detail_log WHERE completed is NULL and error is NULL and hos_id = 'inamdar' """  # if runno = '0'->all

    if runno == '1':
      query = """SELECT runno,insurerid,process,emailsubject,date,file_path,hos_id,preauthid,amount,status,lettertime,policyno,memberid,row_no,comment, doa, dod from updation_detail_log WHERE completed is NULL and error is NULL and hos_id = 'noble' """  # if runno = '0'->all
    elif runno == '2':
        query = """SELECT runno,insurerid,process,emailsubject,date,file_path,hos_id,preauthid,amount,status,lettertime,policyno,memberid,row_no,comment, doa, dod from updation_detail_log WHERE completed is NULL and error is NULL and hos_id = 'ils' """  # if runno = '0'->all
    elif runno == '3':
        query = """SELECT runno,insurerid,process,emailsubject,date,file_path,hos_id,preauthid,amount,status,lettertime,policyno,memberid,row_no,comment, doa, dod from updation_detail_log WHERE completed is NULL and error is NULL and hos_id = 'ils_dumdum' """  # if runno = '0'->all
    else:
      query = """SELECT runno,insurerid,process,emailsubject,`date`,file_path,hos_id,preauthid,amount,`status`, \
          lettertime,policyno,memberid,row_no,comment, doa, dod from updation_detail_log WHERE error IS NULL and completed is NULL"""

    # print(query)
    # log_api_data('query', query)
    cur.execute(query)
    data = cur.fetchall()
    if data:
      myList = []
      for row in data:
        localDic = {}
        localDic['runno'] = row[0]
        localDic['insurerid'] = row[1]
        query = """SELECT IC_ID from IC_name WHERE IC_name ='%s' """ % row[1]
        cur.execute(query)
        dat = cur.fetchall()
        if dat:
          for ro in dat:
            localDic['ins_id'] = ro[0]
        localDic['process'] = row[2]
        localDic['emailsubject'] = row[3]
        localDic['date'] = str(row[4])
        localDic['file_path'] = row[5]
        localDic['hos_id'] = row[6]
        localDic['preauthid'] = row[7]
        localDic['amount'] = row[8]
        localDic['status'] = row[9]
        localDic['lettertime'] = row[10]
        localDic['policyno'] = row[11]
        localDic['memberid'] = row[12]
        localDic['row_no'] = row[13]
        localDic['comment'] = row[14]
        localDic['doa'] = row[15]
        localDic['dod'] = row[16]

        url = request.url_root
        url = url + 'api/downloadfile?filename='
        url = url + str(row[5])
        localDic['file_path'] = url

        if localDic['memberid'] != None or localDic['preauthid'] != None or localDic['policyno'] != None or localDic[
          'comment'] != None:
          # if localDic['hos_id'] == 'Max PPT':
          #   url = 'https://vnusoftware.com/iclaimmax/api/preauth/vnupatientsearch'
          # else:
          #   url = 'https://vnusoftware.com/iclaimportal/api/preauth/vnupatientsearch'
          url = get_api_url(localDic['hos_id'], 'getupdateDetailsLog')
          payload = {
            'memberid': localDic['memberid'],
            'preauthid': localDic['preauthid'],
            'policyno': localDic['policyno'],
            'comment': localDic['comment']
          }

          try:
            temp = {}

            for i, j in payload.items():
              # print(i, j)
              if j == None:
                temp[i] = ''
              else:
                temp[i] = j

            payload = temp

            response = requests.post(url, data=payload)
            result = response.json()
            # print(result)
            log_data(payload=payload, url=url, response=response)

            if result['status'] == '1':
              localDic['searchdata'] = result['searchdata']
            else:
              localDic["searchdata"] = {
                "refno": "",
                "approve_amount": "",
                "current_status": "",
                "process": "",
                "InsurerId": "",
                "insname": "",
                "Cumulative_flag": ""
              }
          except Exception as e:
            # log_data(payload=payload, url=url, response=response)
            log_exceptions()
            # print(e)
            # log_api_data('e', e)
            localDic["searchdata"] = {
              "refno": "",
              "approve_amount": "",
              "current_status": "",
              "process": "",
              "InsurerId": "",
              "insname": ""
            }
        else:
          localDic["searchdata"] = {
            "refno": "",
            "approve_amount": "",
            "current_status": "",
            "process": "",
            "InsurerId": "",
            "insname": ""
          }

        myList.append(localDic)

      return jsonify({
        'status': 'pass',
        'data': (myList)
      })
    else:
      localDic = {}
      localDic['runno'] = ''
      localDic['insurerid'] = ''
      localDic['process'] = ''
      localDic['emailsubject'] = ''
      localDic['date'] = ''
      localDic['file_path'] = ''
      localDic['hos_id'] = ''
      localDic['preauthid'] = ''
      localDic['amount'] = ''
      localDic['status'] = ''
      localDic['lettertime'] = ''
      localDic['policyno'] = ''
      localDic['memberid'] = ''
      localDic['row_no'] = ''
      localDic['comment'] = ''
      localDic['doa'] = ''
      localDic['dod'] = ''
      return jsonify({'status': 'fail',
                      'data': (localDic)})


  except Exception as e:
    log_exceptions()
    # print(e)
    # log_api_data('e', e)
    return jsonify({
      'status': 'failure',
      'reason': e.__str__()
    })


@app.route("/api/downloadfile")
def get_file():
    """Download a file."""
    if request.args['filename'] != None:
        filepath=request.args['filename']
        print("path=",filepath)
        #log_api_data('filepath', filepath)
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
  formparameter = {}
  formparameter['interval'] = (request.form["intervel"])
  formparameter['fromtime'] = request.form["fromtime"]
  formparameter['totime'] = request.form["totime"]
  formparameter['id'] = request.form["id"]
  formparameter['hid'] = request.form["hid"]
  formparameter['count'] = request.form["count"]
  formparameter['pid'] = request.form["pid"]
  formparameter['nowtime'] = akdatetime.now()
  formparameter['formnowtime'] = request.form['formnowtime']
  # formparameter['datetime'] = request.form['datetime']

  with open('nowtime.txt', 'a') as f:
    f.write('form ' + str(formparameter['nowtime']) + '\n')

  try:
    if formparameter['formnowtime'] != '' and formparameter['interval'] != '':
      formparameter['nowtime'] = akdatetime.strptime(formparameter['formnowtime'], '%d/%m/%Y %H:%M:%S')
  except Exception as e:
    log_exceptions()
    pass

  #formparameter['interval'] = 'interval1'
  #if formparameter['interval'] == 'interval1':
  #  deltaMessage()

  if formparameter['interval'] != '':
    # if now time is given from screen, then it will be considered, else akdatetime.now along with date
    print("Scheduler is called.")
    sched = BackgroundScheduler(daemon=False)
    sched.add_job(add1, 'interval', seconds=10, max_instances=1)
    sched.start()
  else:
    add1(formparameter)
  return "success"


# @app.route('/add', methods=["POST", "GET"])
def add1():
  with mysql.connector.connect(**conn_data) as mydb:
    cur = mydb.cursor()
    q1 = f"insert into runs (date) value ('{str(datetime.datetime.now())}');"
    cur.execute(q1)
    mydb.commit()
  # # from datetime import datetime as akdatetime
  intervel = 10
  # nowtime = formparameter['nowtime']
  #
  # with open('nowtime.txt', 'a') as f:
  #   f.write('add1 ' + str(formparameter['nowtime']) + '\n')
  # print("Starting time")
  # print(nowtime)
  #
  # if intervel == '':
  #   fromtime = formparameter["fromtime"]
  #   totime = formparameter["totime"]
  #   id = formparameter["id"]
  #   hid = formparameter["hid"]
  #   cou = formparameter["count"]
  #   proces = formparameter["pid"]
  #   nowtime = formparameter['nowtime']
  #
  # with mysql.connector.connect(**conn_data) as mydb:
  #   cur = mydb.cursor()
  #   q = "SELECT COUNT(*) FROM updation_log;"
  #   cur.execute(q)
  #   r = cur.fetchall()
  # print(r)
  # # log_api_data('r', r)
  # max_row = r[0][0]
  row_count_1 = 1
  # #subprocess.run(["python", "updation.py", "0", "max1", "1", str(row_count_1)])
  # #subprocess.run(["python", "updation.py", "0", "max", "2", str(today)])
  # #subprocess.run(["python", "updation.py", "0", "max", "3", str(now)])
  #
  # if intervel == '':
  #   datetimeobject = datetime.datetime.strptime(fromtime, '%Y-%m-%d')
  #   fromtime = str(datetimeobject.strftime('%d-%b-%Y'))
  #   datetimeobject = datetime.datetime.strptime(totime, '%Y-%m-%d')
  #   totime = str(datetimeobject.strftime('%d-%b-%Y'))
  #
  #   msg = fromtime + " TO " + totime
  #   if (intervel != '' and fromtime == '' and totime == ''):
  #     mode = "intervel"
  #   elif (intervel == '' and fromtime != '' and totime != ''):
  #     mode = "RANGE"
  #   else:
  #     mode = "ERROR"
  #   a = mode + "|" + intervel + "|" + fromtime + "|" + totime + "|" + id + "|" + hid
  # else:
  #   mode = "intervel"
  #   a = mode + "|" + intervel
  #   hid = 'all'
  #
  # file = open("sample.txt", "w")
  # file.write(a)
  # file.close()
  #
  # if hid == 'all':
  #   q = "SELECT * FROM hospital WHERE active='X'"
  # else:
  #   q = "SELECT * FROM hospital WHERE id=" + hid
  # with mysql.connector.connect(**conn_data) as mydb:
  #   cur = mydb.cursor()
  #   cur.execute(q + ';')
  #   r_credentials = cur.fetchall()
  #
  # for i in range(0, len(r_credentials)):
  #   # print(r_credentials)
  #   email = r_credentials[i][2]
  #   password = r_credentials[i][3]
  #   server = r_credentials[i][4]
  #   inbox = r_credentials[i][5]
  #   mail = imaplib.IMAP4_SSL(server)
  #   hid = r_credentials[i][1]
  #
  #   f = None
  #   f = open(hid + ".txt", "r")
  #   c = f.read()
  #   fg = c.split()
  #   f = open(hid + ".txt", "a+")
  #   f.close()
  #   try:
  #     mail.login(email, password)
  #     # print(mail.list_folders())
  #     #subprocess.run(["python", "updation.py", "0", "max", "6", 'YES'])
  #   except Exception as e:
  #     log_exceptions()
  #     #subprocess.run(["python", "updation.py", "0", "max", "6", 'NO'])
  #
  #   mail.select(inbox, readonly=True)
  #
  #   if (mode == "intervel"):
  #     type, mail.data = mail.search(None, '(since ' + str(tg[-1]) + ')')
  #     mail.ids = mail.data[0]
  #     mail.id_list = mail.ids.split()
  #   elif mode == "RANGE":
  #     q = "SELECT * FROM email_ids WHERE IC==" + id
  #     templist = ['settlement']
  #     if proces == 'all':
  #       tempidlist = []
  #       icidlist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
  #                   28, 29, 30, 31, 32]
  #
  #       for id in icidlist:
  #         id = str(id)
  #         for i in templist:
  #           b = "SELECT email_master.subject ,email_master.table_name, email_ids.email_ids, email_ids.IC FROM email_master JOIN email_ids  ON email_master.ic_id=email_ids.IC WHERE email_master.table_name = '" + i + "' and email_master.ic_id= '" + id + "' "
  #           print(b)
  #           cur.execute(b)
  #           r = cur.fetchall()
  #           mail.id_list_1 = []
  #           for row in r:
  #             ic_email = row[2]
  #             ic_subject = row[0]
  #             if (mode == "RANGE"):
  #               print(ic_email + fromtime + totime)
  #               type, mail.data = mail.search(None,
  #                                             '(FROM ' + ic_email + ' since ' + fromtime + ' before ' + totime + ' (SUBJECT "%s"))' % ic_subject)
  #               mail.ids = mail.data[0]  # data is a list.
  #               mycount = len(mail.data[0].split())
  #
  #               if mycount > 0:
  #                 mail.id_list_1.append(mail.ids.split())
  #
  #                 coun = int(cou)
  #                 try:
  #                   mail.id_list_1 = list(chain.from_iterable(mail.id_list_1))
  #                 except TypeError:
  #                   log_exceptions()
  #                   pass
  #                 mail.id_list = mail.id_list_1
  #                 if (len(mail.id_list) > coun):
  #                   mail.id_list = mail.id_list[len(mail.id_list) - coun - 1:-1]
  #                 for i in mail.id_list:
  #                   tempidlist.append(i)
  #         mail.id_list = tempidlist
  #     elif id == '17' and proces != 'settlement':
  #       b = "SELECT * FROM email_ids  WHERE IC= '" + id + "' "
  #       print(b)
  #       cur.execute(b)
  #       r = cur.fetchall()
  #       mail.id_list_1 = []
  #       for row in r:
  #         ic_email = row[1]
  #       print(ic_email + fromtime + totime)
  #       type, mail.data = mail.search(None, '(FROM ' + ic_email + ' since ' + fromtime + ' before ' + totime + ')')
  #       mail.ids = mail.data[0]  # data is a list.
  #       mycount = len(mail.data[0].split())
  #       if mycount > 0:
  #         mail.id_list_1.append(mail.ids.split())
  #         coun = int(cou)
  #         mail.id_list_1 = list(chain.from_iterable(mail.id_list_1))
  #         mail.id_list = mail.id_list_1
  #         if (len(mail.id_list) > coun):
  #           mail.id_list = mail.id_list[len(mail.id_list) - coun - 1:-1]
  #         print("mail.id_list")
  #         print(mail.id_list)
  #
  #
  #
  #     else:
  #       b = "SELECT email_master.subject ,email_master.table_name, email_ids.email_ids, email_ids.IC FROM email_master JOIN email_ids  ON email_master.ic_id=email_ids.IC WHERE email_master.table_name = '" + proces + "' and email_master.ic_id= '" + id + "' "
  #       print(b)
  #       cur.execute(b)
  #       r = cur.fetchall()
  #       mail.id_list_1 = []
  #       for row in r:
  #         ic_email = row[2]
  #         ic_subject = row[0]
  #         if (mode == "RANGE"):
  #           print(ic_email + fromtime + totime)
  #           type, mail.data = mail.search(
  #             None,
  #             '(FROM ' + ic_email + ' since ' + fromtime + ' before ' + totime + ' (SUBJECT "%s"))' % ic_subject)
  #           mail.ids = mail.data[0]  # data is a list.
  #           mycount = len(mail.data[0].split())
  #           if mycount > 0:
  #             # mail.id_list_2=mail.ids.split()
  #             # mail.ids = mail.data[0]
  #             mail.id_list_1.append(mail.ids.split())
  #             # print("mail_id=",mail.id_list_1)
  #             coun = int(cou)
  #       if (mode == "RANGE"):
  #         mail.id_list_1 = list(chain.from_iterable(mail.id_list_1))
  #         mail.id_list = mail.id_list_1
  #         if (len(mail.id_list) > coun):
  #           mail.id_list = mail.id_list[len(mail.id_list) - coun - 1:-1]
  #   print("mail.id_list")
  #   ##############################akshay
  #   blist = []
  #   for i in mail.id_list:
  #     if isinstance(i, bytes):
  #       blist.append(i)
  #   mail.id_list = blist
  #
  #   ##############################akshayend
  #   mail.id_list = sorted(mail.id_list)
  #
  #   # if (mode == "intervel"):
  #   #   mail.id_list, call_to_cmp_time = cmp_to_subject_function(hid, mail, mail.id_list, formparameter['formnowtime'])
  #   #   if call_to_cmp_time is not None:
  #   #     mail.id_list = mailid_time_subject(mail.id_list, mail, hid, formparameter['formnowtime'])
  #   print(mail.id_list)
  #   if (mode == "intervel"):
  #     with open('nowtime.txt', 'a') as f:
  #       f.write('processinterval ' + str(nowtime) + '\n')
  #     # to call process_copy for those entries of graphAPI table with  completed = None or blank
  #     # process(now, today, mail, row_count_1, hid, fg, mode, nowtime)
  #     result = []
  #     with mysql.connector.connect(**conn_data) as con:
  #       cur = con.cursor()
  #       q = "select * from graphApi where completed=''"
  #       cur.execute(q)
  #       result = cur.fetchall()
  #     with mysql.connector.connect(**conn_data) as con:
  #       cur = con.cursor()
  #       q1 = "update graphApi set completed='A' where completed=''"
  #       cur.execute(q1)
  #       con.commit()
  #       # q1 = "update graphApi set completed='A' where completed=''"
  #       # cur.execute(q1)
  #       if result == []:
  #         return str([])
  #     # process_copy_parallel(result, now, today, row_count_1)
  #     process_copy(result, now, today, row_count_1)
  #
  #   # sort ascending order mail.id_list
  #   if len(mail.id_list) > 0 and mode == 'RANGE':
  #     # print(int(mail.id_list[-1].decode()),fg[-1],int(mail.id_list[-1].decode()) > int(fg[-1]))
  #     if len(fg) == 0 or int(mail.id_list[-1].decode()) > int(fg[-1]):
  #       #subprocess.run(["python", "updation.py", "0",
  #                       # "max", "7", str(len(mail.id_list))])
  #
  #       print('new_mail')
  #       for j in range(0, len(mail.id_list)):
  #         if len(fg) == 0 or int(mail.id_list[j].decode()) > int(fg[-1]):
  #           temp = str(mail.id_list[j])
  #           f = open(hid + ".txt", "a+")
  #           f.write(temp[2:-1] + '\n')
  #           f.close()
  #         if id == "17" and proces != 'settlement':
  #           proces_park(now, today, mail, row_count_1, hid, fg, mode, nowtime)
  #         else:
  #           with open('nowtime.txt', 'a') as f:
  #             f.write('processinterval ' + str(nowtime) + '\n')
  #           process(now, today, mail, row_count_1, hid, fg, mode, nowtime)
  #
  #     else:
  #       #subprocess.run(["python", "updation.py", "0", "max", "7", '0'])
  #       pass
  #     subprocess.run(
  #       ["python", "updation.py", "0", "max", "8", str(s_r)])
  #   pass
  now = datetime.datetime.now()
  today = datetime.date.today()
  today = today.strftime('%d-%b-%Y')
  r_credentials = []
  if r_credentials == []:
    result = []
    with mysql.connector.connect(**conn_data) as con:
      cur = con.cursor()
      q = "select * from graphApi where completed=''"
      cur.execute(q)
      result = cur.fetchall()
      if result == []:
        return str([])
    # process_copy_parallel(result, now, today, row_count_1)
    process_copy(result, now, today, row_count_1)
    # d = 0
    # with mysql.connector.connect(**conn_data) as con:
    #   cur = con.cursor()
    #   q = "select * from graphApi where completed='D'"
    #   cur.execute(q)
    #   result = cur.fetchall()
    #   if len(result) > 0:
    #     d = 1
    # with mysql.connector.connect(**conn_data) as con:
    #   cur = con.cursor()
    #   q = "update graphApi set completed = 'F' where completed='D' or completed='E'"
    #   cur.execute(q)
    #   con.commit()
    # if d == 1:
    #   process_copy(result, now, today, row_count_1)
  fo = open("defualt_time_read.txt", "a+")
  if (str(today) != str(tg[-1])):
    fo.write(str(today) + '\n')
  now = datetime.datetime.now()
  today = datetime.date.today()
  today = today.strftime('%d-%b-%Y')
  #subprocess.run(["python", "updation.py", "0", "max", "4", str(today)])
  #subprocess.run(["python", "updation.py", "0", "max", "5", str(now)])
  # return str(msg)
  print(f"----Job is scheduled for every ", intervel, " seconds")

def inamdar(formparameter):
  with mysql.connector.connect(**conn_data) as mydb:
    cur = mydb.cursor()
    q1 = f"insert into runs (date) value ('{str(datetime.datetime.now())}');"
    cur.execute(q1)
    mydb.commit()
  # # from datetime import datetime as akdatetime
  intervel = formparameter["interval"]
  nowtime = formparameter['nowtime']
  #
  # with open('nowtime.txt', 'a') as f:
  #   f.write('add1 ' + str(formparameter['nowtime']) + '\n')
  # print("Starting time")
  # print(nowtime)
  #
  # if intervel == '':
  #   fromtime = formparameter["fromtime"]
  #   totime = formparameter["totime"]
  #   id = formparameter["id"]
  #   hid = formparameter["hid"]
  #   cou = formparameter["count"]
  #   proces = formparameter["pid"]
  #   nowtime = formparameter['nowtime']
  #
  # with mysql.connector.connect(**conn_data) as mydb:
  #   cur = mydb.cursor()
  #   q = "SELECT COUNT(*) FROM updation_log;"
  #   cur.execute(q)
  #   r = cur.fetchall()
  # print(r)
  # # log_api_data('r', r)
  # max_row = r[0][0]
  row_count_1 = 1
  now = datetime.datetime.now()
  today = datetime.date.today()
  today = today.strftime('%d-%b-%Y')
  r_credentials = []
  if r_credentials == []:
    result = []
    with mysql.connector.connect(**conn_data) as con:
      cur = con.cursor()
      q = "select * from graphApi where completed=''"
      cur.execute(q)
      result = cur.fetchall()
      if result == []:
        return str([])
    # process_copy_parallel(result, now, today, row_count_1)
    process_copy(result, now, today, row_count_1)
    # d = 0
    # with mysql.connector.connect(**conn_data) as con:
    #   cur = con.cursor()
    #   q = "select * from graphApi where completed='D'"
    #   cur.execute(q)
    #   result = cur.fetchall()
    #   if len(result) > 0:
    #     d = 1
    # with mysql.connector.connect(**conn_data) as con:
    #   cur = con.cursor()
    #   q = "update graphApi set completed = 'F' where completed='D' or completed='E'"
    #   cur.execute(q)
    #   con.commit()
    # if d == 1:
    #   process_copy(result, now, today, row_count_1)
  fo = open("defualt_time_read.txt", "a+")
  if (str(today) != str(tg[-1])):
    fo.write(str(today) + '\n')
  now = datetime.datetime.now()
  today = datetime.date.today()
  today = today.strftime('%d-%b-%Y')
  #subprocess.run(["python", "updation.py", "0", "max", "4", str(today)])
  #subprocess.run(["python", "updation.py", "0", "max", "5", str(now)])
  # return str(msg)
  print(f"----Job is scheduled for every ", str(intervel), " seconds")

def proces_park(now, today, mail, row_count_1, hid, fg, mode, nowtime):
  for i in range(0, len(mail.id_list)):
    if len(fg) == 0 or int(mail.id_list[i].decode()) > int(fg[-1]):
      temp = str(mail.id_list[i])
      # f = open("unread_mail.txt", "a+")
      # f.write(temp[2:-1]+'\n')
      # f.close()
      mail.latest_email_id = mail.id_list[i]  # get the latest
      print(mail.latest_email_id)
      mail.latest_email_id = mail.latest_email_id
      print("________________")
      print(mail.latest_email_id)
      try:
        mail.result, mail.data1 = mail.fetch(mail.latest_email_id, "(RFC822)")
      except Exception as e:
        log_exceptions()
        continue
      try:
        mail.raw_email = mail.data1[0][1].decode('utf-8')
      except UnicodeDecodeError:
        try:
          mail.raw_email = mail.data1[0][1].decode('ISO-8859-1')
        except UnicodeDecodeError:
          try:
            mail.raw_email = mail.data1[0][1].decode('ascii')
          except UnicodeDecodeError:
            pass
      mail.email_message = email.message_from_string(mail.raw_email)
      from_email = mail.email_message['From']
      tempvar = mail.email_message['Subject']

      print(from_email)
      l_time = mail.email_message['Date']
      # if intervel, then compare system date and time with mail ids date and time..if system date is greater, then continue, else proceed further
      l_time = ifutc_to_indian(l_time)

      if mode != 'RANGE':
        try:
          a = l_time.replace(',', '')
          with open('l_time.txt', 'a+') as temp:
            temp.write(+a + '\n')
          b = '%a %d %b %Y %H:%M:%S %z'
          # d = '%a %d %b %Y %H:%M:%S %z'
          c = '%d %b %Y %H:%M:%S %z'
          india = timezone('Asia/Kolkata')
          try:
            datetime_object = akdatetime.strptime(a, b)
          except:
            log_exceptions()
            datetime_object = akdatetime.strptime(a, c)

          datetime_object = datetime_object.astimezone(india)
          datetime_object = datetime_object.replace(tzinfo=None)
          with open('nowtime.txt', 'a') as f:
            f.write('inrange ' + str(nowtime) + '\n')
          if datetime_object.year > nowtime.year or datetime_object.month > nowtime.month or datetime_object.day > nowtime.day:
            pass
          else:
            if datetime_object.year < nowtime.year:
              continue
            if datetime_object.month < nowtime.month:
              continue
            if datetime_object.day < nowtime.day:
              continue
            if datetime_object.hour < nowtime.hour:
              continue
            if datetime_object.hour <= nowtime.hour and datetime_object.minute < nowtime.minute:
              continue
        except Exception as e:
          log_exceptions()
          pass

      w = l_time.find(',') + 1
      g = l_time[w:]
      u = g.find('+') + w
      s = l_time[w:u]
      s = s.split(' ')
      while ("" in s):
        s.remove("")
        # print(s)
      if (len(s) == 4):
        t = s[0] + ' ' + s[1] + ' ' + s[2] + ' ' + s[3]

        d = datetime.datetime.strptime(t, '%d %b %Y %H:%M:%S')
        l_time = d.strftime('%d/%m/%Y %H:%M:%S')
      else:
        l_time = mail.email_message['Date']
        l_time = date_parser.parse(ifutc_to_indian(l_time)).strftime('%d/%m/%Y %H:%M:%S')
      temp_email = from_email
      if temp_email.find("<") != -1:
        temp_w = temp_email.find("<")
        temp_w = temp_w + 1
        from_email = temp_email[temp_w:-1]
      else:
        from_email = temp_email
      subject = mail.email_message['Subject']
      print(subject)
      subprocess.run(["python", "foldercheck.py", ("Park")])
      download_pdf(s_r, mail, "Park", "General", row_count_1, subject, hid)


def process(now, today, mail, row_count_1, hid, fg, mode, nowtime):
  for i in range(0, len(mail.id_list)):
    if len(fg) == 0 or int(mail.id_list[i].decode()) > int(fg[-1]):
      temp = str(mail.id_list[i])
      # f = open("unread_mail.txt", "a+")
      # f.write(temp[2:-1]+'\n')
      # f.close()
      mail.latest_email_id = mail.id_list[i]  # get the latest
      print(mail.latest_email_id)
      mail.latest_email_id = mail.latest_email_id
      print("________________")
      print(mail.latest_email_id)
      try:
        mail.result, mail.data1 = mail.fetch(mail.latest_email_id, "(RFC822)")
        try:
          mail.raw_email = mail.data1[0][1].decode('utf-8')
        except UnicodeDecodeError:
          try:
            mail.raw_email = mail.data1[0][1].decode('ISO-8859-1')
          except UnicodeDecodeError:
            try:
              mail.raw_email = mail.data1[0][1].decode('ascii')
            except UnicodeDecodeError:
              pass
      except Exception as e:
        try:
          if mail.data1[0][1] is None:
            log_exceptions(mailid='None', hid=hid)
          else:
            log_exceptions(mailid=mail.data1[0][1], hid=hid)
        except:
          pass
        continue

      mail.email_message = email.message_from_string(mail.raw_email)
      from_email = mail.email_message['From']
      print(from_email)
      l_time = mail.email_message['Date']
      l_time = ifutc_to_indian(l_time)

      if mode != 'RANGE':
        try:
          a = l_time.replace(',', '')
          with open('l_time.txt', 'a+') as temp:
            temp.write(a + '\n')
          b = '%a %d %b %Y %H:%M:%S %z'
          # d = '%a %d %b %Y %H:%M:%S %z'
          c = '%d %b %Y %H:%M:%S %z'
          india = pytz.timezone('Asia/Kolkata')
          try:
            datetime_object = akdatetime.strptime(a, b)
          except:
            log_exceptions()
            datetime_object = akdatetime.strptime(a, c)

          datetime_object = datetime_object.astimezone(india)
          datetime_object = datetime_object.replace(tzinfo=None)
          with open('nowtime.txt', 'a') as f:
            f.write('inrange ' + str(nowtime) + '\n')
          if datetime_object.year > nowtime.year or datetime_object.month > nowtime.month or datetime_object.day > nowtime.day:
            pass
          else:
            if datetime_object.year < nowtime.year:
              continue
            if datetime_object.month < nowtime.month:
              continue
            if datetime_object.day < nowtime.day:
              continue
            if datetime_object.hour < nowtime.hour:
              continue
            if datetime_object.hour <= nowtime.hour and datetime_object.minute < nowtime.minute:
              continue
        except Exception as e:
          log_exceptions()
          pass

      w = l_time.find(',') + 1
      g = l_time[w:]
      u = g.find('+') + w
      s = l_time[w:u]
      s = s.split(' ')
      while ("" in s):
        s.remove("")
        # print(s)
      if (len(s) == 4):
        t = s[0] + ' ' + s[1] + ' ' + s[2] + ' ' + s[3]

        d = datetime.datetime.strptime(t, '%d %b %Y %H:%M:%S')
        l_time = d.strftime('%d/%m/%Y %H:%M:%S')
      else:
        l_time = mail.email_message['Date']
        l_time = date_parser.parse(ifutc_to_indian(l_time)).strftime('%d/%m/%Y %H:%M:%S')
      temp_email = from_email
      if temp_email.find("<") != -1:
        temp_w = temp_email.find("<")
        temp_w = temp_w + 1
        from_email = temp_email[temp_w:-1]
      else:
        from_email = temp_email
      subject = mail.email_message['Subject']
      if subject is None:
        subject = ' '
      print(subject)
      # l_time = time_fun_two(l_time)
      if subject.find('UTF') != -1:
        subject = decode_header(mail.email_message['Subject'])
        subject = subject[0]
        subject = subject[0].decode()
      elif subject.find('utf') != -1:
        subject = decode_header(mail.email_message['Subject'])
        subject = subject[0]
        subject = subject[0].decode()
      subject = subject.replace("\r", "")
      subject = subject.replace("\n", "")
      print(subject)
      print("++++++++++++")
      print(from_email)
      # function to check whether 'subject', 'l_time' is found in  dbsubject and dbdate;if found, continue
      if check_if_sub_and_ltime_exist(subject, l_time):
        continue
      with mysql.connector.connect(**conn_data) as con:
        xyz = 10
        cur = con.cursor()
        try:
          b = "SELECT IC_name.IC ,IC_name.IC_name, email_ids.email_ids FROM IC_name JOIN email_ids  ON IC_name.IC=email_ids.IC WHERE email_ids.email_ids = '" + from_email + "'"
          print(b)
          cur.execute(b)
        except Exception as e:
          log_exceptions()
          continue
        r = cur.fetchall()
        if (len(r) > 0):
          id = str(r[0][0])
          ic_name = r[0][1]
          subprocess.run(["python", "foldercheck.py", (ic_name)])
          ic_emal_id = r[0][2]
          b = "SELECT * FROM email_master WHERE ic_id = " + id
          cur.execute(b)
          r = cur.fetchall()
          flag = "false"
          if (len(r) > 0):
            for row in r:
              subject_result = row[1]
              table_name = row[2]
              if id == "35" and table_name != 'settlement':
                download_pdf(s_r, mail, "alankit", "General", row_count_1, subject, hid, l_time)
                flag = "true"
                break
              if id == "17" and table_name != 'settlement':
                download_pdf(s_r, mail, "Park", "General", row_count_1, subject, hid, l_time)
                flag = "true"
                break
              if subject.find(subject_result) != -1:  # and ic_name!='star' :
                if subject.find('Denial') != -1 or subject.find('REJECTED') != -1 or subject.find('Rejection') != -1:
                  table_name = 'denial'
                if subject.find('Query') != -1:
                  table_name = 'query'
                if ic_name == 'fhpl' and subject.find('Patient Name') != -1 and subject.find(
                  'Approval') == -1 and subject.find('Pending') == -1 and subject.find('Reject') == -1 and subject.find(
                  'Settlement') == -1:
                  table_name = 'ack'
                  if subject.find('Approv') != -1 or subject.find('Approval') != -1 or subject.find('Approved') != -1:
                    table_name = 'preauth'
                  if subject.find('Final') != -1:
                    table_name = 'final'
                  if subject.find('Pending') != -1 or subject.find('Query') != -1:
                    table_name = 'query'
                  if subject.find('Reject') != -1 or subject.find('Rejected') != -1 or subject.find('Rejection') != -1:
                    table_name = 'denial'
                  if subject.find('Settlement') != -1:
                    table_name = 'settlement'
                download_pdf(s_r, mail, ic_name, table_name, row_count_1, subject, hid, l_time)
                flag = "true"
                break
              '''
              elif subject.find(subject_result)!=-1 and ic_name=='star' and table_name == 'settlement':

                  if subject.find('Rejection')!=-1:
                    table_name = 'denial'
                  if subject.find('Query')!=-1:
                    table_name = 'query'
                  if table_name == 'query' or table_name=='denial':
                    download_pdf(s_r,mail,ic_name,table_name,row_count_1,subject,hid)
                    flag="true"
                    break
                  #subprocess.run(["python", "updation.py","2","max1","1",str(row_count_1)])
                  #subprocess.run(["python", "updation.py","2","max","2",'star'])
                  #subprocess.run(["python", "updation.py","2","max","4",str(now)])
                  #subprocess.run(["python", "updation.py","2","max","8",l_time])
                  #subprocess.run(["python", "updation.py","2","max","7", subject])
                  #subprocess.run(["python", "updation.py","2","max","17",str(mail.email_message['From'])])
                  ##subprocess.run(["python", "updation.py","2","max","15",str('subject not known')])
                  #subprocess.run(["python", "updation.py","2","max","20",str(mail.latest_email_id)[2:-1]])
                  #subprocess.run(["python", "updation.py","1","max","21",hid])
                  ##subprocess.run(["python", "updation.py","1","max","15",'error while downloading'])

                  star_subject=mail.email_message['Subject']
                  w=star_subject.find('-')
                  ccn=star_subject[:w-1]
                  #for table_name = settlement, call main.py and based on subject , decide insurer
                  if table_name == 'settlement':
                    flag="true"
                    uid=mail.latest_email_id.decode()
                    if 'Intimation' in subject:
                      subprocess.run(["python", "main.py"," "," ","big",hid,uid,star_subject])
                      #subprocess.run(["python", "updation.py","1","max","3",'settlement_big'])
                      break
                    else:
                      subprocess.run(["python", "main.py",' ',' ',"small",hid,uid,star_subject])
                      #subprocess.run(["python", "updation.py","1","max","3",'settlement_small'])
                      break
                  else:
                    flag="true"
                    #subprocess.run(["python", "updation.py","1","max","3",table_name])
                    subprocess.run(["python", "star_download.py",ccn,star_subject,l_time,str(row_count_1),table_name,hid])
                    break
              '''

            if (flag == "true"):
              print(subject)
            else:
              print(subject, "=", subject_result)

              # NEED to raise error subject not known
              #subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
              #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
              #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
              now = datetime.datetime.now()
              #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
              #subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
              #subprocess.run(["python", "updation.py", "2", "max", "15", str('subject not known')])
              #subprocess.run(["python", "updation.py", "2", "max", "20", str(mail.latest_email_id)[2:-1]])
              #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
              subprocess.run(["python", "sms_api.py", str('Updation failed for ' + mail.email_message['Subject'])])
              add_time_diff()
          else:
            # need to raise error if no subject
            print(subject)
            #subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
            #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
            #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
            now = datetime.datetime.now()
            #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
            #subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
            #subprocess.run(["python", "updation.py", "2", "max", "20", str(mail.latest_email_id)[2:-1]])
            #subprocess.run(["python", "updation.py", "2", "max", "15", str('No subject found in database ')])
            #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
            subprocess.run(
              ["python", "sms_api.py", str('No subject found in database ' + mail.email_message['Subject'])])
            add_time_diff()

        else:
          # need to raise error for invalid email id
          print("invalid email " + from_email)
          #subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
          #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
          now = datetime.datetime.now()
          #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
          #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
          #subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
          #subprocess.run(["python", "updation.py", "2", "max", "15", str('No email id found in database ')])
          #subprocess.run(["python", "updation.py", "2", "max", "20", str(mail.latest_email_id)[2:-1]])
          subprocess.run(["python", "sms_api.py", str('No email id found in database  ' + subject)])
          add_time_diff()
          #subprocess.run(["python", "updation.py", "1", "max", "21", hid])

  fo = open("defualt_time_read.txt", "a+")
  if (str(today) != str(tg[-1])):
    fo.write(str(today) + '\n')
    now = datetime.datetime.now()
    today = datetime.date.today()
    today = today.strftime('%d-%b-%Y')

    #subprocess.run(["python", "updation.py", "0", "max", "4", str(today)])
    #subprocess.run(["python", "updation.py", "0", "max", "5", str(now)])
    print('done1')

def process_copy_parallel(result, now, today, row_count_1):
  sched = BackgroundScheduler(daemon=False,
                              executors={'processpool': ProcessPoolExecutor(max_workers=3)})
  for i in result:
    sched.add_job(process_copy, args=[[i], now, today, row_count_1], misfire_grace_time=10000)
  sched.start()

def process_copy(result,now,today,row_count_1):
  try:
    # today = datetime.date.today()
    # today = today.strftime('%d-%b-%Y')
    mail = ""
    #
    print('in process copy ',len(result), today, row_count_1)
    result_cnt, processed_cnt = len(result), 0
    for j, i in enumerate(result):
      try:
        with mysql.connector.connect(**conn_data) as con:
          cur = con.cursor()
          q1 = "insert into jobs values (%s, %s, %s);"
          data = (j, i[1], i[2])
          cur.execute(q1, data)
          con.commit()
        with mysql.connector.connect(**conn_data) as con:
          cur = con.cursor()
          q1 = "update graphApi set completed = 'p' where date = %s;"
          data = (i[2],)
          cur.execute(q1, data)
          con.commit()
      except:
        log_exceptions()
      print('in loop', len(i))
    #   today = datetime.date.today()
    #   today = today.strftime('%d-%b-%Y')
    #   with mysql.connector.connect(**conn_data) as con:
    #     cur = con.cursor()
    #     b = "SELECT COUNT (*) FROM updation_log"
    #     cur.execute(b)
    #     r = cur.fetchall()
    #     print(r)
    #     # log_api_data('r', r)
    #     max_row = r[0][0]
    #     row_count_1 = max_row + 1

      subject, l_time, files, from_email, hid, mail_id = i[1], i[2], i[4], i[6], 'Max PPT', i[0]
      subject = subject.replace("\r", "")
      subject = subject.replace("\n", "")
      try:
          with mysql.connector.connect(**conn_data) as con:
              cur = con.cursor()
              b = "SELECT email_ids FROM email_ids;"
              cur.execute(b)
              result_temp = cur.fetchall()
              if len(result_temp) > 0:
                  result_temp = [i[0] for i in result_temp]
                  if from_email in result_temp:
                      q1 = "update graphApi set completed = 'DD' where date = %s;"
                      data = (i[2],)
                      cur.execute(q1, data)
                      con.commit()
                      with open('logs/dd_queries.log', 'a') as temp_fp:
                          print(str(datetime.datetime.now()), str(cur.statement), file=temp_fp, sep=',')
      except:
          log_exceptions()
      if check_if_sub_and_ltime_exist(subject, l_time):
        continue
      try:
        with mysql.connector.connect(**conn_data) as con:
          xyz = 10
          cur = con.cursor()
          try:
            b = "SELECT IC_name.IC ,IC_name.IC_name, email_ids.email_ids FROM IC_name JOIN email_ids  ON IC_name.IC=email_ids.IC WHERE email_ids.email_ids = '" + from_email + "'"
            print(b)
            cur.execute(b)
          except Exception as e:
            log_exceptions()
            continue
          r = cur.fetchall()
          if (len(r) > 0):
            id = str(r[0][0])
            ic_name = r[0][1]
            subprocess.run(["python", "foldercheck.py", (ic_name)])
            ic_emal_id = r[0][2]
            b = "SELECT * FROM email_master WHERE ic_id = " + id
            cur.execute(b)
            r = cur.fetchall()
            flag = "false"
            if (len(r) > 0):
              for row in r:
                subject_result = row[1]
                table_name = row[2]
                if id == "35" and table_name != 'settlement':
                  download_pdf_copy(s_r, mail, "alankit", "General", row_count_1, subject, hid, l_time, files, mail_id, from_email)
                  flag = "true"
                  break
                if id == "17" and table_name != 'settlement':
                  download_pdf_copy(s_r, mail, "Park", "General", row_count_1, subject, hid, l_time, files, mail_id, from_email)
                  flag = "true"
                  break
                if subject.find(subject_result) != -1:  # and ic_name!='star' :
                  if subject.find('Denial') != -1 or subject.find('REJECTED') != -1 or subject.find('Rejection') != -1:
                    table_name = 'denial'
                  if subject.find('Query') != -1:
                    table_name = 'query'
                  if ic_name == 'fhpl' and subject.find('Patient Name') != -1 and subject.find(
                    'Approval') == -1 and subject.find('Pending') == -1 and subject.find('Reject') == -1 and subject.find(
                    'Settlement') == -1:
                    table_name = 'ack'
                    if subject.find('Approv') != -1 or subject.find('Approval') != -1 or subject.find('Approved') != -1:
                      table_name = 'preauth'
                    if subject.find('Final') != -1:
                      table_name = 'final'
                    if subject.find('Pending') != -1 or subject.find('Query') != -1:
                      table_name = 'query'
                    if subject.find('Reject') != -1 or subject.find('Rejected') != -1 or subject.find('Rejection') != -1:
                      table_name = 'denial'
                    if subject.find('Settlement') != -1:
                      table_name = 'settlement'
                  download_pdf_copy(s_r, mail, ic_name, table_name, row_count_1, subject, hid, l_time, files, mail_id, from_email)
                  flag = "true"
                  break
              if (flag == "true"):
                print(subject)
              else:
                print(subject, "=", subject_result)

                # NEED to raise error subject not known
                #subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                now = datetime.datetime.now()
                #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                #subprocess.run(["python", "updation.py", "2", "max", "17", str(from_email)])
                #subprocess.run(["python", "updation.py", "2", "max", "15", str('subject not known')])
                #subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
                #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
                subprocess.run(["python", "sms_api.py", str('Updation failed for ' + subject)])
                add_time_diff()
            else:
              # need to raise error if no subject
              print(subject)
              #subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
              #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
              #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
              now = datetime.datetime.now()
              #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
              #subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
              #subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
              #subprocess.run(["python", "updation.py", "2", "max", "15", str('No subject found in database ')])
              #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
              subprocess.run(
                ["python", "sms_api.py", 'No subject found in database ' + subject])
              add_time_diff()

          else:
            # need to raise error for invalid email id
            print("invalid email " + from_email)
            #subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
            #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
            now = datetime.datetime.now()
            #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
            #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
            #subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
            #subprocess.run(["python", "updation.py", "2", "max", "15", str('No email id found in database ')])
            #subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
            subprocess.run(["python", "sms_api.py", str('No email id found in database  ' + subject)])
            add_time_diff()
            #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
      except:
        log_exceptions()
    custom_log_data(filename="process_copy_stats", result_cnt=result_cnt, processed_cnt=processed_cnt)

    fo = open("defualt_time_read.txt", "a+")
    if (str(today) != str(tg[-1])):
      fo.write(str(today) + '\n')
      now = datetime.datetime.now()
      today = datetime.date.today()
      today = today.strftime('%d-%b-%Y')

      #subprocess.run(["python", "updation.py", "0", "max", "4", str(today)])
      #subprocess.run(["python", "updation.py", "0", "max", "5", str(now)])
      print('done1')
  except:
    log_exceptions()

def download_pdf_copy(s_r, mail, ins, ct, row_count_1, subject, hid, l_time, files, mail_id, sender):
  print("pdf downloading")
  now = datetime.datetime.now()
  dol = 0
  try:
    t_p = 0
    for fp in files.split(','):
      fp = os.path.split(fp)[1]
      # file name (complete path is  coming in fp, only filename sud come ---> akshay
      subprocess.run(["python", "foldercheck.py", (os.getcwd() + '/' + ins + '/attachments_pdf_' + ct)])
      detach_dir = (os.getcwd() + '/' + ins + '/attachments_pdf_' + ct + '/')
      if 'body.pdf' in fp:
        break
      if bool(fp):
        if (fp.find('MDI') != -1) and (fp.find('Query') == -1):
          continue
        if (fp.find('KYC') != -1):
          continue
        if (fp.find('image') != -1):
          continue
        if (fp.find('DECLARATION') != -1):
          continue
        if (fp.find('Declaration') != -1):
          continue
        if (fp.find('notification') != -1):
          continue
        if (fp.find('CLAIMGENIEPOSTER') != -1):
          continue
        if (fp.find('decla') != -1):
          continue
        else:
          t_p = 1
          if ins.find("Cholamandalams") != -1:
            w = subject.find(':') + 2
            jk = str(now)
            jk = jk.replace(' ', '_')
            filename = subject[w:]
            # print(filename)
            filepath = os.path.join(detach_dir, filename + '.pdf')
            ter = 1
            # print(filepath)
            while (path.exists(filepath)):
              filepath = os.path.join(detach_dir, filename + '(' + str(ter) + ').pdf')
              # print(filepath)
              ter += 1


          else:
            fil = fp
            fil = fil.replace("\r", "")
            fil = fil.replace("\n", "")
            fil = fil.replace("/", "")
            if fil.find("\r" or "\\r" or "\n" or "\\n") != -1:
              re.sub(r'\\r\\n', '', fil)
              if ins == 'Max_Bupa':
                fil = fil[:-11]
            fil = fil[:-4]
            fp = fil + '.pdf'
            filepath = os.path.join(detach_dir, fp)
          if ins == 'Raksha':
            filename = fp
            subject = subject.replace("\r", "")
            subject = subject.replace("\n", "")
            subprocess.run(["python", "raksha_test.py", str(filename), str(ct), subject])
            with mysql.connector.connect(**conn_data) as con:
              cur = con.cursor()
              q1 = "update graphApi set completed = 'R' where date = %s;"
              data = (l_time,)
              cur.execute(q1, data)
              con.commit()
          else:
            # try:
            #   fp2 = open(fp, "r")
            # except:
            #   pass
            #   fp2.close()
            # need to change code, sud be moved to appropriate folder, line 1869, remove html also--> akshay
            if isfile('../graph_api/new_attach/'+fp):
                copyfile('../graph_api/new_attach/'+fp, os.getcwd() + '/' + ins + '/attachments_pdf_' + ct + '/' +fp)
            else:
              fp = fp.replace('.pdf', '.PDF')
              if isfile('../graph_api/new_attach/' + fp):
                fp1 = fp.replace('.PDF', '.pdf')
                copyfile('../graph_api/new_attach/' + fp, os.getcwd() + '/' + ins + '/attachments_pdf_' + ct + '/' + fp1)
            break
            # fp = open(filepath, 'wb')
            # fp.write(mail.part.get_payload(decode=True))
            # fp.close()
    dol = 1

  except Exception as e:
    log_exceptions()

    #subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])

    s_r += 1
    #subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
    #subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
    #subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
    #subprocess.run(["python", "updation.py", "1", "max", "15", 'error while downloading'])

  try:
    if (t_p == 0):
      body_pdf = files.split(',')[0]
      if 'body.pdf' in body_pdf:
        subprocess.run(["python", "foldercheck.py", (os.getcwd() + '/' + ins + '/attachments_' + ct)])
        mypath = os.getcwd() + '/' + ins + '/attachments_' + ct
        try:
          temp_seq = str(max([int(splitext(f)[0]) for f in listdir(mypath) if isfile(join(mypath, f))]) + 1)
        except:
          temp_seq = get_fp_seq()
        copyfile(body_pdf, os.getcwd() + '/' + ins + '/attachments_' + ct + '/' + str(temp_seq) + splitext(os.path.split(fp)[1])[1])
        #rename file as per folder  sequence
        detach_dir = (os.getcwd() + '/' + ins + '/attachments_' + ct + '/')
        fp = str(temp_seq) + splitext(os.path.split(fp)[1])[1]
        filepath = os.path.join(detach_dir, fp)
        dol = 1
        #return 0
  except:
    log_exceptions()
  try:
    if (dol == 1):
      #subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
      try:
        if ct == 'settlement':
          with open('logs/letters.log', 'a') as tfp:
            print(hid, ins, l_time, filepath, sep=',', file=tfp)
          if 'Intimation No' in subject:
            ins = 'big'
          if 'STAR HEALTH AND ALLIED INSUR04239' in subject:
            ins = 'small'
          filepath = create_settlement_folder(hid, ins, l_time, filepath)
          try:
              with mysql.connector.connect(**conn_data) as con:
                  cur = con.cursor()
                  q = f"insert into settlement_mails (`id`,`subject`,`date`,`sys_time`,`attach_path`,`completed`,`sender`,`hospital`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                  data = (mail_id, subject, l_time, str(datetime.datetime.now()), filepath, '', sender, hid)
                  cur.execute(q, data)
                  q1 = f"update graphApi set completed = 'S' where date = %s and subject=%s;"
                  data1 = (l_time, subject)
                  cur.execute(q1, data1)
                  con.commit()
          except:
            log_exceptions()
        else:
          ins_file = ins + "_" + ct + ".py"
          if not os.path.exists(ins_file):
            send_sms(f"{ins_file} not exist")
          with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            q1 = "update graphApi set completed = 'D' where date = %s;"
            data = (l_time,)
            cur.execute(q1, data)
            con.commit()
          with open("logs/download_pdf.log", "a+") as fp:
            row = f"{l_time}, {ins}, {ct}, {subject}, {filepath}\n"
            fp.write(row)
          if ins == 'star' and ct == 'preauth' or ct == "final":
              run_ins(ins, ct, filepath, subject, l_time, hid, mail_id)
          else:
              subprocess.run(
                ["python", ins + "_" + ct + ".py", filepath, str(row_count_1), ins, ct, subject, l_time, hid,
                 mail_id])
      except Exception as e:
        send_sms(f'exception in {subject}')
        log_exceptions()
  except:
    log_exceptions()

def run_ins(ins, ct, filepath, subject, l_time, hid, mail_id):
    subprocess.Popen(
        ["python", ins + "_" + ct + ".py", filepath, str(1), ins, ct, subject, l_time, hid,
         mail_id])


def download_html_copy(s_r, mail, ins, ct, row_count_1, subject, hid, l_time, files, mail_id, sender):
  now = datetime.datetime.now()
  # wbkName = 'log file.xlsx'
  subprocess.run(["python", "foldercheck.py", (ins + '/attachments_' + ct)])
  dirFiles = os.listdir(ins + '/attachments_' + ct)
  detach_dir = (os.getcwd() + '/' + ins + '/attachments_' + ct + '/')
  dirFiles.sort(key=lambda l: int(re.sub('\D', '', l)))
  # print(dirFiles[-1])
  if (len(dirFiles) > 0):
    m = dirFiles[-1].find('.')
    b = int(dirFiles[-1][:m])
  else:
    b = 0
  b += 1
  # print(b)
  token = _get_token_from_cache(app_config.SCOPE)
  getmail = f"https://graph.microsoft.com/v1.0/me/messages/{mail_id}"
  data = requests.get(getmail, headers={'Authorization': 'Bearer ' + token['access_token'],
                                          "Prefer": "odata.track-changes",
                                          },
                      ).json()

  with open(ins + '/email.html', 'w') as tempf:
    tempf.write(data['body']['content'])
  try:
    pdfkit.from_file(ins + '/email.html', ins + '/attachments_' + ct + '/' + str(b) + '.pdf', configuration=config)
  except Exception as e:
    log_exceptions()
    pass

  # for mail.part in mail.email_message.walk():
  #   if mail.part.get_content_type() == "text/html" or mail.part.get_content_type() == "text/plain":
  #     mail.body = mail.part.get_payload(decode=True)
  #     mail.file_name = ins + '/email.html'
  #     mail.output_file = open(mail.file_name, 'w')
  #     try:
  #       mail.output_file.write("Body: %s" % (mail.body.decode('utf-8')))
  #     except Exception as e:
  #       log_exceptions()
  #       continue
  #
  #     mail.output_file.close()
  #     try:
  #       pdfkit.from_file(ins + '/email.html', ins + '/attachments_' + ct + '/' + str(b) + '.pdf', configuration=config)
  #     except Exception as e:
  #       log_exceptions()
  #       pass
  #subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
  filePath = os.path.join(detach_dir, str(b) + '.pdf')
  # print(mail.email_message['Date'])
  '''
  l_time=mail.email_message['Date']
  l_time = ifutc_to_indian(l_time)
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
    l_time = date_parser.parse(ifutc_to_indian(l_time)).strftime('%d/%m/%Y %H:%M:%S')
    # l_time = ifutc_to_indian(l_time)
    '''
  try:
    if (ct == 'settlement'):
      #varun sir
      return 1
      start_date = datetime.date.today().strftime("%d-%b-%Y")
      end_date = datetime.date.today().strftime("%d-%b-%Y")
      uid = mail.latest_email_id.decode()
      #subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
      now = datetime.datetime.now()
      #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
      #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
      #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
      #subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
      subprocess.run(["python", "main.py", start_date, end_date, ins, hid, uid, subject])
    else:
      fp2 = open(ins + "_" + ct + ".py", "r")
      fp2.close()
      try:
        subprocess.run(
          ["python", ins + "_" + ct + ".py", ins + '/attachments_' + ct + '/' + str(b) + '.pdf', str(row_count_1), ins,
           ct, subject, l_time, hid, mail_id])
      except:
        log_exceptions()
  except Exception as e:
    log_exceptions()
    #subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
    # wbk.save(wbkName)
    s_r += 1
    #subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
    #subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
    #subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
    #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
    #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
    #subprocess.run(["python", "updation.py", "1", "max", "15", 'python file doesnot exist- ' + ins + '_' + ct + '.py'])
    # print(e)
  #subprocess.run(["python", "updation.py", "1", "max", "19", filePath])
  #subprocess.run(["python", "updation.py", "1", "max", "20", mail_id])
  #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
  #subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
  s_r = s_r + 1

  #subprocess.run(["python", "updation.py", "1", "max", "4", str(now)])
  add_time_diff()



def download_html(s_r, mail, ins, ct, row_count_1, subject, hid, l_time):
  now = datetime.datetime.now()
  # wbkName = 'log file.xlsx'
  subprocess.run(["python", "foldercheck.py", (ins + '/attachments_' + ct)])
  dirFiles = os.listdir(ins + '/attachments_' + ct)
  mail.detach_dir = (os.getcwd() + '/' + ins + '/attachments_' + ct + '/')
  dirFiles.sort(key=lambda l: int(re.sub('\D', '', l)))
  # print(dirFiles[-1])
  if (len(dirFiles) > 0):
    m = dirFiles[-1].find('.')
    b = int(dirFiles[-1][:m])
  else:
    b = 0
  b += 1
  # print(b)
  for mail.part in mail.email_message.walk():
    if mail.part.get_content_type() == "text/html" or mail.part.get_content_type() == "text/plain":
      mail.body = mail.part.get_payload(decode=True)
      mail.file_name = ins + '/email.html'
      mail.output_file = open(mail.file_name, 'w')
      try:
        mail.output_file.write("Body: %s" % (mail.body.decode('utf-8')))
      except Exception as e:
        log_exceptions()
        continue

      mail.output_file.close()
      try:
        pdfkit.from_file(ins + '/email.html', ins + '/attachments_' + ct + '/' + str(b) + '.pdf', configuration=config)
      except Exception as e:
        log_exceptions()
        pass
  #subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
  mail.filePath = os.path.join(mail.detach_dir, str(b) + '.pdf')
  # print(mail.email_message['Date'])
  '''
  l_time=mail.email_message['Date']
  l_time = ifutc_to_indian(l_time)
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
    l_time = date_parser.parse(ifutc_to_indian(l_time)).strftime('%d/%m/%Y %H:%M:%S')
    # l_time = ifutc_to_indian(l_time)
    '''
  try:
    if (ct == 'settlement'):
      start_date = datetime.date.today().strftime("%d-%b-%Y")
      end_date = datetime.date.today().strftime("%d-%b-%Y")
      uid = mail.latest_email_id.decode()
      #subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
      now = datetime.datetime.now()
      #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
      #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
      #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
      #subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
      subprocess.run(["python", "main.py", start_date, end_date, ins, hid, uid, subject])
    else:
      fp2 = open(ins + "_" + ct + ".py", "r")
      fp2.close()
      try:
        subprocess.run(
          ["python", ins + "_" + ct + ".py", ins + '/attachments_' + ct + '/' + str(b) + '.pdf', str(row_count_1), ins,
           ct, subject, l_time, hid, str(mail.latest_email_id)[2:-1]])
      except:
        log_exceptions()
  except Exception as e:
    log_exceptions()
    #subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
    # wbk.save(wbkName)
    s_r += 1
    #subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
    #subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
    #subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
    #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
    #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
    #subprocess.run(["python", "updation.py", "1", "max", "15", 'python file doesnot exist- ' + ins + '_' + ct + '.py'])
    # print(e)
  #subprocess.run(["python", "updation.py", "1", "max", "19", mail.filePath])
  #subprocess.run(["python", "updation.py", "1", "max", "20", str(mail.latest_email_id)[2:-1]])
  #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
  #subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
  s_r = s_r + 1

  #subprocess.run(["python", "updation.py", "1", "max", "4", str(now)])
  add_time_diff()


def download_pdf(s_r, mail, ins, ct, row_count_1, subject, hid, l_time):
  print("pdf downloading")
  now = datetime.datetime.now()
  # wbkName = 'log file.xlsx'
  dol = 0
  # try:
  try:
    t_p = 0
    for mail.part in mail.email_message.walk():
      if mail.part.get_content_maintype() == 'multipart':
        # print part.as_string()
        continue
      if mail.part.get('Content-Disposition') is None or mail.part.get_filename() is None:
        # print part.as_string()
        if mail.part.get_filename() is not None:
          pass
        else:
          continue
      mail.fileName = mail.part.get_filename()
      subprocess.run(["python", "foldercheck.py", (os.getcwd() + '/' + ins + '/attachments_pdf_' + ct)])
      mail.detach_dir = (os.getcwd() + '/' + ins + '/attachments_pdf_' + ct + '/')
      if bool(mail.fileName):
        if (mail.fileName.find('MDI') != -1) and (mail.fileName.find('Query') == -1):
          continue
        if (mail.fileName.find('KYC') != -1):
          continue
        if (mail.fileName.find('image') != -1):
          continue
        if (mail.fileName.find('DECLARATION') != -1):
          continue
        if (mail.fileName.find('Declaration') != -1):
          continue
        if (mail.fileName.find('notification') != -1):
          continue
        if (mail.fileName.find('CLAIMGENIEPOSTER') != -1):
          continue
        if (mail.fileName.find('declaration_cashless') != -1):
          continue
        else:
          t_p = 1
          if ins.find("Cholamandalams") != -1:
            w = subject.find(':') + 2
            jk = str(now)
            jk = jk.replace(' ', '_')
            filename = subject[w:]
            # print(filename)
            mail.filePath = os.path.join(mail.detach_dir, filename + '.pdf')
            ter = 1
            # print(mail.filePath)
            while (path.exists(mail.filePath)):
              mail.filePath = os.path.join(mail.detach_dir, filename + '(' + str(ter) + ').pdf')
              # print(mail.filePath)
              ter += 1


          else:
            fil = mail.fileName
            fil = fil.replace("\r", "")
            fil = fil.replace("\n", "")
            fil = fil.replace("/", "")
            if fil.find("\r" or "\\r" or "\n" or "\\n") != -1:
              re.sub(r'\\r\\n', '', fil)
              if ins == 'Max_Bupa':
                fil = fil[:-11]
            fil = fil[:-4]
            mail.fileName = fil + '_' + str(mail.latest_email_id)[2:-1] + '.pdf'
            mail.filePath = os.path.join(mail.detach_dir, mail.fileName)
          if ins == 'Raksha':
            filename = mail.fileName
            subject = subject.replace("\r", "")
            subject = subject.replace("\n", "")
            subprocess.run(["python", "raksha_test.py", str(filename), str(ct), subject])
          else:
            fp = open(mail.filePath, 'wb')
            fp.write(mail.part.get_payload(decode=True))
            fp.close()
    dol = 1

  except Exception as e:
    log_exceptions()

    #subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])

    s_r += 1
    #subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
    #subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
    #subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
    #subprocess.run(["python", "updation.py", "1", "max", "15", 'error while downloading'])

  if (t_p == 0):
    download_html(s_r, mail, ins, ct, row_count_1, subject, hid, l_time)
    trigger_alert()
    return 0
  if (dol == 1):
    #subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])

    '''
    l_time=mail.email_message['Date']
    l_time = ifutc_to_indian(l_time)
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
      l_time = date_parser.parse(ifutc_to_indian(l_time)).strftime('%d/%m/%Y %H:%M:%S')
      # l_time = ifutc_to_indian(l_time)
      '''
    try:
      if (ct == 'settlement'):
        start_date = datetime.date.today().strftime("%d-%b-%Y")
        end_date = datetime.date.today().strftime("%d-%b-%Y")
        uid = mail.latest_email_id.decode()
        #subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
        now = datetime.datetime.now()
        #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
        #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
        #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
        #subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
        if ins == 'star':
          if 'Intimation' in subject:
            subprocess.run(["python", "main.py", " ", " ", "big", hid, uid, subject])

          else:
            subprocess.run(["python", "main.py", ' ', ' ', "small", hid, uid, subject])

        else:
          subprocess.run(["python", "main.py", start_date, end_date, ins, hid, uid, subject])
      else:
        fp1 = open(ins + "_" + ct + ".py", "r")
        fp1.close()
        subprocess.run(
          ["python", ins + "_" + ct + ".py", mail.filePath, str(row_count_1), ins, ct, subject, l_time, hid,
           str(mail.latest_email_id)[2:-1]])
    except Exception as e:
      log_exceptions()
      #subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])

      s_r += 1
      #subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
      #subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
      #subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
      #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
      #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
      subprocess.run(
        ["python", "updation.py", "1", "max", "15", 'python file doesnot exist- ' + ins + '_' + ct + '.py'])
      print(e)
    #subprocess.run(["python", "updation.py", "1", "max", "19", mail.filePath])
    #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
    #subprocess.run(["python", "updation.py", "1", "max", "20", str(mail.latest_email_id)[2:-1]])

    s_r += 1
    #subprocess.run(["python", "updation.py", "1", "max", "4", str(now)])
    add_time_diff()
    trigger_alert()


def trigger_alert():
  with mysql.connector.connect(**conn_data) as mydb:
    cur = mydb.cursor()
    b = "SELECT row_no FROM updation_detail_log ORDER BY row_no DESC LIMIT 1"
    cur.execute(b)
    r = cur.fetchone()
    try:
      if r[0] is not None:
        rowno = r[0]
    except:
      rowno = 0
    get_update_log(rowno)


def add_time_diff():
  from push_api import api_trigger
  with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    b = "SELECT date,downloadtime,row_no  FROM updation_detail_log ORDER BY row_no DESC LIMIT 1"
    cur.execute(b)
    r = cur.fetchone()
    if r is not None:
      if r[0] is not None and r[1] is not None and r[2] is not None:
        time_diff = datetime.datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S.%f").timestamp() - datetime.datetime.strptime(
          r[0], "%d/%m/%Y %H:%M:%S").timestamp()
        rowno = r[2]
        query = f"update updation_detail_log set time_difference={int(time_diff)} where row_no={r[2]}"
        cur.execute(query)
        con.commit()

        if int(time_diff) > 500:
          time_diff = time_diff - 500
          api_trigger(time_diff)


# ------------------------------

@app.route('/viewlog')
def viewlog():
  con = sqlite3.connect("database1.db", timeout=timeout_time)
  cur = con.cursor()
  cur.execute("SELECT * from updation_log")
  log_row = cur.fetchall()

  row_len = len(log_row)
  cur.execute("PRAGMA table_info('updation_log') ")
  log_head = cur.fetchall()
  return render_template("viewlog.html", log_head=log_head, log_row=log_row, row_len=row_len)


@app.route('/viewdetaillog/<id>')
def viewdetaillog(id):
  con = sqlite3.connect("database1.db", timeout=timeout_time)
  cur = con.cursor()
  cur.execute("SELECT * from updation_detail_log WHERE runno=" + id)
  log_row = cur.fetchall()

  row_len = len(log_row)
  cur.execute("PRAGMA table_info('updation_detail_log') ")
  log_head = cur.fetchall()

  return render_template("viewdetaillog.html", log_head=log_head, log_row=log_row, row_len=row_len)
  # return render_template("viewdetaillog.html",log_head=log_head,log_row = log_row,row_len=row_len)


@app.route('/apirun', methods=["POST", "GET"])
def apirun():
  api_value = request.form["api_value"]
  x = api_value.replace("'", '"')

  res = json.loads(x)
  print(res)
  with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    q = 'SELECT file_path FROM updation_detail_log WHERE apiparameter== "' + api_value + '"'
    print(q)
    cur.execute(q)
    r = cur.fetchall()
    file_path = r[0][0]
  subprocess.run(
    ["python", "test_api.py", res["preauthid"], res["amount"], res["policyno"], res["process"], res["status"],
     res["lettertime"], file_path, "NULL", res["comment"]])

  return "hello"


@app.route('/openpdf', methods=["POST", "GET"])
def openPdf():
  if request.method == "GET":
    if request.args['path'] != '':
      filepath = request.args['path']
      print("path=", filepath)

      filepath = filepath.replace("\\", "/")
      subprocess.Popen(filepath, shell=True)

  return "success"



def process_copy_test(subject, l_time, files, from_email):
  mail = ""
  # subject ="Claim Query Letter- MemberID:-N90A0175TODAY	Claim No:-90222021477211"
  row_count_1 = "12333"
  # l_time ="07/12/2020 16:06:58"
  # files ="/home/akshay/Downloads/z2/90222021477211_35231.pdf"
  # from_email ="paymentsupport@rakshatpa.com"
  hid ="test"
  mail_id = "asdsaasdasd"
  subject = subject.replace("\r", "")
  subject = subject.replace("\n", "")
  if check_if_sub_and_ltime_exist(subject, l_time):
    return 1
  with mysql.connector.connect(**conn_data) as con:
    xyz = 10
    cur = con.cursor()
    try:
      b = "SELECT IC_name.IC ,IC_name.IC_name, email_ids.email_ids FROM IC_name JOIN email_ids  ON IC_name.IC=email_ids.IC WHERE email_ids.email_ids = '" + from_email + "'"
      print(b)
      cur.execute(b)
    except Exception as e:
      log_exceptions()
      return 1
    r = cur.fetchall()
    if (len(r) > 0):
      id = str(r[0][0])
      ic_name = r[0][1]
      subprocess.run(["python", "foldercheck.py", (ic_name)])
      ic_emal_id = r[0][2]
      b = "SELECT * FROM email_master WHERE ic_id = " + id
      cur.execute(b)
      r = cur.fetchall()
      flag = "false"
      if (len(r) > 0):
        for row in r:
          subject_result = row[1]
          table_name = row[2]
          if id == "35" and table_name != 'settlement':
            download_pdf_copy(s_r, mail, "alankit", "General", row_count_1, subject, hid, l_time, files, mail_id, from_email)
            flag = "true"
            break
          if id == "17" and table_name != 'settlement':
            download_pdf_copy(s_r, mail, "Park", "General", row_count_1, subject, hid, l_time, files, mail_id, from_email)
            flag = "true"
            break
          if subject.find(subject_result) != -1:  # and ic_name!='star' :
            if subject.find('Denial') != -1 or subject.find('REJECTED') != -1 or subject.find('Rejection') != -1:
              table_name = 'denial'
            if subject.find('Query') != -1:
              table_name = 'query'
            if ic_name == 'fhpl' and subject.find('Patient Name') != -1 and subject.find(
              'Approval') == -1 and subject.find('Pending') == -1 and subject.find('Reject') == -1 and subject.find(
              'Settlement') == -1:
              table_name = 'ack'
              if subject.find('Approv') != -1 or subject.find('Approval') != -1 or subject.find('Approved') != -1:
                table_name = 'preauth'
              if subject.find('Final') != -1:
                table_name = 'final'
              if subject.find('Pending') != -1 or subject.find('Query') != -1:
                table_name = 'query'
              if subject.find('Reject') != -1 or subject.find('Rejected') != -1 or subject.find('Rejection') != -1:
                table_name = 'denial'
              if subject.find('Settlement') != -1:
                table_name = 'settlement'
            download_pdf_copy(s_r, mail, ic_name, table_name, row_count_1, subject, hid, l_time, files, mail_id, from_email)
            flag = "true"
            break
        if (flag == "true"):
          print(subject)
        else:
          print(subject, "=", subject_result)

          # NEED to raise error subject not known
          #subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
          #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
          #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
          now = datetime.datetime.now()
          #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
          #subprocess.run(["python", "updation.py", "2", "max", "17", str(from_email)])
          #subprocess.run(["python", "updation.py", "2", "max", "15", str('subject not known')])
          #subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
          #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
          subprocess.run(["python", "sms_api.py", str('Updation failed for ' + subject)])
          add_time_diff()
      else:
        # need to raise error if no subject
        print(subject)
        #subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
        #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
        #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
        now = datetime.datetime.now()
        #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
        #subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
        #subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
        #subprocess.run(["python", "updation.py", "2", "max", "15", str('No subject found in database ')])
        #subprocess.run(["python", "updation.py", "1", "max", "21", hid])
        subprocess.run(
          ["python", "sms_api.py", 'No subject found in database ' + subject])
        add_time_diff()

    else:
      # need to raise error for invalid email id
      print("invalid email " + from_email)
      #subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
      #subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
      now = datetime.datetime.now()
      #subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
      #subprocess.run(["python", "updation.py", "2", "max", "7", subject])
      #subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
      #subprocess.run(["python", "updation.py", "2", "max", "15", str('No email id found in database ')])
      #subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
      subprocess.run(["python", "sms_api.py", str('No email id found in database  ' + subject)])
      add_time_diff()
      #subprocess.run(["python", "updation.py", "1", "max", "21", hid])

def temp_fun():
  path = "result.csv"
  result = []
  with open(path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for i in csv_reader:
      result.append(i)
    now = datetime.datetime.now()
    process_copy(result, now, '14-Dec-2020', 898)
    # with mysql.connector.connect(**conn_data) as con:
    #   cur = con.cursor()
    #   for i in csv_reader:
    #     q = "SELECT * FROM graphApi where date = %s limit 1;"
    #     cur.execute(q, (i[0],))
    #     result = cur.fetchone()
    #     if result is not None:
    #       process_copy_test(result[1], result[2], result[4], result[6])
    #     else:
    #       pass

####for test purpose
print("Scheduler is called.")
sched = BackgroundScheduler(daemon=False)
sched.add_job(add1, 'interval', seconds=10, max_instances=1)
sched.add_job(check_date, 'interval', seconds=300, max_instances=1)
sched.start()
###

if __name__ == '__main__':
    # app.run()
    pass