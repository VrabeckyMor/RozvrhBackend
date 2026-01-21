from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import json
import os

app = Flask(__name__)
CORS(app)

# Připojovací řetězec z environment proměnné (pro lokální testování můžeš nahradit svým stringem)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:[TVOJE-HESLO]@db.kvjwbiucxsdfipdcetfv.supabase.co:5432/postgres')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS arrays (
            token TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    c.close()
    conn.close()

# Inicializace tabulky (pokud neexistuje)
init_db()

@app.route('/api/schedule', methods=['POST'])
def save_array():
    try:
        incoming_data = request.get_json()
        stringified = json.dumps(incoming_data)
        token = str(uuid.uuid4())

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO arrays (token, data) VALUES (%s, %s)', (token, stringified))
        conn.commit()
        c.close()
        conn.close()

        return jsonify({'token': token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get/<token>', methods=['GET'])
def get_array(token):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT data FROM arrays WHERE token = %s', (token,))
        row = c.fetchone()
        c.close()
        conn.close()

        if row:
            return jsonify({'data': json.loads(row[0])}), 200
        else:
            return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
