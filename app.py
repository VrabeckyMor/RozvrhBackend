from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import uuid
import json
import os

app = Flask(__name__)
CORS(app)

# Použij URL pro 'Transaction' mód z dashboardu (port 6543)
# Přidej nakonec ?sslmode=require pokud tam není
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    # Přidáme sslmode=require pro jistotu
    return psycopg2.connect(DATABASE_URL)

_db_initialized = False

def init_db_if_needed():
    global _db_initialized
    if _db_initialized:
        return
    
    conn = None
    try:
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
        _db_initialized = True
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database init failed: {e}")
    finally:
        if conn:
            conn.close()

@app.route('/api/schedule', methods=['POST'])
def save_array():
    init_db_if_needed()
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
    init_db_if_needed()
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

# Pro Vercel nepotřebujeme init_db() na top levelu
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
