import email
import imaplib
import sqlite3
import pytz
from email.header import decode_header
from datetime import datetime as akdatetime
from dateutil import parser as date_parser
from cust_time_functs import ifutc_to_indian
from make_log import log_data, log_exceptions
from percentage import get_percentage

inam = (1, 'inamdar hospital', 'mediclaim@inamdarhospital.org', 'Mediclaim@2019', 'imap.gmail.com', 'inbox', 'X')
max = (2, 'Max PPT', 'Tpappg@maxhealthcare.com', 'Sept@2020', 'outlook.office365.com', 'inbox', 'X')

a = 1
if a == 1:
    server = max[4]
    user = max[2]
    pwd = max[3]
else:
    server = inam[4]
    user = inam[2]
    pwd = inam[3]

mail = imaplib.IMAP4_SSL(server)
mail.login(user, pwd)
mail.select("inbox", readonly=True)

mail_id_list = [b'28392', b'28404', b'28417', b'28450', b'28505', b'28549', b'28550', b'28552', b'28554', b'28557']
mlist = []


def mailid_time_subject(mail_id_list, mail, hid,formnowtime):
    try:
        formnowtime = akdatetime.strptime(formnowtime, "%d/%m/%Y %H:%M:%S")
        formnowtime = formnowtime.strftime( "%m/%d/%Y %H:%M:%S")
        formdate = date_parser.parse(formnowtime)
        timezone = pytz.timezone("Asia/Kolkata")
        formdate = timezone.localize(formdate)
        print(formdate, formnowtime)
        mlist, templist = [], []
        hdate, dbsubject, db_mid = get_latest_time_from_db(hid)
        if hdate == "":
            return mail_id_list
       # hdate = hdate.replace(tzinfo=None)
        tlen = len(mail_id_list)
        cnt = 0
        if hdate > formdate:
            formdate = hdate
        for i in mail_id_list:
            try:
                cnt += 1
                result, data = mail.fetch(i, "(RFC822)")
                if result != 'OK' :
                    raise Exception
                # raw_email = data[0][1].decode('utf-8')
                try:
                    raw_email = data[0][1].decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        raw_email = data[0][1].decode('ISO-8859-1')
                    except UnicodeDecodeError:
                        try:
                            raw_email = data[0][1].decode('ascii')
                        except UnicodeDecodeError:
                            pass
                print(round(cnt / tlen * 100, 3), '% done')
            except:
                try:
                    if data[0] is not None:
                        log_exceptions(i=i,result=result,data01='garbage',error='decode_error')
                    else:
                        log_exceptions(i=i,result=result,data='None',error='decode_error')
                    continue
                except Exception as e:
                    continue
            email_message = email.message_from_string(raw_email)
            subject = email_message['Subject']
            date_original = email_message['Date']
            date = ifutc_to_indian(date_original)
            date = date_parser.parse(date)
            print(subject)
            # put a comparison on web page date..
            
            if date < formdate:
                continue
            if hdate == '':
                hdate = formdate
            #clean subject
            try:
                subject.replace('\r', "")
                subject.replace('\n', "")
            except Exception as e:
                subject = ''
                print(i)
                print(date)

            # if date > hdate and subject != dbsubject: # and int(db_mid) < int(i)
            if cmp(hdate, date):
                if subject.find('UTF') != -1:
                    subject = decode_header(subject)
                    subject = subject[0]
                    subject = subject[0].decode()
                elif subject.find('utf') != -1:
                    subject = decode_header(subject)
                    subject = subject[0]
                    subject = subject[0].decode()
                if subject != dbsubject and get_percentage(subject, dbsubject) < 95: # and int(db_mid) < int(i)
                # mlist.append((i, date, subject))
                #log_data(date=str(date),hdate=str(hdate),mid=i,db_mid=db_mid,hid=hid)
                    templist.append([i, date])
                    mlist.append(i)
        log_data(inputlen=len(mail_id_list),outputlen=len(mlist),hid=hid,dbsubject=dbsubject,hdate=str(hdate),mail_id_list=mail_id_list,mlist=mlist,mlist1=templist)
        return mlist
    except:
        log_exceptions(error='Complete failure of cmp_to_time', i= i)
        #call sms_api
        return mail_id_list

def cmp(hdate, mdate):
    hdate, mdate = hdate.replace(tzinfo=None), mdate.replace(tzinfo=None)
    if mdate.year > hdate.year or mdate.month > hdate.month or mdate.day > hdate.day:
        return True
    else:
        if mdate.year < hdate.year:
            return False
        if mdate.month < hdate.month:
            return False
        if mdate.day < hdate.day:
            return False
        if mdate.hour < hdate.hour:
            return False
        if mdate.hour <= hdate.hour and mdate.minute < hdate.minute:
            if  mdate.minute == hdate.minute:
                log_data(log='second', mail_second=mdate.second, dbdate_second=hdate.second)
                if  mdate.second < hdate.second:
                    return False
            else:
                return False
        return True



def get_latest_time_from_db(hid):
    try:
        with sqlite3.connect("database1.db") as con:
            cur = con.cursor()
            b = f"SELECT date,emailsubject,mail_id  FROM updation_detail_log where hos_id='{hid}' ORDER BY row_no DESC LIMIT 1"
            cur.execute(b)
            r = cur.fetchone()
            if r is not None:
                r = list(r)
                hdate = r[0]
                hdate = akdatetime.strptime(hdate, "%d/%m/%Y %H:%M:%S")
                timezone = pytz.timezone("Asia/Kolkata")
                hdate = timezone.localize(hdate)
                r[1] = ''.join([i if ord(i) < 128 else '' for i in r[1]])#remove non ascii chars
                return (hdate, r[1], r[2])
            return ("", "", "")
    except:
        log_exceptions()
        return ("", "", "")


if __name__ == '__main__':
    # mlist = mailid_time_subject(mail_id_list, mail, 'inamdar hospital')
    # for i in mlist:
    #     print(i)
    a, b, c = get_latest_time_from_db('inamdar hospital')
    print(a, b, c)

