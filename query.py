import sqlite3
conn = sqlite3.connect("wh40k.db")
cur = conn.cursor()
cur.execute("SELECT DISTINCT faction FROM units ORDER BY faction")
print(cur.fetchall())
conn.close()
