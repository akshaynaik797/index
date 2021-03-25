import psycopg2

def write(x):
    value, time = x[0], x[1]
    print(f"job running is {x[0]}")
    conn = psycopg2.connect(database="temp", user="akshay", password="41424344", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    q = f"begin;" \
        f"insert into jobs (jobid, data) values ('{x[0]}', '{x[1]}');select pg_sleep('{x[1]}');" \
        f"commit;"
    # f"insert into jobs (jobid, data) values ('{x[0]}', '{x[1]}');select pg_sleep('{x[1]}');" \
    cur.execute(q)
if __name__ == "__main__":
    x = (1, 10)
    write(x)