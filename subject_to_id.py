import email
import imaplib
from dateutil import parser as date_parser
from datetime import datetime as akdatetime
from cust_time_functs import ifutc_to_indian
from make_log import log_exceptions, log_data

import pdfkit


ins = 'vipul'
inam = (1, 'inamdar hospital', 'mediclaim@inamdarhospital.org', 'Mediclaim@2019', 'imap.gmail.com', 'inbox', 'X')
max = (2, 'Max PPT', 'Tpappg@maxhealthcare.com', 'May@2020', 'outlook.office365.com', 'inbox', 'X')

server = 'outlook.office365.com'
user = 'Tpappg@maxhealthcare.com'
pwd = 'Sept@2020'
ic_email = 'saurabhdutta22@gmail.com'
fromtime = '15-Oct-2020'
totime = '16-Oct-2020'
ic_subject = 'Vijay Kumar Datta'
mail = imaplib.IMAP4_SSL(server)
mail.login(user,pwd)
mail.select("inbox", readonly=True)


type, data1 = mail.search(None,
                              '(FROM ' + ic_email + ' since ' + fromtime + ' before ' + totime + ' (SUBJECT "%s"))' % ic_subject)
result, data = mail.fetch(b'53415', "(RFC822)")
raw_email = data[0][1].decode('utf-8')
email_message = email.message_from_string(raw_email)
subject = email_message['Subject']
date_original = email_message['Date']
mdate = ifutc_to_indian(date_original)
mdate = date_parser.parse(mdate)
mdate = mdate.replace(tzinfo=None)

'''
for mail.part in email_message.walk():
    if mail.part.get_content_type() == "text/html" or mail.part.get_content_type() == "text/plain":
        mail.body = mail.part.get_payload(decode=True)
        mail.file_name = ins + '/email.html'
        mail.output_file = open(mail.file_name, 'w')
        mail.output_file.write("Body: %s" % (mail.body.decode('utf-8')))
        mail.output_file.close()
        pdfkit.from_file(ins + '/email.html', ins+'/'+ ins + '.pdf')
'''
print(type, mail.data, result, data)

