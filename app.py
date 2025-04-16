import gevent.monkey
gevent.monkey.patch_all()  # TÄRKEÄÄ: tämä tulee ennen mitään muita importteja

import os
import traceback
import sqlite3

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent')  # Käytetään gevent-ajuria

# --- Tietokannan alustus --
def init_db():
    conn = sqlite3.connect("mittaukset.db3")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mittaukset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aika TEXT,
            lampo_sisa REAL,
            lampo_ulko REAL,
            kosteus_sisa INTEGER,
            kosteus_ulko INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect("mittaukset.db3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT aika, lampo_sisa, lampo_ulko, kosteus_sisa, kosteus_ulko
        FROM (
            SELECT * FROM mittaukset
            ORDER BY id ASC
            LIMIT 100
        ) ORDER BY id DESC
    """)
    
    data = cursor.fetchall()
    conn.close()
    return render_template("chart.html", taulukko=data)

@app.route('/lisaa_tieto', methods=['POST'])
def lisaa_tieto():
    try:
        data = request.get_json(force=True)
        print("POST /lisaa_tieto vastaanotettu data:", data)  # Tulostetaan vastaanotettu data

        # Odotamme seuraavia kenttiä: "aika", "lampo_sisa", "lampo_ulko", "kosteus_sisa", "kosteus_ulko"
        aika = data['aika']
        lampo_sisa = data['lampo_sisa']
        lampo_ulko = data['lampo_ulko']
        kosteus_sisa = data['kosteus_sisa']
        kosteus_ulko = data['kosteus_ulko']

        conn = sqlite3.connect("mittaukset.db3")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mittaukset (aika, lampo_sisa, lampo_ulko, kosteus_sisa, kosteus_ulko)
            VALUES (?, ?, ?, ?, ?)
        """, (aika, lampo_sisa, lampo_ulko, kosteus_sisa, kosteus_ulko))
        conn.commit()
                # Poista vanhat rivit (säilytetään vain uusimmat 100)
        cursor.execute("""
            DELETE FROM mittaukset
            WHERE id NOT IN (
                SELECT id FROM mittaukset
                ORDER BY id DESC
                LIMIT 100
            )
        """)
        conn.commit()

        conn.close()

        print(f"Lisättiin: {aika} | Sisä: {lampo_sisa}°C / {kosteus_sisa}% | Ulko: {lampo_ulko}°C / {kosteus_ulko}%")
        print("SocketIO: Event lähetetään")  # Ilmoitetaan eventin lähetyksestä

        socketio.emit('data_update')
        return jsonify({"STATUS": "OK"}), 200

    except Exception as e:
        print("Virhe /lisaa_tieto-reitillä:")
        traceback.print_exc()
        return jsonify({"ERROR": str(e)}), 500

if __name__ == '__main__':
    print("Käynnistetään palvelin osoitteessa http://127.0.0.1:5000 ...")
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, use_reloader=False)
