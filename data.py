import requests
import sys
import openpyxl
import subprocess
print("--------------------	")
print(sys.argv)
data = {
	'preauthid':sys.argv[1],
	#'pname': sys.argv[10],
    'amount':sys.argv[2],
    'status':sys.argv[5],
	'process':sys.argv[4],
	'lettertime':sys.argv[6],
	'policyno':sys.argv[3],
	'memberid':sys.argv[9],
	'comment':'test'
	}

prinr(data)
