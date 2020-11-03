import imaplib, email
from email.header import decode_header


SMTP_SERVER = 'outlook.office365.com'
e_id = 'Tpappg@maxhealthcare.com'
pswd = 'May@2020'
subject = 'Settlement of your Claim Reference :CCN# 22589691 under policy#\r\n H0230972'

data = {'server':SMTP_SERVER,
        'hospmail':e_id,
        'pass':pswd,
        'subject':subject}

def read_from_delete(data):
    subject = data['subject']
    mail = imaplib.IMAP4_SSL(data['server'])
    mail.login(data['hospmail'], data['pass'])
    if data['hospmail'] == 'Tpappg@maxhealthcare.com':
        inbox = '"Deleted Items"'
        # inbox = 'inbox'
    else:
        inbox = '"[Gmail]/Trash"'
    mail.select(inbox, readonly=True)
    type, data = mail.search(None, f'(SUBJECT "{subject}")')
    mid = data[0] #this is the list, get last element and assign it to mid
    ma=[]
    ma.append(mid.split())
    result, data = mail.fetch(ma[0][-1], "(RFC822)")
    if result == 'OK':
        return data
        pass
    else:
        return None

def check_subject(subject, syssubject, mail):
    fil = subject
    fil = fil.replace("\r", "")
    fil = fil.replace("\n", "")
    subject = fil
    syssubject = syssubject.replace("\r", "")
    syssubject = syssubject.replace("\n", "")
    if subject.find('UTF') != -1:
        subject = decode_header(mail.email_message['Subject'])
        subject = subject[0]
        subject = subject[0].decode()
    elif subject.find('utf') != -1:
        subject = decode_header(mail.email_message['Subject'])
        subject = subject[0]
        subject = subject[0].decode()
    if syssubject.find('UTF') != -1:
        syssubject = decode_header(mail.email_message['Subject'])
        syssubject = syssubject[0]
        syssubject = syssubject[0].decode()
    elif syssubject.find('utf') != -1:
        syssubject = decode_header(mail.email_message['Subject'])
        syssubject = syssubject[0]
        syssubject = syssubject[0].decode()
    if subject != syssubject:
        result = 'Changed'
        # return result
        return result, syssubject
    # return None
    return None, syssubject

if __name__ == '__main__':
    print(read_from_delete(data))