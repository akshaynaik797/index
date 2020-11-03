import requests
import sys
import openpyxl

files={'doc':open('/home/shivam/Desktop/vnu_scripts/automation/aditya/attachments_pdf_final/11-19-0006310-00.pdf', 'rb')}
#files = {'doc': open(sys.argv[7],  'rb')}
API_ENDPOINT ="https://vnusoftware.com/iclaimtest/api/preauth"

data = {'preauthid':'OC-20-1002-8429-00009998', 
        'amount':'19603.00', 
        'status':'Approved',
	'process':'Pa',
	'lettertime':'20/04/2020 12:30:00',
	'policyno':'11-19-0006310-00',
	'memberid':'',
	'comment':'test'
	}
r = requests.post(url = API_ENDPOINT, data = data , files = files)
pastebin_url = r.text
print(pastebin_url)
