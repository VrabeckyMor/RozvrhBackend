from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import uuid
import json

app = Flask(__name__)
CORS(app)

# Inicializace databáze
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS arrays (
            token TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/schedule', methods=['POST'])
def save_array():
    try:
        incoming_data = request.get_json()
        stringified = json.dumps(incoming_data)
        token = str(uuid.uuid4())

        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('INSERT INTO arrays (token, data) VALUES (?, ?)', (token, stringified))
        conn.commit()
        conn.close()

        return jsonify({'token': token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get/<token>', methods=['GET'])
def get_array(token):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT data FROM arrays WHERE token = ?', (token,))
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({'data': json.loads(row[0])}), 200
    else:
        return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)