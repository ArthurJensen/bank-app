import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

# Load hidden variables from .env
load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}) 

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

# @app.route('/api/signup', methods=['POST'])
# def signup():
#     data = request.json
#     first_name = data.get('first')
#     last_name = data.get('last')
#     email = data.get('email')
#     password = data.get('password') # In production, hash this!

#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
        
#         # Insert the fresh registration data directly into your Neon cloud database
#         cur.execute(
#             "INSERT INTO users (first_name, email, password_hash) VALUES (%s, %s, %s)",
#             (first_name, email, password)
#         )
#         conn.commit()
        
#         cur.close()
#         conn.close()
#         return jsonify({"status": "success", "message": "Account created successfully!"}), 201
        
#     except psycopg2.errors.UniqueViolation:
#         # Prevents duplicate registrations with the same email address
#         return jsonify({"status": "error", "message": "An account with this email already exists."}), 400
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/api/signup', methods=['POST'])
def signup():

    data = request.json
    first_name = data.get('first')
    email = data.get('email')
    password = data.get('password')

    conn = None
    cur = None

    try:
        print("SIGNUP STARTED")
        print("DATA RECEIVED:", data)

        conn = get_db_connection()
        print("DATABASE CONNECTED")

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (first_name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (first_name, email, password))

        new_user_id = cur.fetchone()[0]
        print("USER CREATED:", new_user_id)

        print("ABOUT TO CREATE ACCOUNT FOR USER:", new_user_id)

        cur.execute("""
            INSERT INTO accounts (user_id, account_type, account_name, balance)
            VALUES (%s, %s, %s, %s)
            RETURNING id, user_id, account_type, account_name, balance
        """, (new_user_id, "checking", "Everyday Checking", 1000))

        new_account = cur.fetchone()
        print("ACCOUNT CREATED:", new_account)

        conn.commit()
        print("COMMIT SUCCESSFUL")

        return jsonify({
            "status": "success",
            "message": "Account created successfully!",
            "user_id": new_user_id,
            "account": {
                "id": new_account[0],
                "user_id": new_account[1],
                "account_type": new_account[2],
                "account_name": new_account[3],
                "balance": str(new_account[4])
            }
        }), 201

    except psycopg2.errors.UniqueViolation as e:
        if conn:
            conn.rollback()
        print("UNIQUE ERROR:", e)
        return jsonify({"status": "error", "message": "Email already exists."}), 400

    except Exception as e:
        if conn:
            conn.rollback()
        print("SIGNUP ERROR:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("DATABASE CLOSED")
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch the name and balance for this specific user ID
        cur.execute("SELECT first_name, balance FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user:
            return jsonify({
                "status": "success", 
                "first_name": user[0], 
                "balance": str(user[1]) # Convert numeric to string for JSON safely
            }), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/api/send-money', methods=['POST'])
def send_money():
    data = request.json

    sender_id = data.get('sender_id')
    recipient_email = data.get('recipient')
    amount = float(data.get('amount'))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Take money away from sender
        cur.execute(
            "UPDATE users SET balance = balance - %s WHERE id = %s",
            (amount, sender_id)
        )

        # 2. Add money to recipient
        cur.execute(
            "UPDATE users SET balance = balance + %s WHERE email = %s",
            (amount, recipient_email)
        )

        # 3. Save both changes together
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Money sent successfully!"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
@app.route("/api/user/<int:user_id>/accounts", methods=["GET"])
def get_user_accounts(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id, account_type, account_name, balance
            FROM accounts
            WHERE user_id = %s
            ORDER BY id
            """,
            (user_id,)
        )

        accounts = cur.fetchall()

        account_list = []

        for account in accounts:
            account_list.append({
                "id": account[0],
                "account_type": account[1],
                "account_name": account[2],
                "balance": float(account[3])
            })

        return {
            "status": "success",
            "accounts": account_list
        }

    except Exception as e:
        print("Accounts fetch error:", e)
        return {
            "status": "error",
            "message": "Could not load accounts"
        }, 500

    finally:
        cur.close()
        conn.close()
        
@app.route('/api/test-send-money', methods=['GET'])
def test_send_money():
    return jsonify({"message": "send money route area exists"})
@app.route('/')
def home():
    return "Bank backend is running"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
