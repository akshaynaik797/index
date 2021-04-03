import mysql.connector
import requests

from custom_app import get_api_url
from custom_parallel import conn_data

def get_status_table():
    r = []
    with mysql.connector.connect(**conn_data) as mydb:
        cur = mydb.cursor()
        q = "select current_status, status from status_table"
        cur.execute(q)
        r = cur.fetchall()
    return r

def get_exp_status_table():
    r = []
    with mysql.connector.connect(**conn_data) as mydb:
        cur = mydb.cursor()
        q = "select current_status, status, insurer from exception_status_table"
        cur.execute(q)
        r = cur.fetchall()
    return r


def auto_post():
    fields = ("runno","insurerid","process","downloadtime","starttime","endtime","emailsubject","date",
              "fieldreadflag","failedfields","apicalledflag","apiparameter","apiresult","sms","error",
              "row_no","emailid","completed","file_path","mail_id","hos_id","preauthid","amount","status",
              "lettertime","policyno","memberid","comment","time_difference","diagno","insname",
              "doa","dod","corp","polhol","jobid","time_difference2","weightage")
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select * from updation_detail_log WHERE error IS NULL and completed is NULL"
        ####for test purpose
        # q = "select * from updation_detail_log_copy WHERE row_no=29928"
        cur.execute(q)
        r = cur.fetchall()
        data = []
        for row in r:
            temp = {}
            for k, v in zip(fields, row):
                temp[k] = v
            data.append(temp)
    for row in data:
        temp = {}
        payload = {
            'memberid': row['memberid'],
            'preauthid': row['preauthid'],
            'policyno': row['policyno'],
            'comment': row['comment']
        }
        for i, j in payload.items():
            if j == None:
                temp[i] = ''
            else:
                temp[i] = j
        payload = temp
        url = get_api_url(row['hos_id'], 'getupdateDetailsLog')
        response = requests.post(url, data=payload)
        result = response.json()
        if 'searchdata' in result and 'current_status' in result['searchdata']:
            row["searchdata"] = result['searchdata']
            tag_id = ''
            if 'wait' in row['status']:
                tag_id = 'Q02'
            if 'nial' in row['status']:
                tag_id = 'D05'
            r = get_status_table()
            for curs, status in r:
                if curs in row["searchdata"]["current_status"] and status == row['status']:
                    requests.post(url_for("postUpdateLog", _external=True),
                                  data={"row_no": row['row_no'],
                                        "completed": "A",
                                        "preauthid": row['preauthid'],
                                        "amount": row['amount'],
                                        "status": row['status'],
                                        "lettertime": row['lettertime'],
                                        "policyno": row['policyno'],
                                        "memberid": row['memberid'],
                                        "comment": row['comment'],
                                        "tag_id": tag_id,
                                        "refno": row["searchdata"]['refno']})

            r = get_exp_status_table()
            for curs, status, insurer in r:
                if curs in row["searchdata"]["current_status"] and status == row['status'] and insurer == \
                        row['insurerid']:
                    requests.post(url_for("postUpdateLog", _external=True),
                                  data={"row_no": row['row_no'],
                                        "completed": "A",
                                        "preauthid": row['preauthid'],
                                        "amount": row['amount'],
                                        "status": row['status'],
                                        "lettertime": row['lettertime'],
                                        "policyno": row['policyno'],
                                        "memberid": row['memberid'],
                                        "comment": row['comment'],
                                        "tag_id": tag_id,
                                        "refno": row["searchdata"]['refno']})

if __name__ == '__main__':
    auto_post()