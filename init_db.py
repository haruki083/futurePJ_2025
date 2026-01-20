import sqlite3

conn = sqlite3.connect("medical.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS facilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    address TEXT,
    phone TEXT,
    lat REAL,
    lng REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("DB & facilitiesテーブル作成完了")
