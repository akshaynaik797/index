import imaplib
import base64
import os
import email
import sys

email_user = 'iclaim.vnusoftware@gmail.com'
email_pass = '44308000'
mail = imaplib.IMAP4_SSL("imap.gmail.com",993)
mail.login(email_user,email_pass)
mail.select('Inbox', readonly=True)
subject = sys.argv[3]
w = subject.find('(')
subject = subject[w:-1]
type, data = mail.search(None, 'ALL (SUBJECT "%s")' % subject)
mail_ids = data[0]
id_list = mail_ids.split()
if len(id_list)>0:
    num=id_list[-1]
    typ, data = mail.fetch(num, '(RFC822)' )
    raw_email = data[0][1]
    # converts byte literal to string removing b''
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)
        #print(email_message)
    # downloading attachments
    for part in email_message.walk():
            # this part comes from the snipped I don't understand yet... 
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()
        print(fileName)
        if bool(fileName):
            if(fileName.find('DECLARATION')==-1):
                if sys.argv[2] == 'preauth':
                    filePath = os.path.join(r'/home/ubuntu/index/index/Raksha/attachments_pdf_preauth', sys.argv[1])
                elif sys.argv[2] == 'query':
                    filePath = os.path.join(r'/home/ubuntu/index/index/Raksha/attachments_pdf_query', sys.argv[1])
                elif sys.argv[2] == 'denial':
                    filePath = os.path.join(r'/home/ubuntu/index/index/Raksha/attachments_pdf_denial', sys.argv[1])

                if not os.path.isfile(filePath) :
                
                    fp = open(filePath, 'wb')
                    #print(part.get_payload(decode=True))
                    fp.write(part.get_payload(decode=True))
                    fp.close()