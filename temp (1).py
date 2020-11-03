import sqlite3
from datetime import datetime

def add_time_diff():
    """
    Before calling this function, check if time_diff column is present in db
    Working of function:
    select last row from db
    add time difference between date and downloadtime of last row
    to time_diif coloumn of last row
    works only if required fields are not empty
    if any field is empty then time_diff col will also remains blank
    """
    with sqlite3.connect("database1.db") as con:
        cur = con.cursor()
        b = "SELECT date,downloadtime,row_no  FROM updation_detail_log ORDER BY row_no DESC LIMIT 1"
        cur.execute(b)
        r = cur.fetchone()
        if r[0] is not None and r[1] is not None and r[2] is not None:
            time_diff = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S.%f").timestamp()\
                - datetime.strptime(r[0], "%d/%m/%Y %H:%M:%S").timestamp()
            rowno = r[2]
            query = f"update updation_detail_log set time_diff={int(time_diff)} where row_no={r[2]}"
            cur.execute(query)
add_time_diff()