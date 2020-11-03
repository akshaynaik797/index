import email
from datetime import date
from cmp_to_time import get_latest_time_from_db
from dateutil import parser as date_parser
from datetime import datetime as akdatetime
from cust_time_functs import ifutc_to_indian
from make_log import log_exceptions, log_data

# if (mode == "intervel"):
#     mail.id_list, call_to_cmp_time = cmp_to_subject_function(hid, mail, mail.id_list)
#     if call_to_cmp_time is not None:
#         mail.id_list = mailid_time_subject(mail.id_list, mail, hid, formparameter['formnowtime'])
# print(mail.id_list)


def cmp_to_subject_function(hid, mail, mailid_list, formnowtime):
    try:
        hdate, dbsubject, db_mid = get_latest_time_from_db(hid)
        if hdate != "":
            hdate = hdate.replace(tzinfo=None)
        formnowtime = akdatetime.strptime(formnowtime, "%d/%m/%Y %H:%M:%S")
        if hdate < formnowtime:
            return (mailid_list, 'call cmp_to_time')
        dbsubject = dbsubject.replace('\n', '').replace('\r', '').replace('\r\n', '')
        if dbsubject != '' and hdate != '':
            thdate = hdate.strftime('%d-%b-%Y')
            temp_idlist = []
            mail.select("inbox",readonly=True)
            try:
                type, data = mail.search(None, f'(since "{thdate}" SUBJECT "{dbsubject}")')
            except:
                log_exceptions(hdate=hdate, thdate=thdate,dbsubject=dbsubject, error='dbsubject search fail')
                return (mailid_list, 'call cmp_to_time')
            if type == 'OK':
                if data != [b'']:
                    mid = data[0].split()
                    sub_mail_id = mid[-1]
                    temp_list = []
                    #if multiple ids for dbsubject then compare time with hdate and match if match forward
                    tlen = len(mailid_list)
                    cnt = 0
                    for j in mid:
                        try:
                            cnt += 1
                            result, data = mail.fetch(j, "(RFC822)")
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
                            email_message = email.message_from_string(raw_email)
                            subject = email_message['Subject']
                            date_original = email_message['Date']
                            mdate = ifutc_to_indian(date_original)
                            mdate = date_parser.parse(mdate)
                            mdate = mdate.replace(tzinfo=None)
                            temp_list.append((j, mdate))
                            z1, z2 = temp_list[-1][1].replace(second=0), hdate.replace(second=0)
                            print(round(cnt/tlen*100, 3),'% done')
                        except:
                            log_exceptions(mid=j,error='decode_error')
                            continue
                    if len(temp_list)==0:
                        return (mailid_list, 'call cmp_to_time')
                    a = temp_list[-1][1]
                    if z1 == z2:
                        if sub_mail_id == mid[-1] and len(mid)>1:
                            #if hdate do not match with any of the dbsubject mails ids
                            log_data(sub_mail_ids=mid,hdate=hdate, thdate=thdate, dbsubject =dbsubject, msg='multiple same subject, but picked last one with same time')
                        for i in mailid_list:
                            if int(i) > int(sub_mail_id):
                                temp_idlist.append(i)
                        mailid_list = temp_idlist
                        return (mailid_list, None)
                    elif z1 > z2:
                        for j in reversed(temp_list):
                            if j[1] == hdate:
                                log_data(sub_mail_ids=mid, hdate=hdate, thdate=thdate, dbsubject=dbsubject,
                                         msg=f'multiple same subject, but picked {j}')
                                for i in mailid_list:
                                    if int(i) > int(j[0]):
                                        temp_idlist.append(i)
                                mailid_list = temp_idlist
                                return (mailid_list, None)
                        if temp_idlist == []:
                            log_data(sub_mail_ids=mid, hdate=hdate, thdate=thdate, dbsubject=dbsubject,
                                     msg=f'multiple same subject, but not found in the list')
                            return (mailid_list, 'call cmp_to_time')
                    else:
                        return (mailid_list, 'call cmp_to_time')
                else:
                    log_data(hdate=hdate, dbsubject=dbsubject, error='type = ok but no id')
                    return (mailid_list, 'call cmp_to_time')
            else:
                log_data(hdate=hdate, dbsubject=dbsubject, error='type != ok')
                return (mailid_list, 'call cmp_to_time')
        return (mailid_list, 'call cmp_to_time')
    except:
        log_exceptions(hid=hid, hdate=hdate, dbsubject=dbsubject)
        return (mailid_list, 'call cmp_to_time')
