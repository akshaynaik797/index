# from flask import *
import csv
import uuid
from multiprocessing import Pool
from os.path import splitext, isfile, join
from pathlib import Path
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
from custom_app import check_if_sub_and_ltime_exist, get_fp_seq, create_settlement_folder, \
    change_active_flag_mail_storage_tables
from custom_parallel import conn_data
from sms_alerts import send_sms
from process_p_flag import process_p_flag_mails

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
    return render_template('index.html')  # , user=session["user"], version=msal.__version__


def log_api_data(varname, value):
    from datetime import datetime as akdatetime
    with open('api_data.log', 'a+') as fp:
        nowtime = str(akdatetime.now())
        entry = ('===================================================================================================\n'
                 f'{nowtime}\n'
                 # '---------------------------------------------------------------------------------------------------\n'
                 f'{varname}->{value}\n')
        fp.write(entry)


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
    if request.method != 'POST':
        return jsonify(
            {
                'status': 'failed',
                'message': 'inavlid request method.Only Post method Allowed'
            }
        )
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
            return jsonify({
                'status': 'success',
                'message': apimessage})

    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = f'select preauthid,amount,status,process,lettertime,policyno,memberid,hos_id from updation_detail_log where row_no={row_no}'
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
                if hosid == 'Max PPT':
                    API_ENDPOINT = "https://vnusoftware.com/iclaimmax/api/preauth/"
                else:
                    API_ENDPOINT = "https://vnusoftware.com/iclaimportal/api/preauth"
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
                    if char == 'X':
                        query = f'update updation_detail_log set completed= "X" where row_no={row_no};'
                    elif char == 'x':
                        query = f'update updation_detail_log set completed= "x" where row_no={row_no};'
                    with mysql.connector.connect(**conn_data) as con:
                        cur = con.cursor()
                        cur.execute(query)
                        con.commit()
                    apimessage = 'Record successfully updated, and API successfully called'
                    # update completed flag in table
                    with sqlite3.connect('../mail_fetch/database1.db', timeout=timeout_time) as con:
                        cur = con.cursor()
                        cur.execute(f"update run_table set completed = 'D' where ref_no = '{refno}'")

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


@app.route("/api/getupdateDetailsLog", methods=["POST"])
def getUpdateLog():
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
            query = """SELECT runno,insurerid,process,emailsubject,date,file_path,hos_id,preauthid,amount,status,lettertime,policyno,memberid,row_no,comment from updation_detail_log WHERE completed is NULL and error is NULL and hos_id = 'inamdar hospital' """  # if runno = '0'->all

        elif runno != '0':
            query = """SELECT runno,insurerid,process,emailsubject,date,file_path,hos_id,preauthid,amount,status,lettertime,policyno,memberid,row_no,comment from updation_detail_log WHERE completed is NULL and error is NULL and runno=%s""" % runno  # if runno = '0'->all
        else:
            query = """SELECT runno,insurerid,process,emailsubject,`date`,file_path,hos_id,preauthid,amount,`status`, \
          lettertime,policyno,memberid,row_no,comment from updation_detail_log WHERE error IS NULL and completed is NULL"""

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

                url = request.url_root
                url = url + 'api/downloadfile?filename='
                url = url + str(row[5])
                localDic['file_path'] = url

                if localDic['memberid'] != None or localDic['preauthid'] != None or localDic['policyno'] != None or \
                    localDic[
                        'comment'] != None:
                    if localDic['hos_id'] == 'Max PPT':
                        url = 'https://vnusoftware.com/iclaimmax/api/preauth/vnupatientsearch'
                    else:
                        url = 'https://vnusoftware.com/iclaimportal/api/preauth/vnupatientsearch'
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
                        log_data(payload=payload, url=url, response=response)
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
        filepath = request.args['filename']
        print("path=", filepath)
        # log_api_data('filepath', filepath)
        # filepath1=r"C:\Users\91798\Desktop\trial_shikha-master2\hdfc\attachments_pdf_denial\PreAuthDenialLe_RC-HS19-10809032_1_202_20200129142830250_19897.pdf"
        filepath = filepath.replace("\\", "/")
        mylist = filepath.split('/')
        filename = mylist[-1]
        index = 0
        dirname = ''
        for x in mylist:
            index = index + 1
            if index != len(mylist):
                dirname = dirname + x + '/'

        # return send_from_directory(r"C:\Users\91798\Desktop\download\templates", filename='ASHISHKUMAR_IT.pdf', as_attachment=True)
        return send_from_directory(dirname, filename=filename, as_attachment=True)


# @app.route('/add', methods=["POST", "GET"])
# def add():
#     formparameter = {}
#     formparameter['interval'] = (request.form["intervel"])
#     formparameter['fromtime'] = request.form["fromtime"]
#     formparameter['totime'] = request.form["totime"]
#     formparameter['id'] = request.form["id"]
#     formparameter['hid'] = request.form["hid"]
#     formparameter['count'] = request.form["count"]
#     formparameter['pid'] = request.form["pid"]
#     formparameter['nowtime'] = akdatetime.now()
#     formparameter['formnowtime'] = request.form['formnowtime']
#     # formparameter['datetime'] = request.form['datetime']
#
#     with open('nowtime.txt', 'a') as f:
#         f.write('form ' + str(formparameter['nowtime']) + '\n')
#
#     try:
#         if formparameter['formnowtime'] != '' and formparameter['interval'] != '':
#             formparameter['nowtime'] = akdatetime.strptime(formparameter['formnowtime'], '%d/%m/%Y %H:%M:%S')
#     except Exception as e:
#         log_exceptions()
#         pass
#
#     # formparameter['interval'] = 'interval1'
#     # if formparameter['interval'] == 'interval1':
#     #  deltaMessage()
#
#     if formparameter['interval'] != '':
#         # if now time is given from screen, then it will be considered, else akdatetime.now along with date
#         print("Scheduler is called.")
#         sched = BackgroundScheduler(daemon=False)
#         sched.add_job(inamdar, 'interval', seconds=int(formparameter['interval']), args=[formparameter], max_instances=1)
#         sched.add_job(noble, 'interval', seconds=int(formparameter['interval']), args=[formparameter],
#                       max_instances=1)
#         sched.add_job(ils, 'interval', seconds=int(formparameter['interval']), args=[formparameter],
#                       max_instances=1)
#         sched.add_job(ils_dumdum, 'interval', seconds=int(formparameter['interval']), args=[formparameter],
#                       max_instances=1)
#         sched.add_job(ils_agartala, 'interval', seconds=int(formparameter['interval']), args=[formparameter],
#                       max_instances=1)
#         sched.add_job(ils_howrah, 'interval', seconds=int(formparameter['interval']), args=[formparameter],
#                       max_instances=1)
#         sched.start()
#     else:
#         inamdar(formparameter)
#     return "success"

def main(formparameter, hospital_name, **kwargs):
    print(hospital_name)

    with mysql.connector.connect(**conn_data) as mydb:
        cur = mydb.cursor()
        q1 = f"insert into runs (date) value ('{str(datetime.datetime.now())}');"
        cur.execute(q1)
        mydb.commit()
    # # from datetime import datetime as akdatetime
    intervel = formparameter["interval"]
    nowtime = formparameter['nowtime']
    row_count_1 = 1
    now = datetime.datetime.now()
    today = datetime.date.today()
    today = today.strftime('%d-%b-%Y')
    r_credentials = []
    if r_credentials == []:
        result = []
        q = f"select * from {hospital_name}_mails where completed=''"
        if kwargs:
            if kwargs['mode'] == "test":
                q = f"select * from {hospital_name}_mails where sno='{kwargs['sno']}'"
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            cur.execute(q)
            result = cur.fetchall()
            if result == []:
                return str([])
        if kwargs:
            result = [list(i) for i in result]
            result[0][4] = kwargs['filepath']
            dst = f'../{hospital_name}/new_attach/'
            Path(dst).mkdir(parents=True, exist_ok=True)
            dst = os.path.join(dst, os.path.split(kwargs['filepath'])[1])
            copyfile(kwargs['filepath'], dst)
        process_copy_hospital(result, now, today, row_count_1, hospital_name)
    fo = open("defualt_time_read.txt", "a+")
    if (str(today) != str(tg[-1])):
        fo.write(str(today) + '\n')
    now = datetime.datetime.now()
    today = datetime.date.today()
    today = today.strftime('%d-%b-%Y')
    # subprocess.run(["python", "updation.py", "0", "max", "4", str(today)])
    # subprocess.run(["python", "updation.py", "0", "max", "5", str(now)])
    # return str(msg)
    print(f"----Job is scheduled for every " ,intervel ," seconds")


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
                                if subject.find('Denial') != -1 or subject.find('REJECTED') != -1 or subject.find(
                                    'Rejection') != -1:
                                    table_name = 'denial'
                                if subject.find('Query') != -1:
                                    table_name = 'query'
                                if ic_name == 'fhpl' and subject.find('Patient Name') != -1 and subject.find(
                                    'Approval') == -1 and subject.find('Pending') == -1 and subject.find(
                                    'Reject') == -1 and subject.find(
                                    'Settlement') == -1:
                                    table_name = 'ack'
                                    if subject.find('Approv') != -1 or subject.find('Approval') != -1 or subject.find(
                                        'Approved') != -1:
                                        table_name = 'preauth'
                                    if subject.find('Final') != -1:
                                        table_name = 'final'
                                    if subject.find('Pending') != -1 or subject.find('Query') != -1:
                                        table_name = 'query'
                                    if subject.find('Reject') != -1 or subject.find('Rejected') != -1 or subject.find(
                                        'Rejection') != -1:
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
                            # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                            # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                            # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                            now = datetime.datetime.now()
                            # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                            # subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
                            # subprocess.run(["python", "updation.py", "2", "max", "15", str('subject not known')])
                            # subprocess.run(["python", "updation.py", "2", "max", "20", str(mail.latest_email_id)[2:-1]])
                            # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
                            subprocess.run(
                                ["python", "sms_api.py", str('Updation failed for ' + mail.email_message['Subject'])])
                            add_time_diff()
                    else:
                        # need to raise error if no subject
                        print(subject)
                        # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                        # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                        # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                        now = datetime.datetime.now()
                        # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                        # subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
                        # subprocess.run(["python", "updation.py", "2", "max", "20", str(mail.latest_email_id)[2:-1]])
                        # subprocess.run(["python", "updation.py", "2", "max", "15", str('No subject found in database ')])
                        # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
                        subprocess.run(
                            ["python", "sms_api.py",
                             str('No subject found in database ' + mail.email_message['Subject'])])
                        add_time_diff()

                else:
                    # need to raise error for invalid email id
                    print("invalid email " + from_email)
                    # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                    # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                    now = datetime.datetime.now()
                    # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                    # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                    # subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
                    # subprocess.run(["python", "updation.py", "2", "max", "15", str('No email id found in database ')])
                    # subprocess.run(["python", "updation.py", "2", "max", "20", str(mail.latest_email_id)[2:-1]])
                    subprocess.run(["python", "sms_api.py", str('No email id found in database  ' + subject)])
                    add_time_diff()
                    # subprocess.run(["python", "updation.py", "1", "max", "21", hid])

    fo = open("defualt_time_read.txt", "a+")
    if (str(today) != str(tg[-1])):
        fo.write(str(today) + '\n')
        now = datetime.datetime.now()
        today = datetime.date.today()
        today = today.strftime('%d-%b-%Y')

        # subprocess.run(["python", "updation.py", "0", "max", "4", str(today)])
        # subprocess.run(["python", "updation.py", "0", "max", "5", str(now)])
        print('done1')


def process_copy_parallel(result, now, today, row_count_1):
    sched = BackgroundScheduler(daemon=False,
                                executors={'processpool': ProcessPoolExecutor(max_workers=3)})
    for i in result:
        sched.add_job(process_copy, args=[[i], now, today, row_count_1], misfire_grace_time=10000)
    sched.start()


def process_copy(result, now, today, row_count_1):
    try:
        # today = datetime.date.today()
        # today = today.strftime('%d-%b-%Y')
        mail = ""
        #
        print('in process copy ', len(result), today, row_count_1)
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
                                    download_pdf_copy(s_r, mail, "alankit", "General", row_count_1, subject, hid,
                                                      l_time, files, mail_id, from_email)
                                    flag = "true"
                                    break
                                if id == "17" and table_name != 'settlement':
                                    download_pdf_copy(s_r, mail, "Park", "General", row_count_1, subject, hid, l_time,
                                                      files, mail_id, from_email)
                                    flag = "true"
                                    break
                                if subject.find(subject_result) != -1:  # and ic_name!='star' :
                                    if subject.find('Denial') != -1 or subject.find('REJECTED') != -1 or subject.find(
                                        'Rejection') != -1:
                                        table_name = 'denial'
                                    if subject.find('Query') != -1:
                                        table_name = 'query'
                                    if ic_name == 'fhpl' and subject.find('Patient Name') != -1 and subject.find(
                                        'Approval') == -1 and subject.find('Pending') == -1 and subject.find(
                                        'Reject') == -1 and subject.find(
                                        'Settlement') == -1:
                                        table_name = 'ack'
                                        if subject.find('Approv') != -1 or subject.find(
                                            'Approval') != -1 or subject.find('Approved') != -1:
                                            table_name = 'preauth'
                                        if subject.find('Final') != -1:
                                            table_name = 'final'
                                        if subject.find('Pending') != -1 or subject.find('Query') != -1:
                                            table_name = 'query'
                                        if subject.find('Reject') != -1 or subject.find(
                                            'Rejected') != -1 or subject.find('Rejection') != -1:
                                            table_name = 'denial'
                                        if subject.find('Settlement') != -1:
                                            table_name = 'settlement'
                                    download_pdf_copy(s_r, mail, ic_name, table_name, row_count_1, subject, hid, l_time,
                                                      files, mail_id, from_email)
                                    flag = "true"
                                    break
                            if (flag == "true"):
                                print(subject)
                            else:
                                print(subject, "=", subject_result)

                                # NEED to raise error subject not known
                                # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                                # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                                # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                                now = datetime.datetime.now()
                                # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                                # subprocess.run(["python", "updation.py", "2", "max", "17", str(from_email)])
                                # subprocess.run(["python", "updation.py", "2", "max", "15", str('subject not known')])
                                # subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
                                # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
                                subprocess.run(["python", "sms_api.py", str('Updation failed for ' + subject)])
                                add_time_diff()
                        else:
                            # need to raise error if no subject
                            print(subject)
                            # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                            # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                            # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                            now = datetime.datetime.now()
                            # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                            # subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
                            # subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
                            # subprocess.run(["python", "updation.py", "2", "max", "15", str('No subject found in database ')])
                            # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
                            subprocess.run(
                                ["python", "sms_api.py", 'No subject found in database ' + subject])
                            add_time_diff()

                    else:
                        # need to raise error for invalid email id
                        print("invalid email " + from_email)
                        # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                        # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                        now = datetime.datetime.now()
                        # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                        # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                        # subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
                        # subprocess.run(["python", "updation.py", "2", "max", "15", str('No email id found in database ')])
                        # subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
                        subprocess.run(["python", "sms_api.py", str('No email id found in database  ' + subject)])
                        add_time_diff()
                        # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
            except:
                log_exceptions()
        custom_log_data(filename="process_copy_stats", result_cnt=result_cnt, processed_cnt=processed_cnt)

        fo = open("defualt_time_read.txt", "a+")
        if (str(today) != str(tg[-1])):
            fo.write(str(today) + '\n')
            now = datetime.datetime.now()
            today = datetime.date.today()
            today = today.strftime('%d-%b-%Y')

            # subprocess.run(["python", "updation.py", "0", "max", "4", str(today)])
            # subprocess.run(["python", "updation.py", "0", "max", "5", str(now)])
            print('done1')
    except:
        log_exceptions()


def process_copy_hospital(result, now, today, row_count_1, hid):
    try:
        # today = datetime.date.today()
        # today = today.strftime('%d-%b-%Y')
        mail = ""
        #
        change_active_flag_mail_storage_tables(hospital=hid, flag=0)
        print(hid, 'in process copy ', len(result), today, row_count_1)
        result_cnt, processed_cnt = len(result), 0
        for j, i in enumerate(result):
            subject, l_time, files, from_email, hid, mail_id, mail_table_sno = i[1], i[2], i[4], i[6], hid, i[0], i[7]
            with mysql.connector.connect(**conn_data) as con:
                cur = con.cursor()
                q1 = f"insert into {hid}_jobs values (%s, %s, %s);"
                data = (j, i[1], i[2])
                cur.execute(q1, data)
                con.commit()
            with mysql.connector.connect(**conn_data) as con:
                cur = con.cursor()
                q1 = f"update {hid}_mails set completed = 'p' where sno=%s;"
                data = (mail_table_sno,)
                cur.execute(q1, data)
                con.commit()
            subject = subject.replace("\r", "")
            subject = subject.replace("\n", "")
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
                                if id == "25" and table_name != 'settlement':
                                    download_pdf_copy(s_r, mail, "icici_prudential", "General", row_count_1, subject, hid,
                                                      l_time, files, mail_id, from_email, mail_table_sno)
                                    flag = "true"
                                    break
                                if id == "35" and table_name != 'settlement':
                                    download_pdf_copy(s_r, mail, "alankit", "General", row_count_1, subject, hid,
                                                      l_time, files, mail_id, from_email, mail_table_sno)
                                    flag = "true"
                                    break
                                if id == "17" and table_name != 'settlement':
                                    download_pdf_copy(s_r, mail, "Park", "General", row_count_1, subject, hid, l_time,
                                                      files, mail_id, from_email, mail_table_sno)
                                    flag = "true"
                                    break
                                if id == "36" and table_name != 'settlement':
                                    download_pdf_copy(s_r, mail, "tata", "General", row_count_1, subject, hid, l_time,
                                                      files, mail_id, from_email, mail_table_sno)
                                    flag = "true"
                                    break
                                if subject.find(subject_result) != -1:  # and ic_name!='star' :
                                    if subject.find('Denial') != -1 or subject.find('REJECTED') != -1 or subject.find(
                                        'Rejection') != -1:
                                        table_name = 'denial'
                                    if subject.find('Query') != -1:
                                        table_name = 'query'
                                    if ic_name == 'fhpl' and subject.find('Patient Name') != -1 and subject.find(
                                        'Approval') == -1 and subject.find('Pending') == -1 and subject.find(
                                        'Reject') == -1 and subject.find(
                                        'Settlement') == -1:
                                        table_name = 'ack'
                                        if subject.find('Approv') != -1 or subject.find(
                                            'Approval') != -1 or subject.find('Approved') != -1:
                                            table_name = 'preauth'
                                        if subject.find('Final') != -1:
                                            table_name = 'final'
                                        if subject.find('Pending') != -1 or subject.find('Query') != -1:
                                            table_name = 'query'
                                        if subject.find('Reject') != -1 or subject.find(
                                            'Rejected') != -1 or subject.find('Rejection') != -1:
                                            table_name = 'denial'
                                        if subject.find('Settlement') != -1:
                                            table_name = 'settlement'
                                    download_pdf_copy(s_r, mail, ic_name, table_name, row_count_1, subject, hid, l_time,
                                                      files, mail_id, from_email, mail_table_sno)
                                    flag = "true"
                                    break
                            if (flag == "true"):
                                print(subject)
                            else:
                                print(subject, "=", subject_result)
                                # with mysql.connector.connect(**conn_data) as con:
                                #     cur = con.cursor()
                                #     q1 = f"update {hid}_mails set completed = 'SNM' where sno = %s;"
                                #     data = (i[7],)
                                #     cur.execute(q1, data)
                                #     con.commit()

                                # NEED to raise error subject not known
                                # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                                # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                                # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                                now = datetime.datetime.now()
                                # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                                # subprocess.run(["python", "updation.py", "2", "max", "17", str(from_email)])
                                # subprocess.run(["python", "updation.py", "2", "max", "15", str('subject not known')])
                                # subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
                                # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
                                subprocess.run(["python", "sms_api.py", str('Updation failed for ' + subject)])
                                add_time_diff()
                        else:
                            # need to raise error if no subject
                            print(subject)
                            # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                            # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                            # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                            now = datetime.datetime.now()
                            # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                            # subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
                            # subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
                            # subprocess.run(["python", "updation.py", "2", "max", "15", str('No subject found in database ')])
                            # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
                            subprocess.run(
                                ["python", "sms_api.py", 'No subject found in database ' + subject])
                            add_time_diff()

                    else:
                        # need to raise error for invalid email id
                        print("invalid email " + from_email)
                        # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                        # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                        now = datetime.datetime.now()
                        # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                        # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                        # subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
                        # subprocess.run(["python", "updation.py", "2", "max", "15", str('No email id found in database ')])
                        # subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
                        # subprocess.run(["python", "sms_api.py", str('No email id found in database  ' + subject)])
                        add_time_diff()
                        # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
            except:
                log_exceptions()
        change_active_flag_mail_storage_tables(hospital=hid, flag=1)
        custom_log_data(filename=f"{hid}_process_copy_stats", result_cnt=result_cnt, processed_cnt=processed_cnt)

        fo = open("defualt_time_read.txt", "a+")
        if (str(today) != str(tg[-1])):
            fo.write(str(today) + '\n')
            now = datetime.datetime.now()
            today = datetime.date.today()
            today = today.strftime('%d-%b-%Y')

            # subprocess.run(["python", "updation.py", "0", "max", "4", str(today)])
            # subprocess.run(["python", "updation.py", "0", "max", "5", str(now)])
            print('done1')
    except:
        log_exceptions()


def download_pdf_copy(s_r, mail, ins, ct, row_count_1, subject, hid, l_time, files, mail_id, sender, mail_table_sno):
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

                    if isfile(f'../{hid}/new_attach/' + fp):
                        copyfile(f'../{hid}/new_attach/' + fp,
                                 os.getcwd() + '/' + ins + '/attachments_pdf_' + ct + '/' + fp)
                    else:
                        fp = fp.replace('.pdf', '.PDF')
                        if isfile(f'../{hid}/new_attach/' + fp):
                            fp1 = fp.replace('.PDF', '.pdf')
                            copyfile(f'../{hid}/new_attach/' + fp,
                                     os.getcwd() + '/' + ins + '/attachments_pdf_' + ct + '/' + fp1)
                    break

        dol = 1

    except Exception as e:
        log_exceptions()

        # subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])

        s_r += 1
        # subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
        # subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
        # subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
        # subprocess.run(["python", "updation.py", "1", "max", "15", 'error while downloading'])

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
                copyfile(body_pdf, os.getcwd() + '/' + ins + '/attachments_' + ct + '/' + str(temp_seq) +
                         splitext(os.path.split(fp)[1])[1])
                # rename file as per folder  sequence
                detach_dir = (os.getcwd() + '/' + ins + '/attachments_' + ct + '/')
                fp = str(temp_seq) + splitext(os.path.split(fp)[1])[1]
                filepath = os.path.join(detach_dir, fp)
                dol = 1
                # return 0
    except:
        log_exceptions()
    try:
        if (dol == 1):
            # subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
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
                            q = f"insert into settlement_mails (`id`,`subject`,`date`,`sys_time`,`attach_path`,`completed`,`sender`,`hospital`, `folder`, `process`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            data = (mail_id, subject, l_time, str(datetime.datetime.now()), filepath, '', sender, hid, 'INBOX', 'index')
                            cur.execute(q, data)
                            q1 = f"update {hid}_mails set completed = 'S' where sno=%s;"
                            data1 = (mail_table_sno,)
                            cur.execute(q1, data1)
                            con.commit()
                    except:
                      log_exceptions()
                    # varun sir
                    # return 1
                    # start_date = datetime.date.today().strftime("%d-%b-%Y")
                    # end_date = datetime.date.today().strftime("%d-%b-%Y")
                    # uid = mail.latest_email_id.decode()
                    # subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
                    # now = datetime.datetime.now()
                    # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                    # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                    # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                    # subprocess.run(["python", "updation.py", "2", "max", "17", sender])
                    # if ins == 'star':
                    #     if 'Intimation' in subject:
                    #         subprocess.run(["python", "main.py", " ", " ", "big", hid, uid, subject])
                    #
                    #     else:
                    #         subprocess.run(["python", "main.py", ' ', ' ', "small", hid, uid, subject])
                    #
                    # else:
                    #     subprocess.run(["python", "main.py", start_date, end_date, ins, hid, uid, subject])
                else:
                    with mysql.connector.connect(**conn_data) as con:
                        cur = con.cursor()
                        q1 = f"update {hid}_mails set completed = 'D' where sno=%s;"
                        data = (mail_table_sno,)
                        cur.execute(q1, data)
                        con.commit()
                    with open(f"logs/{hid}_download_pdf.log", "a+") as fp:
                        row = f"{l_time}, {ins}, {ct}, {subject}, {filepath}\n"
                        fp.write(row)
                    subprocess.run(
                        ["python", ins + "_" + ct + ".py", filepath, str(row_count_1), ins, ct, subject, l_time, hid,
                         mail_id, str(mail_table_sno)])
                    # trigger_alert()
            except Exception as e:
                send_sms(f'exception in {subject}, {hid}')
                log_exceptions()
            temp_flag = 0
            with mysql.connector.connect(**conn_data) as con:
                cur = con.cursor()
                q = f"select completed from {hid}_mails where date=%s and subject=%s limit 1"
                data = (l_time, subject)
                cur.execute(q, data)
                r = cur.fetchone()
                if r:
                    flag = r[0]
                    if flag in ['E', 'D']:
                        temp_flag = 1
            if temp_flag == 1:
                send_sms(f'error in {subject}, {hid}')
    except:
        log_exceptions()


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
    # subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
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
            # varun sir
            return 1
            start_date = datetime.date.today().strftime("%d-%b-%Y")
            end_date = datetime.date.today().strftime("%d-%b-%Y")
            uid = mail.latest_email_id.decode()
            # subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
            now = datetime.datetime.now()
            # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
            # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
            # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
            # subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
            subprocess.run(["python", "main.py", start_date, end_date, ins, hid, uid, subject])
        else:
            fp2 = open(ins + "_" + ct + ".py", "r")
            fp2.close()
            try:
                subprocess.run(
                    ["python", ins + "_" + ct + ".py", ins + '/attachments_' + ct + '/' + str(b) + '.pdf',
                     str(row_count_1), ins,
                     ct, subject, l_time, hid, mail_id])
            except:
                log_exceptions()
    except Exception as e:
        log_exceptions()
        # subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
        # wbk.save(wbkName)
        s_r += 1
        # subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
        # subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
        # subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
        # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
        # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
        # subprocess.run(["python", "updation.py", "1", "max", "15", 'python file doesnot exist- ' + ins + '_' + ct + '.py'])
        # print(e)
    # subprocess.run(["python", "updation.py", "1", "max", "19", filePath])
    # subprocess.run(["python", "updation.py", "1", "max", "20", mail_id])
    # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
    # subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
    s_r = s_r + 1

    # subprocess.run(["python", "updation.py", "1", "max", "4", str(now)])
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
                pdfkit.from_file(ins + '/email.html', ins + '/attachments_' + ct + '/' + str(b) + '.pdf',
                                 configuration=config)
            except Exception as e:
                log_exceptions()
                pass
    # subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
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
            # subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
            now = datetime.datetime.now()
            # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
            # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
            # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
            # subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
            subprocess.run(["python", "main.py", start_date, end_date, ins, hid, uid, subject])
        else:
            fp2 = open(ins + "_" + ct + ".py", "r")
            fp2.close()
            try:
                subprocess.run(
                    ["python", ins + "_" + ct + ".py", ins + '/attachments_' + ct + '/' + str(b) + '.pdf',
                     str(row_count_1), ins,
                     ct, subject, l_time, hid, str(mail.latest_email_id)[2:-1]])
            except:
                log_exceptions()
    except Exception as e:
        log_exceptions()
        # subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])
        # wbk.save(wbkName)
        s_r += 1
        # subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
        # subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
        # subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
        # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
        # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
        # subprocess.run(["python", "updation.py", "1", "max", "15", 'python file doesnot exist- ' + ins + '_' + ct + '.py'])
        # print(e)
    # subprocess.run(["python", "updation.py", "1", "max", "19", mail.filePath])
    # subprocess.run(["python", "updation.py", "1", "max", "20", str(mail.latest_email_id)[2:-1]])
    # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
    # subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
    s_r = s_r + 1

    # subprocess.run(["python", "updation.py", "1", "max", "4", str(now)])
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

        # subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])

        s_r += 1
        # subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
        # subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
        # subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
        # subprocess.run(["python", "updation.py", "1", "max", "15", 'error while downloading'])

    if (t_p == 0):
        download_html(s_r, mail, ins, ct, row_count_1, subject, hid, l_time)
        trigger_alert()
        return 0
    if (dol == 1):
        # subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])

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
                # subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
                now = datetime.datetime.now()
                # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                # subprocess.run(["python", "updation.py", "2", "max", "17", str(mail.email_message['From'])])
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
            # subprocess.run(["python", "updation.py", "0", "max", "11", str(row_count_1)])

            s_r += 1
            # subprocess.run(["python", "updation.py", "1", "max1", "1", str(row_count_1)])
            # subprocess.run(["python", "updation.py", "1", "max", "2", str(ins)])
            # subprocess.run(["python", "updation.py", "1", "max", "3", str(ct)])
            # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
            # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
            subprocess.run(
                ["python", "updation.py", "1", "max", "15", 'python file doesnot exist- ' + ins + '_' + ct + '.py'])
            print(e)
        # subprocess.run(["python", "updation.py", "1", "max", "19", mail.filePath])
        # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
        # subprocess.run(["python", "updation.py", "1", "max", "20", str(mail.latest_email_id)[2:-1]])

        s_r += 1
        # subprocess.run(["python", "updation.py", "1", "max", "4", str(now)])
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
                time_diff = datetime.datetime.strptime(r[1],
                                                       "%Y-%m-%d %H:%M:%S.%f").timestamp() - datetime.datetime.strptime(
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
    hid = "test"
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
                        download_pdf_copy(s_r, mail, "alankit", "General", row_count_1, subject, hid, l_time, files,
                                          mail_id, from_email)
                        flag = "true"
                        break
                    if id == "17" and table_name != 'settlement':
                        download_pdf_copy(s_r, mail, "Park", "General", row_count_1, subject, hid, l_time, files,
                                          mail_id, from_email)
                        flag = "true"
                        break
                    if subject.find(subject_result) != -1:  # and ic_name!='star' :
                        if subject.find('Denial') != -1 or subject.find('REJECTED') != -1 or subject.find(
                            'Rejection') != -1:
                            table_name = 'denial'
                        if subject.find('Query') != -1:
                            table_name = 'query'
                        if ic_name == 'fhpl' and subject.find('Patient Name') != -1 and subject.find(
                            'Approval') == -1 and subject.find('Pending') == -1 and subject.find(
                            'Reject') == -1 and subject.find(
                            'Settlement') == -1:
                            table_name = 'ack'
                            if subject.find('Approv') != -1 or subject.find('Approval') != -1 or subject.find(
                                'Approved') != -1:
                                table_name = 'preauth'
                            if subject.find('Final') != -1:
                                table_name = 'final'
                            if subject.find('Pending') != -1 or subject.find('Query') != -1:
                                table_name = 'query'
                            if subject.find('Reject') != -1 or subject.find('Rejected') != -1 or subject.find(
                                'Rejection') != -1:
                                table_name = 'denial'
                            if subject.find('Settlement') != -1:
                                table_name = 'settlement'
                        download_pdf_copy(s_r, mail, ic_name, table_name, row_count_1, subject, hid, l_time, files,
                                          mail_id, from_email)
                        flag = "true"
                        break
                if (flag == "true"):
                    print(subject)
                else:
                    print(subject, "=", subject_result)

                    # NEED to raise error subject not known
                    # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                    # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                    # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                    now = datetime.datetime.now()
                    # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                    # subprocess.run(["python", "updation.py", "2", "max", "17", str(from_email)])
                    # subprocess.run(["python", "updation.py", "2", "max", "15", str('subject not known')])
                    # subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
                    # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
                    subprocess.run(["python", "sms_api.py", str('Updation failed for ' + subject)])
                    add_time_diff()
            else:
                # need to raise error if no subject
                print(subject)
                # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
                # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
                # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
                now = datetime.datetime.now()
                # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
                # subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
                # subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
                # subprocess.run(["python", "updation.py", "2", "max", "15", str('No subject found in database ')])
                # subprocess.run(["python", "updation.py", "1", "max", "21", hid])
                subprocess.run(
                    ["python", "sms_api.py", 'No subject found in database ' + subject])
                add_time_diff()

        else:
            # need to raise error for invalid email id
            print("invalid email " + from_email)
            # subprocess.run(["python", "updation.py", "2", "max1", "1", str(row_count_1)])
            # subprocess.run(["python", "updation.py", "2", "max", "8", l_time])
            now = datetime.datetime.now()
            # subprocess.run(["python", "updation.py", "2", "max", "4", str(now)])
            # subprocess.run(["python", "updation.py", "2", "max", "7", subject])
            # subprocess.run(["python", "updation.py", "2", "max", "17", from_email])
            # subprocess.run(["python", "updation.py", "2", "max", "15", str('No email id found in database ')])
            # subprocess.run(["python", "updation.py", "2", "max", "20", i[0]])
            subprocess.run(["python", "sms_api.py", str('No email id found in database  ' + subject)])
            add_time_diff()
            # subprocess.run(["python", "updation.py", "1", "max", "21", hid])


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

print("Scheduler is called.")
interval = 10
formparameter = dict()
formparameter['interval'] = interval
formparameter['nowtime'] = ''
sched = BackgroundScheduler(daemon=False)
sched.add_job(process_p_flag_mails, 'interval', seconds=300, max_instances=1)
sched.add_job(main, 'interval', seconds=int(formparameter['interval']), args=[formparameter, 'noble'],
              max_instances=1, id='noble')
sched.add_job(main, 'interval', seconds=int(formparameter['interval']), args=[formparameter, 'inamdar'],
              max_instances=1, id='inamdar')

if __name__ == '__main__':
    ####for test purpose
    # main(formparameter, 'noble', mode="test", sno="43426", filepath="/home/akshay/temp/8382_556222122140071.pdf")
    sched.start()
