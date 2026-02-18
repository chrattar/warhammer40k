import sqlite3

conn = sqlite3.connect("wh40k.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM units")
print("Total units:", cur.fetchone()[0])

cur.execute("SELECT name, faction FROM units WHERE faction LIKE '%knight%'")
rows = cur.fetchall()

print("\nChaos-related units:")
for r in rows:
    print(r)

conn.close()
