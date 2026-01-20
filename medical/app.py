from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "medical.db")

# -----------------------
# DB接続
# -----------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------
# テーブル自動作成
# -----------------------
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            address TEXT,
            phone TEXT,
            note TEXT,
            lat REAL,
            lng REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# -----------------------
# HTMLルート
# -----------------------
@app.route("/")
def index():
    # app.py と同じフォルダに test.html を置く
    return send_from_directory('.', 'test.html')

# -----------------------
# API: すべての医療機関取得
# -----------------------
@app.route("/api/facilities", methods=["GET"])
def get_facilities():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM facilities ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# -----------------------
# API: 医療機関追加
# -----------------------
@app.route("/api/facilities", methods=["POST"])
def add_facility():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO facilities (name,type,address,phone,note,lat,lng)
        VALUES (?,?,?,?,?,?,?)
    """, (
        data.get("name"),
        data.get("type"),
        data.get("address"),
        data.get("phone"),
        data.get("note"),
        data.get("lat"),
        data.get("lng")
    ))
    conn.commit()
    id = cur.lastrowid
    conn.close()
    return jsonify({"id": id})

# -----------------------
# API: 医療機関編集
# -----------------------
@app.route("/api/facilities/<int:id>", methods=["PUT"])
def edit_facility(id):
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE facilities SET name=?, type=?, address=?, phone=?, note=?, lat=?, lng=? WHERE id=?
    """, (
        data.get("name"),
        data.get("type"),
        data.get("address"),
        data.get("phone"),
        data.get("note"),
        data.get("lat"),
        data.get("lng"),
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

# -----------------------
# API: 医療機関削除
# -----------------------
@app.route("/api/facilities/<int:id>", methods=["DELETE"])
def delete_facility(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM facilities WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

# -----------------------
# メイン
# -----------------------
if __name__ == "__main__":
    init_db()  # ← 起動時にテーブル作成
    app.run(debug=True)
