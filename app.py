import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

# Load hidden variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app) # Allows your HTML files to talk to this backend[cite: 1]

def get_db_connection():
    # Fetch the unified connection string from your Neon Dashboard
    database_url = os.getenv("DATABASE_URL")
    
    # Connect directly using the Neon connection string (SSL is handled automatically via the URL)
    return psycopg2.connect(database_url)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json[cite: 1]
    email = data.get('email')[cite: 1]
    password = data.get('password') # In production, hash this![cite: 1]

    try:
        conn = get_db_connection()
        cur = conn.cursor()[cite: 1]
        
        # Check if user exists with this email and password
        cur.execute(
            "SELECT id, first_name FROM users WHERE email = %s AND password_hash = %s",
            (email, password)[cite: 1]
        )
        user = cur.fetchone()[cite: 1]
        
        cur.close()[cite: 1]
        conn.close()[cite: 1]

        if user:
            return jsonify({
                "status": "success", 
                "message": f"Welcome back, {user[1]}!",
                "user_id": user[0]
            }), 200[cite: 1]
        else:
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401[cite: 1]

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500[cite: 1]

if __name__ == '__main__':
    app.run(debug=True, port=5000)[cite: 1]