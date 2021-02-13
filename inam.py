import pickle
import base64
import os.path
from random import randint
from datetime import datetime
from pytz import timezone, utc

import mysql.connector
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pdfkit

if not os.path.exists('new_attach'):
    os.mkdir('new_attach')

conn_data = {'host':"iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
        'user':"admin",
        'password':"Welcome1!",
        'database':'python'}

config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def file_no(len):
    return str(randint((10 ** (len - 1)), 10 ** len)) + '_'


def file_blacklist(filename):
    fp = filename
    filename, file_extension = os.path.splitext(fp)
    ext = ['.pdf', '.htm', '.html']
    if file_extension not in ext:
        return False
    if fp.find('ATT00001') != -1:
        return False
    if (fp.find('MDI') != -1) and (fp.find('Query') == -1):
        return False
    if (fp.find('knee') != -1):
        return False
    if (fp.find('KYC') != -1):
        return False
    if fp.find('image') != -1:
        return False
    if (fp.find('DECLARATION') != -1):
        return False
    if (fp.find('Declaration') != -1):
        return False
    if (fp.find('notification') != -1):
        return False
    if (fp.find('CLAIMGENIEPOSTER') != -1):
        return False
    if (fp.find('declar') != -1):
        return False
    if (fp.find('PAYMENT_DETAIL') != -1):
        return False
    return True


def fetch(after, before):
    after, before = str(after), str(before)
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'inamdar_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    q = f"after:{after} before:{before}"
    results = service.users().messages().list(userId='me', labelIds=['INBOX'],
                                              q=q).execute()
    messages = results.get('messages', [])
    if not messages:
        print("No messages found.")
    else:
        print("Message snippets:")
        for message in messages[::-1]:
            id, subject, date, filename, sender = '', '', '', '', ''
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            id = msg['id']
            for i in msg['payload']['headers']:
                if i['name'] == 'Subject':
                    subject = i['value']
                if i['name'] == 'From':
                    sender = i['value']
                    sender = sender.split('<')[-1].replace('>', '')
                if i['name'] == 'Date':
                    tmp = int(msg['internalDate'][:10])
                    date = datetime.fromtimestamp(tmp, utc)
                    # date = i['value']
                    # date = date.split(',')[-1].strip()
                    # format = '%d %b %Y %H:%M:%S %z'
                    # try:
                    #     date = datetime.strptime(date, format)
                    # except:
                    #     pass
                    date = date.astimezone(timezone('Asia/Kolkata')).replace(tzinfo=None)
            flag = 0
            if 'parts' in msg['payload']:
                for j in msg['payload']['parts']:
                    if 'attachmentId' in j['body']:
                        filename = j['filename']
                        filename = filename.replace('.PDF', '.pdf')
                        filename = 'new_attach/' + file_no(4) + filename
                        if file_blacklist(filename):
                            filename = filename.replace(' ', '')
                            a_id = j['body']['attachmentId']
                            attachment = service.users().messages().attachments().get(userId='me', messageId=id,
                                                                                      id=a_id).execute()
                            data = attachment['data']
                            with open(filename, 'wb') as fp:
                                fp.write(base64.urlsafe_b64decode(data))
                            print(filename)
                            flag = 1
            else:
                data = msg['payload']['body']['data']
                filename = 'new_attach/' + file_no(8) + '.pdf'
                with open('new_attach/' + 'temp.html', 'wb') as fp:
                    fp.write(base64.urlsafe_b64decode(data))
                print(filename)
                pdfkit.from_file('new_attach/temp.html', filename, configuration=config)
                flag = 1
            if flag == 0:
                data = msg['payload']['parts'][-1]['body']['data']
                filename = 'new_attach/' + file_no(8) + '.pdf'
                with open('new_attach/' + 'temp.html', 'wb') as fp:
                    fp.write(base64.urlsafe_b64decode(data))
                print(filename)
                pdfkit.from_file('new_attach/temp.html', filename, configuration=config)
                flag = 1
            with mysql.connector.connect(**conn_data) as con:
                cur = con.cursor()
                q = "insert into inamdar_mails values (%s, %s, %s, %s, %s, %s, %s)"
                data = (id, subject, date, str(datetime.now()), os.path.abspath(filename), '', sender)
                cur.execute(q, data)
                con.commit()



if __name__ == '__main__':
    after, before = '1609749000', '1609752600'
    fetch(after, before)
