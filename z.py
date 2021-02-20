import csv
import subprocess
import mysql.connector
from custom_parallel import conn_data
def run():
    ins = "MDINDIA"
    ct = "query"
    fpath = "/home/akshay/Downloads/z2/MDI5983457_Query_NO_1_45985.pdf"
    subject = "Claim Query Letter- MemberID:-N90A0175TODAY	Claim No:-90222021477211"
    l_time = "07/12/2020 18:22:25"
    hid = "test"
    mail_id = 'asdasdasda'
    subprocess.run(
              ["python", ins + "_" + ct + ".py", fpath, str(999999), ins,
               ct, subject, l_time, hid, mail_id])

def check():
    a, b = "/home/akshay/Downloads/rdp.csv", "/home/akshay/Downloads/ubuntu.csv"
    c, d = "/home/akshay/Downloads/rdpgraph.csv", "/home/akshay/Downloads/ubuntugraph.csv"
    rdp, ubu = set(), set()
    rdpgraph, ubugraph = set(), set()
    with open(a) as csv_file:
        csv_reader1 = csv.reader(csv_file, delimiter=',')
        for i in csv_reader1:
            rdp.add(i[7])
    with open(b) as csv_file:
        csv_reader2 = csv.reader(csv_file, delimiter=',')
        for i in csv_reader2:
            ubu.add(i[7])

    with open(c) as csv_file:
        csv_reader3 = csv.reader(csv_file, delimiter=',')
        for i in csv_reader3:
            rdpgraph.add(i[2])
    with open(d) as csv_file:
        csv_reader4 = csv.reader(csv_file, delimiter=',')
        for i in csv_reader4:
            ubugraph.add(i[2])
    # common = rdp.intersection(ubu)
    missubu = rdp.difference(ubu)
    missrdp = ubu.difference(rdp)
    # missubugraph = rdpgraph.difference(ubugraph)
    # missrdpgraph = ubugraph.difference(rdpgraph)
    temp = rdp.difference(ubu)
    # temp1 = ubu.difference(rdpgraph)
    # temp2 = missubu.difference(temp)
    with open('/home/akshay/Downloads/missubu.csv', mode='w+') as c:
        fp = csv.writer(c, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        with open(a) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            with mysql.connector.connect(**conn_data) as mydb:
                cur = mydb.cursor()
                for i in csv_reader:
                    for j in missubu:
                        if i[7] == j:
                            query = "select * from graphApi where subject = %s and date = %s limit 1"
                            # query = "select * from updation_detail_log where insurerid = %s and process = %s limit 1"
                            cur.execute(query, (i[6], i[7]))
                            result = cur.fetchone()
                            if result is not None:
                                flag = result[5]
                            else:
                                flag = 'not in graph'
                            fp.writerow([flag, i[7], i[1], i[2], i[6]])

    with open('/home/akshay/Downloads/missubu.csv') as csv_file:
        in_graph, not_in_graph = 0, 0
        csv_reader = csv.reader(csv_file, delimiter=',')
        mega = []
        with mysql.connector.connect(**conn_data) as mydb:
            cur = mydb.cursor()
            for i in csv_reader:
                # query = "select * from graphApi where subject = %s and date = %s limit 1"
                query = "select * from updation_detail_log where insurerid = %s and process = %s limit 1"
                cur.execute(query, (i[1], i[2]))
                result = cur.fetchone()
                if result is not None:
                    # print(result[2], result[5], i)
                    in_graph += 1
                else:
                    print(i[1], i[2])
                    not_in_graph += 1
            print("in", in_graph, not_in_graph)


if __name__ == "__main__":
    run()
    pass