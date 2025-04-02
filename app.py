import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import sqlite3 #tietokantakirjasto
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

#tietokannan teko
yhteys = sqlite3.connect('mittaukset.db3')
kursori = yhteys.cursor()
kursori.execute("CREATE TABLE IF NOT EXISTS mittaukset (id INTEGER PRIMARY KEY, paiva TEXT, mittaus INTEGER)")
yhteys.commit()
yhteys.close()

mittaukset = dict() # {'maanantai' : 7}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', taulukko=mittaukset)

@app.route('/lisaa_tieto', methods=['POST'])
def lisaa_tieto():
    data = request.get_json(force=True)
    if 'mittaus' in data and isinstance(data['mittaus'], list) and len(data['mittaus']) == 2:
        mittaukset[data['mittaus'][0]] = data['mittaus'][1]
        socketio.emit('data_update')
        return "200"
    return "400 Bad Request", 400

if __name__ == '__main__':
    socketio.run(app, debug=True)
