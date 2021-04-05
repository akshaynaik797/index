import csv
import mimetypes
import smtplib
from datetime import datetime
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import mysql.connector

from custom_parallel import conn_data


def send_email(file, subject):
    emailfrom = "iClaim.vnusoftware@gmail.com"
    emailto = ["sachin@vnusoftware.com", 'ceo@vnusoftware.com', 'maneesh@vnusoftware.com', 'akshaynaik797@gmail.com']
    fileToSend = file
    username = emailfrom
    password = "44308000"

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = ", ".join(emailto)
    msg["Subject"] = subject
    msg.preamble = subject

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username,password)
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()

def fun():
    filename = 'diff.csv'
    data = [['hospital', 'date', 'time_diff1(X)', 'time_diff2(X)', 'time_diff1(A)', 'time_diff2(A)']]
    now = datetime.now().strftime('%d/%m/%Y')
    fields = ('hos_id', 'time_difference', 'time_difference2')
    q = "select distinct(hos_id) from updation_detail_log_copy where date like %s"
    q1 = "select time_difference, time_difference2 from updation_detail_log_copy where date like %s and completed=%s and hos_id=%s"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (now + '%',))
        r = cur.fetchall()
        h_list = [i[0] for i in r]
        for hosp in h_list:
            cur.execute(q1, (now + '%', 'X', hosp))
            r1 = cur.fetchall()
            td1, td2 = 0, 0
            for t1, t2 in r1:
                try:
                    td1 = td1 + float(t1)
                except:
                    pass

                try:
                    td2 = td2 + float(t2)
                except:
                    pass
            try:
                td1, td2 = round(td1/len(r1), 2), round(td2/len(r1), 2)
            except ZeroDivisionError:
                td1, td2 = "", ""

            cur.execute(q1, (now + '%', 'A', hosp))
            r1 = cur.fetchall()
            td3, td4 = 0, 0
            for t1, t2 in r1:
                try:
                    td3 = td3 + float(t1)
                except:
                    pass

                try:
                    td4 = td4 + float(t2)
                except:
                    pass
            try:
                td3, td4 = round(td3 / len(r1), 2), round(td4 / len(r1), 2)
            except ZeroDivisionError:
                td3, td4 = "", ""
            data.append([hosp, now, td1, td2, td3, td4])
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    send_email(filename, f"time diff data for {now}")

if __name__ == '__main__':
    fun()