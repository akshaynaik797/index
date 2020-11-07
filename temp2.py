import psycopg2

conn = psycopg2.connect(database="temp", user = "akshay", password = "41424344", host = "127.0.0.1", port = "5432")
cur = conn.cursor()
cur.execute('SELECT version()')
db_version = cur.fetchone()
print(db_version)
pass