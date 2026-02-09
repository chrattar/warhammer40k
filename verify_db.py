import sqlite3

conn = sqlite3.connect("wh40k.db")
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

print("Tables:")
for t in tables:
    print(" -", t[0])

conn.close()
