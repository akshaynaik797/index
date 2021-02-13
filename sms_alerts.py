import mysql.connector
import requests
import json
from datetime import datetime
from custom_parallel import conn_data

headers = {
    'authkey': '167826AqxdlJNZOp5e99d040P1',
    'content-type': "application/json"
}
API_ENDPOINT = "https://api.msg91.com/api/v2/sendsms"


def send_sms(message):
    pass


if __name__ == '__main__':
    send_sms('test message')
