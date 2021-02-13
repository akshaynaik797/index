import requests
import json
import sys
import http.client
'''
'''
conn = http.client.HTTPSConnection("api.msg91.com")

payload = "{ \"sender\": \"SOCKET\", \"route\": \"4\", \"country\": \"91\", \"sms\": [ { \"message\": \"Message1\", \"to\": [ \"98260XXXXX\", \"98261XXXXX\" ] }, { \"message\": \"Message2\", \"to\": [ \"98260XXXXX\", \"98261XXXXX\" ] } ] }"
'''
'''
headers = {
    'authkey': '167826AqxdlJNZOp5e99d040P1',
    'content-type': "application/json"
    }
API_ENDPOINT ="https://api.msg91.com/api/v2/sendsms"
data={
  "sender": "SOCKET",
  "route": "4",
  "country": "91",
  "sms": [
    {
      "message": sys.argv[1],
      "to": [
        "9676454400"
      ]
    }
  ]
}
'''
r = requests.post(url = API_ENDPOINT, data =json.dumps(data),headers=headers)

pastebin_url = r.text
print("The pastebin URL is:%s"%pastebin_url)
'''
