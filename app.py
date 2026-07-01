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
    # Fetch the unified connection string from your Neon Dashboard
    database_url = os.getenv("DATABASE_URL")
    
    # Connect directly using the Neon connection string (SSL is handled automatically via the URL)
    return psycopg2.connect(database_url)

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

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    first_name = data.get('first')
    last_name = data.get('last')
    email = data.get('email')
    password = data.get('password') # In production, hash this!

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert the fresh registration data directly into your Neon cloud database
        cur.execute(
            "INSERT INTO users (first_name, email, password_hash) VALUES (%s, %s, %s)",
            (first_name, email, password)
        )
        conn.commit()
        
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Account created successfully!"}), 201
        
    except psycopg2.errors.UniqueViolation:
        # Prevents duplicate registrations with the same email address
        return jsonify({"status": "error", "message": "An account with this email already exists."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)