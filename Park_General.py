import os
import sys
import struct, time
import subprocess
from datetime import date
import datetime
import openpyxl
import pdftotext
import time
import requests
from make_log import log_exceptions
now = datetime.datetime.now()
try:

    subprocess.run(["python", "updation.py","1","max1","1",sys.argv[2]])
    subprocess.run(["python", "updation.py","1","max","2",sys.argv[3]])
    subprocess.run(["python", "updation.py","1","max","3",sys.argv[4]])
    subprocess.run(["python", "updation.py","1","max","5",str(now)])
    subprocess.run(["python", "updation.py","1","max","7",sys.argv[5]])
    subprocess.run(["python", "updation.py","1","max","8",sys.argv[6]])

    with open(sys.argv[1], "rb") as f:
        pdf = pdftotext.PDF(f)

    with open('Park/output.txt', 'w') as f:
        f.write(" ".join(pdf))
    with open('Park/output.txt', 'r') as myfile:
        f = myfile.read()

    try:
        if f.find("Authorisation For the Cashless request for Hospitalisation")!= -1:
            hg=[]

            w=f.find('Authorisation No')+len('Authorisation No')
            g=f[w:]
            u=g.find('\n')+w
            tempString=f[w:u]
            templist=tempString.split('/')
            if len(templist) >1:
                AuthorisationNo=templist[1]
            else:
                AuthorisationNo=templist[0]
            hg.append(AuthorisationNo)

            status='Approved'

            w=f.find('payment up to Rs.')+len('payment up to Rs.')
            g=f[w:]
            u=g.find('(Rs')+w
            hg.append(f[w:u])

            w=f.find('Policy number')+len('Policy number')
            g=f[w:]
            u=g.find('\n')+w
            hg.append(f[w:u])

            w=f.find('Patient  ')+len('Patient  ')
            g=f[w:]
            u=g.find('to')+w
            tempString=f[w:u]
            u=tempString.rfind(' ')+w
            hg.append(f[w:u])

            hg=[sub.replace(':','') for sub in hg]
            hg=[sub.replace('  ','') for sub in hg]
            hg=[sub.replace('-','') for sub in hg]
            hg=[sub.replace(',','') for sub in hg]
            hg=[sub.replace('(Rs','') for sub in hg]
            print(hg)


            subprocess.run(["python", "updation.py","1","max","9",'Yes'])
            subprocess.run(["python", "updation.py","1","max","10",'NA'])

            try:
                subprocess.run(["python", "test_api.py",hg[0],hg[1],hg[2],' ',status,sys.argv[6],sys.argv[1],' ',' ',hg[3]])
                subprocess.run(["python", "updation.py","1","max","11",'Yes'])
            except Exception as e:
                subprocess.run(["python", "updation.py","1","max","11",'No'])

        elif f.find("Subject") != -1 and f.find("Query For the Cashless request")!=-1:
            status='Information Awaiting'
            hg=[]

            if f.find('Ref No') != -1:
                w=f.find('Ref No')+len('Ref No')
                g=f[w:]
                u=g.find('\n')+w
                tempString=f[w:u]
                templist=tempString.split('/')
                if len(templist) >1:
                    refNo=templist[1]
                else:
                    refNo=templist[0]
                hg.append(refNo)

            if f.find('Policy No') != -1:
                w=f.find('Policy No')+len('Policy No')
                g=f[w:]
                u=g.find('\n')+w
                hg.append(f[w:u])

            if f.find('Patient:') != -1:
                w=f.find('Patient:')+len('Patient:')
                g=f[w:]
                u=g.find('\n')+w
                hg.append(f[w:u])

            hg=[sub.replace(':','') for sub in hg]
            hg=[sub.replace('  ','') for sub in hg]
            hg=[sub.replace('-','') for sub in hg]
            print(hg)

            subprocess.run(["python", "updation.py","1","max","9",'Yes'])
            subprocess.run(["python", "updation.py","1","max","10",'NA'])

            try:
                subprocess.run(["python", "test_api.py",hg[0],' ',hg[1],' ',status,sys.argv[6],sys.argv[1],' ',' ',hg[2]])
                subprocess.run(["python", "updation.py","1","max","11",'Yes'])
            except Exception as e:
                subprocess.run(["python", "updation.py","1","max","11",'No'])
        else:
           print("attachment not present")

    except Exception as e:
        subprocess.run(["python", "updation.py","1","max","9",'Yes'])
        subprocess.run(["python", "updation.py","1","max","11",'No'])
    now = datetime.datetime.now()

    subprocess.run(["python", "updation.py","1","max","6",str(now)])
except:
    log_exceptions()