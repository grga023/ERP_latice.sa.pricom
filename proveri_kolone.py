import sqlite3

# Putanja do tvoje baze (prilagodi ako je drugačije)
db_path = 'data/erp.db'

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("PRAGMA table_info(orders)")
columns = c.fetchall()

print("Kolone u tabeli 'orders':")
for col in columns:
    print(col)

conn.close()
