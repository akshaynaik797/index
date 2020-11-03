import email
import imaplib

inamh = (1, 'inamdar hospital', 'mediclaim@inamdarhospital.org', 'Mediclaim@2019', 'imap.gmail.com', 'inbox', 'X')
maxh = (2, 'Max PPT', 'Tpappg@maxhealthcare.com', 'Sept@2020', 'outlook.office365.com', 'inbox', 'X')

def mail_body_to_text(mailsubject, hid):
    if 'Max' in hid:
        server = maxh[4]
        user = maxh[2]
        pwd = maxh[3]
    else:
        server = inamh[4]
        user = inamh[2]
        pwd = inamh[3]

    mail = imaplib.IMAP4_SSL(server)
    mail.login(user, pwd)
    mail.select("inbox", readonly=True)
    type, data = mail.search(None, f'(SUBJECT "{mailsubject}")')
    mid = data[0]
    result, data = mail.fetch(mid, "(RFC822)")
    raw_email = data[0][1].decode('utf-8')
    email_message = email.message_from_string(raw_email)
    subject = email_message['Subject']
    b = email_message
    body = ""
    if b.is_multipart():
        for part in b.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        body = b.get_payload(decode=True)
    text = body.decode("utf-8")
    with open('city/city.txt', 'w') as f:
        f.write(text)
        return text
    return None


if __name__ == "__main__":
    subject = 'Payment Advice-BCS_ECS9522020061219320025_5697_952'
    hid = 'inamdar hospital'
    mail_body_to_text(subject, hid)
