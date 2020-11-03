import requests
import json

serverToken = 'AbAAAKXlyywA:APA91bFI-NyB5RpfiSyk5Sd6guWtL5GeHNTBhLFREFFxukrqOqxYckIgIc1MIcXS_7m1qEHiL357oUp7e1bbpRHsREbSmRBp8KVWpMVc0voO91q7OLgbRaPlHN5yOf6IQaWdE0rtu-Q1'
deviceToken = 'd346ibQQRsCrvMjNKpuU3G:APA91bG-SLTn03HHRe5xU-In0Y2d8wSimalGTvHXZc8WRbCUGPcZnEyfg6V-WBLbRsj2dJfEatuEjInnHWhWGzHAa8-OfpuD7_WO_Dvj_zr1I7dTHa93p3fc21-JwypjYxTLlcli3kMW'



headers = {
    'Content-Type': 'application/json',
    'Authorization': 'key=' + serverToken,
}

body = {
    'notification': {'title': 'Is it working?',
                     'body': 'So its working?'
                     },
    'to': deviceToken,
    'priority': 'high',

}
response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
print(response.status_code)
print(response.json())