from app import get_exp_status_table, get_status_table, get_api_url
import mysql.connector

from custom_parallel import conn_data

with mysql.connector.connect(**conn_data) as mydb:
    cur = mydb.cursor()
    query = """SELECT hos_id,preauthid,amount,`status`, \
              lettertime,policyno,memberid,row_no,comment, doa, dod from updation_detail_log WHERE error IS NULL and completed is NULL"""
    cur.execute(q)
    r = cur.fetchall()

row = {}
url = get_api_url(row['hos_id'], 'getupdateDetailsLog')
payload = {
'memberid': row['memberid'],
'preauthid': row['preauthid'],
'policyno': row['policyno'],
'comment': row['comment']
}

r = get_status_table()
for curs, status in r:
    pass