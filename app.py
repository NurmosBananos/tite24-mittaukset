# Tämä koodi toimii nyt. 

import os
import traceback
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Tietokannan alustus
def init_db():
    yhteys = sqlite3.connect("mittaukset.db3")
    kursori = yhteys.cursor()
    kursori.execute("""
        CREATE TABLE IF NOT EXISTS mittaukset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aika TEXT,
            lampo_sisa REAL,
            lampo_ulko REAL,
            kosteus_sisa INTEGER,
            kosteus_ulko INTEGER
        )
    """)
    yhteys.commit()
    yhteys.close()

init_db()

@app.route('/')
def index():
    yhteys = sqlite3.connect("mittaukset.db3")
    yhteys.row_factory = sqlite3.Row
    kursori = yhteys.cursor()
    kursori.execute("""
        SELECT aika, lampo_sisa, lampo_ulko, kosteus_sisa, kosteus_ulko
        FROM (
            SELECT * FROM mittaukset
            ORDER BY id DESC
            LIMIT 100
        ) ORDER BY id ASC
    """)
    tiedot = kursori.fetchall()
    yhteys.close()

    return render_template("chart.html", taulukko=tiedot)

@app.route('/lisaa_tieto', methods=['POST'])
def lisaa_tieto():
    try:
        data = request.get_json(force=True)

        aika = data['aika']
        lampo_sisa = data['lampo_sisa']
        lampo_ulko = data['lampo_ulko']
        kosteus_sisa = data['kosteus_sisa']
        kosteus_ulko = data['kosteus_ulko']

        yhteys = sqlite3.connect("mittaukset.db3")
        kursori = yhteys.cursor()
        kursori.execute("""
            INSERT INTO mittaukset (aika, lampo_sisa, lampo_ulko, kosteus_sisa, kosteus_ulko)
            VALUES (?, ?, ?, ?, ?)
        """, (aika, lampo_sisa, lampo_ulko, kosteus_sisa, kosteus_ulko))
        yhteys.commit()
        yhteys.close()

        print(f"Lisättiin: {aika} | Sisä: {lampo_sisa}°C / {kosteus_sisa}% | Ulko: {lampo_ulko}°C / {kosteus_ulko}%")
        socketio.emit('data_update')
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Virhe /lisaa_tieto-reitillä:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Paikallista kehitystä varten
    socketio.run(app, debug=True)
