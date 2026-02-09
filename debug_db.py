import sqlite3

conn = sqlite3.connect("wh40k.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM units")
print("Units:", cur.fetchone()[0])

cur.execute("SELECT DISTINCT faction FROM units LIMIT 10")
print("Factions:", cur.fetchall())

conn.close()
