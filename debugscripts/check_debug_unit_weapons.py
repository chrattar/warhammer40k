import sqlite3

conn = sqlite3.connect("wh40k.db")
cur = conn.cursor()

cur.execute("SELECT unit_id FROM unit_weapons LIMIT 20")
rows = cur.fetchall()

for r in rows:
    print(r[0])

conn.close()
