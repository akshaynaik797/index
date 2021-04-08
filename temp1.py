from app import get_exp_status_table, get_status_table, get_api_url
import mysql.connector

from custom_parallel import conn_data

with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    q = "insert into auto_post (row_no, flag) values (%s, %s)"
    cur.execute(q, ('a', 'b'))
    con.commit()