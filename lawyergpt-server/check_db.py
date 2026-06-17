import sqlite3
conn = sqlite3.connect("lawyergpt.db")
rows = conn.execute("SELECT id, title FROM conversations ORDER BY created_at DESC LIMIT 5").fetchall()
for r in rows:
    print("  ", r[0], "|", r[1])
conn.close()
