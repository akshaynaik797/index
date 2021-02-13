from datetime import datetime
from alertconfig import mydb
from make_log import log_exceptions, log_data
from sms_and_push import send_push, send_sms


def triggerAlert1(patientid_treatmentid,hospital_id,status):
    a = fetch_sms_and_push_notification_records(patientid_treatmentid, hospital_id, status)
    if a[0][0] == 'Patient':
        #if UserType from iclaimtest.alerts is Patient
        b = fetch_p_contact_no(patientid_treatmentid)
        e = fetch_token_list(b, "patient")
        g = send_sms_and_notifications(e, a)
        return True
    elif a[0][0] != 'Patient':
        # if UserType from iclaimtest.alerts is not Patient
        c = fetch_hosp_contacts(hospital_id)
        d = fetch_token_list(c, "hospital")
        f = send_sms_and_notifications(d, a)
        return True




def triggerAlert(refno,hospital_id):
    try:
        a = fetch_sms_and_push_notification_records(refno, hospital_id)
        for i in a:
            if i[0] == 'Patient': # loop for all the values of a[i][0] 
                #if UserType from iclaimtest.alerts is Patient
                b = fetch_p_contact_no(refno)
                e = fetch_token_list(b, "patient")
                g = send_sms_and_notifications(e, a)
                return True
            elif i[0] != 'Patient':
                # if UserType from iclaimtest.alerts is not Patient
                c = fetch_hosp_contacts(hospital_id)
                d = fetch_token_list(c, "hospital")
                f = send_sms_and_notifications(d, a)
        return True
    except Exception as e:
        return "fail in triggeralert "+str(e)

def fetch_sms_and_push_notification_records(refno, hospital_id):
    try:
        mycursor, result3 = mydb.cursor(), []
	# select currentstatus from preauth where where PatientID_TreatmentID='%s' and HospitalID='%s' -> Preauth - Information_Awaiting ->type and status
        q1 = """select currentstatus from preauth where refno='%s' and HospitalID='%s';""" % (refno, hospital_id)
        mycursor.execute(q1)
        result = mycursor.fetchone()
 

        if result is not None:
            result = [result[0].split('-')[0].strip()] #use strip value to make status
            q2 = """SELECT Type FROM send_sms_config where statuslist LIKE '%s';""" % ("%" + status + "%") 
            mycursor.execute(q2)
            result2 = mycursor.fetchall()
            if result2 is not None:
                for i in result2:
                    # uncomment below line
                    user_type, t_ype = i[0], result[0]
                    # remove below line
                    # status, user_type = "Approved", "Patient"
                    q3 = """SELECT UserType,Link_SMS, SMS, PushNotification FROM alerts where UserType='%s' and Type='%s' and Status='%s'""" % (user_type, t_ype, status)
                    mycursor.execute(q3)
                    temp = mycursor.fetchone()
                    if temp is not None:
                        result3.append(temp)
            else:
                log_data(status=status, info="no such records in send_sms_config")
        else:
            log_data(params=(patientid_treatmentid, hospital_id, status), info="no such records in status_track")
        mycursor.close()
        return result3
    except Exception as e:
        return e


def fetch_p_contact_no(patientid_treatmentid):
    try:
        mycursor = mydb.cursor()
        q1 = """SELECT p_contact FROM preauth where refno='%s';""" % (refno)
        mycursor.execute(q1)
        no_list = mycursor.fetchall()
        if no_list is None:
            mycursor.close()
            return []
        clean = []
        for i in no_list:
            clean.append(i[0])
        mycursor.close()
        return clean
    except:
        return []


def fetch_hosp_contacts(hospital_id):
    try:
        mycursor = mydb.cursor()
        q1 = """SELECT he_mobile FROM hospital_employee where he_hospital_id = '%s';""" % (hospital_id)
        mycursor.execute(q1)
        no_list = mycursor.fetchall()
        if no_list is None:
            return []
        clean = []
        for i in no_list:
            clean.append(i[0])
        mycursor.close()
        return clean
    except:
        return []


def fetch_token_list(mobile_no_list, type):
    try:
        token_list = []
        mycursor = mydb.cursor()
        for i in mobile_no_list:
            q1 = """SELECT tokenNo FROM device_Token where mobileNo='%s'""" % (i)
            mycursor.execute(q1)
            temp = []
            for j in mycursor:
                temp.append(j[0])
            token_list.append((i, type, temp))
        mycursor.close()
        return token_list
    except:
        return []


def send_sms_and_notifications(mob_token_list, result):
    for i in result:
        body = i[2]
        flag = 0
        #mob_token_list = list(set(mob_token_list))
        for j in mob_token_list:
            mob_no, t_ype, token_list = j[0], j[1], j[2]
            if t_ype == "hospital" or t_ype == "admin": # add admin also
                for k in token_list:
                    data_dict = {}
                    response = send_push(k, 'Status update', body)

                    data_dict['mobileno'] = mob_no
                    data_dict['type'] = t_ype
                    data_dict['notification_text'] = body
                    data_dict['sms'] = ""
                    data_dict['push'] = "X"
                    data_dict['timestamp'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    data_dict['messageid'] = response[2]
                    data_dict['error'] = response[1]
                    data_dict['device_token'] = k

                    write_to_alert_log(data_dict)
            else:
                for k in token_list:
                    data_dict = {}
                    response = send_push(k, 'Status update', body)
                    flag = 0
                    if response[0] == False:
                        flag = 1

                    data_dict['mobileno'] = mob_no
                    data_dict['type'] = t_ype
                    data_dict['notification_text'] = body
                    data_dict['sms'] = ""
                    data_dict['push'] = "X"
                    data_dict['timestamp'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    data_dict['messageid'] = response[2]
                    data_dict['error'] = response[1]
                    data_dict['device_token'] = k

                    write_to_alert_log(data_dict)

                    if flag == 1 or flag == 2:
                        flag = 2
                        response = send_sms(mob_no, body) #check whether mob no exists or not, change flag value to 2 and check at last flag MUST equal to 1

                        data_dict['mobileno'] = mob_no
                        data_dict['type'] = t_ype
                        data_dict['notification_text'] = body
                        data_dict['sms'] = "X"
                        data_dict['push'] = "Failed"
                        data_dict['timestamp'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        data_dict['messageid'] = ""
                        data_dict['error'] = response
                        data_dict['device_token'] = ""

                        write_to_alert_log(data_dict)
                if flag == 1:
                    response = send_sms(mob_no, body) #check whether mob no exists or not, change flag value to 2 and check at last flag MUST equal to 1

                    data_dict['mobileno'] = mob_no
                    data_dict['type'] = t_ype
                    data_dict['notification_text'] = body
                    data_dict['sms'] = "X"
                    data_dict['push'] = "Failed"
                    data_dict['timestamp'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    data_dict['messageid'] = ""
                    data_dict['error'] = response
                    data_dict['device_token'] = ""

                    write_to_alert_log(data_dict)



def write_to_alert_log(data_dict):
    try:
        try:
            mobileno, t_ype, notification_text, sms = data_dict['mobileno'], data_dict['type'], data_dict[
                'notification_text'], data_dict['sms']
            push, timestamp, messageid, error = data_dict['push'], data_dict['timestamp'], data_dict['messageid'], data_dict['error']
            device_token = data_dict['device_token']
        except:
            mobileno, t_ype, notification_text = "", "", ""
            sms, push, timestamp, messageid, error, device_token = "", "", "", "", "", ""
        mycursor = mydb.cursor()
        q1 = """insert into alerts_log (mobileno, type, `notification text`, sms, push, timestamp, messageid, error, device_token) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"""% (mobileno, t_ype, notification_text, sms, push, timestamp, messageid, error, device_token)
        mycursor.execute(q1)
        mydb.commit()
    except:
        pass

# if __name__ == "__main__":
#     patientid_treatmentid = '29890/1024193'
#     hospital_id = 'LCBP-2009-00337'
#     status = 'Approved'
#     a = fetch_sms_and_push_notification_records(patientid_treatmentid, hospital_id, status)
#     b = fetch_p_contact_no(patientid_treatmentid)
#     c = fetch_hosp_contacts(hospital_id)
#     d = fetch_token_list(c, "hospital")
#     e = fetch_token_list(b, "patient")
#     f = send_sms_and_notifications(d, a)
#     g = send_sms_and_notifications(e, a)
#     pass
