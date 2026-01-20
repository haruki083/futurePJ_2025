from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DB_PATH = 'medical.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =====================================
# HTML を返すルート
# =====================================
@app.route("/")
def index():
    # app.py と同じフォルダに test.html を置くこと
    return send_from_directory('.', 'test.html')

# =====================================
# API: 医療機関 CRUD
# =====================================

@app.route("/api/facilities", methods=["GET"])
def get_facilities():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM facilities ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/facilities", methods=["POST"])
def add_facility():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO facilities (name,type,address,phone,lat,lng)
        VALUES (?,?,?,?,?,?)
    """, (
        data.get("name"),
        data.get("type"),
        data.get("address"),
        data.get("phone"),
        data.get("lat"),
        data.get("lng")
    ))
    conn.commit()
    id = cur.lastrowid
    conn.close()
    return jsonify({"id": id})

@app.route("/api/facilities/<int:id>", methods=["PUT"])
def edit_facility(id):
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE facilities SET name=?, type=?, address=?, phone=?, lat=?, lng=? WHERE id=?
    """, (
        data.get("name"),
        data.get("type"),
        data.get("address"),
        data.get("phone"),
        data.get("lat"),
        data.get("lng"),
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

@app.route("/api/facilities/<int:id>", methods=["DELETE"])
def delete_facility(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM facilities WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

# =====================================
if __name__ == "__main__":
    app.run(debug=True)
