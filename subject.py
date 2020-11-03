from flask import *
import sqlite3

#rows=["a","b","c","d"]
global rows
global email_master_id
app = Flask(__name__)

@app.route("/")
def index():
    con = sqlite3.connect("database1.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select IC_name from IC_name")
    rows = cur.fetchall()

    return render_template("index1.html",rows = rows)


@app.route("/viewdata",methods = ["POST","GET"])
def viewdata():


    if request.method == "POST":
        id = request.form["id"]
        column = request.form["column"]
        addvalue = request.form["addvalue"]
        deletevalue = request.form["deletevalue"]

        with sqlite3.connect("database1.db") as con:
            cur = con.cursor()

            if len(addvalue) != 0:
                b="INSERT INTO " +column+ " VALUES ("+id+","+"'"+addvalue+"')"
                cur.execute(b)
                cur.execute("SELECT COUNT(*) FROM email_master")
                tempv=cur.fetchall()
                email_master_id=int(tempv[0][0])
                email_master_id=str(email_master_id+1)
                col = column.lower()
                b="INSERT INTO email_master VALUES ("+email_master_id+","+"'"+addvalue+"'"+","+"'"+col+"'"+","+id+")"
                #b="INSERT INTO email_master VALUES (10,'t','t',10)"
                cur.execute(b)

            if len(deletevalue) != 0:
                b="DELETE FROM " +column+ " WHERE " +column+ " = '"+deletevalue+"'"
                cur.execute(b)

                b="DELETE FROM email_master WHERE subject  = '"+deletevalue+"' AND ic_id = " +id 
                cur.execute(b)

            b="SELECT " +column+" FROM " +column+" WHERE IC ="+id
            cur.execute(b)
            rows = cur.fetchall()
            msg=rows
    return render_template("index1.html",rows = rows)
