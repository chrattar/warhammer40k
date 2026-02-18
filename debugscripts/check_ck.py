import sqlite3

c = sqlite3.connect("wh40k.db")
cur = c.cursor()

cur.execute("select count(*) from units where faction like 'Chaos Chaos Knights%'")
print("Total:", cur.fetchone())

cur.execute(
    "select count(*) from units where faction like 'Chaos Chaos Knights%' and legends != 'Legends-NotActive'"
)
print("Non-legends:", cur.fetchone())

c.close()
