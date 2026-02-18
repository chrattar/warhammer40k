import sqlite3

conn = sqlite3.connect("wh40k.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM weapons")
print("weapons:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM unit_weapons")
print("unit_weapons:", cur.fetchone()[0])

conn.close()
