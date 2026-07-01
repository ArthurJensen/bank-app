import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

# Load hidden variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app) # Allows your HTML files to talk to this backend

def get_db_connection():
    # Safely connect using variables from the .env file
    return psycopg2.connect(
        host="localhost",
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password') # In production, hash this!

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if user exists with this email and password
        cur.execute(
            "SELECT id, first_name FROM users WHERE email = %s AND password_hash = %s",
            (email, password)
        )
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user:
            return jsonify({
                "status": "success", 
                "message": f"Welcome back, {user[1]}!",
                "user_id": user[0]
            }), 200
        else:
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
