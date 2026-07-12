import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

# Load hidden variables from .env
load_dotenv()

import resend
import secrets
from datetime import datetime, timedelta

resend.api_key = os.getenv("RESEND_API_KEY")

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}) 

def get_db_connection():
    # Fetch the unified connection string from your Neon Dashboard
    database_url = os.getenv("DATABASE_URL")
    
    # Connect directly using the Neon connection string (SSL is handled automatically via the URL)
    return psycopg2.connect(database_url)

@app.route('/api/login', methods=['POST']) # send(post) to flask at api/login
def login(): # a function
    data = request.json #the json frontend sent
    # now, data is the json sent, contain a email/password, then you extract that info
    email = data.get('email') #now variables
    password = data.get('password') # In production, hash this!

    try:
        conn = get_db_connection() #opens a connection to neon database, example: phoneline
        cur = conn.cursor() #connection is phoneline, cursor is a person
        
        # run sqlcode: SELECT the ID, and first_name
        # from user table in database
        # where a email column and password column contain those two %s which are email/password respectivly
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
            INSERT INTO users (first_name, email, password_hash, balance)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (first_name, email, password, 1000))

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

@app.route("/api/user/<int:user_id>/accounts", methods=["GET"])
def get_user_accounts(user_id):

    # Connect to the PostgreSQL database
    conn = get_db_connection()

    # Create a cursor so we can execute SQL queries
    cur = conn.cursor()

    try:

        # Get every account that belongs to this user
        cur.execute(
            """
            SELECT id, account_type, account_name, balance
            FROM accounts
            WHERE user_id = %s
            ORDER BY id
            """,
            (user_id,)   # Replace %s with the user's ID safely
        )

        # Store all rows returned from the database
        accounts = cur.fetchall()

        # This list will hold the account data in JSON format
        account_list = []

        # Convert each SQL row into a Python dictionary
        for account in accounts:
            account_list.append({

                # Account's database ID
                "id": account[0],

                # Example: "checking" or "savings"
                "account_type": account[1],

                # Example: "Everyday Checking"
                "account_name": account[2],

                # Convert PostgreSQL numeric type into a normal float
                "balance": float(account[3])
            })

        # Ask PostgreSQL to calculate the total balance of ALL accounts
        # that belong to this user
        cur.execute(
            """
            SELECT COALESCE(SUM(balance), 0)
            FROM accounts
            WHERE user_id = %s
            """,
            (user_id,)
        )

        # Get the total balance returned by PostgreSQL
        # Example:
        # Checking = 1000
        # Savings = 500
        # High Yield = 2500
        # total_balance = 4000
        total_balance = cur.fetchone()[0]

        # Send everything back to the frontend
        return jsonify({

            # Indicates the request worked
            "status": "success",

            # List containing every account
            "accounts": account_list,

            # Total money across every account
            "total_accounts_balance": float(total_balance)

        }), 200

    except Exception as e:

        # Print the error to the terminal for debugging
        print("Accounts fetch error:", e)

        # Send an error response back to the frontend
        return jsonify({
            "status": "error",
            "message": "Could not load accounts"
        }), 500

    finally:

        # Always close the cursor
        cur.close()

        # Always close the database connection
        conn.close()
@app.route('/api/create-account', methods=['POST'])
def create_account():
    data = request.json
    user_id = data.get('user_id')
    account_type = data.get('account_type')   # "checking" or "savings"
    account_name = data.get('account_name')   # display name

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert the new account with a starting balance of 0
        cur.execute("""
            INSERT INTO accounts (user_id, account_type, account_name, balance)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, account_type, account_name, 1000))

        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        # Generate a readable account number from the database id
        account_number = f"47{new_id:07d}"
        formatted = f"{account_number[:4]} {account_number[4:7]} {account_number[7:]}"

        return jsonify({
            "status": "success",
            "account_id": new_id,
            "account_number": formatted
        }), 201

    except Exception as e:
        print("CREATE ACCOUNT ERROR:", e)
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

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(hours=1)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Remove any existing reset token for this email
        cur.execute("DELETE FROM password_resets WHERE email = %s", (email,))

        # Store the new token with expiry
        cur.execute(
            "INSERT INTO password_resets (email, token, expires_at) VALUES (%s, %s, %s)",
            (email, token, expires)
        )
        conn.commit()
        cur.close()
        conn.close()

        # Build the reset link
        reset_link = f"https://bank-app-owi0.onrender.com/reset-password.html?token={token}"

        # Send the email via Resend
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Reset your Meridian Trust password",
            "html": f"""
                <div style="font-family:sans-serif;max-width:480px;margin:0 auto;">
                    <h2 style="color:#1B2430;">Reset your password</h2>
                    <p>We received a request to reset your Meridian Trust password.</p>
                    <a href="{reset_link}"
                       style="display:inline-block;background:#B08D57;color:#131A23;padding:12px 24px;
                              border-radius:3px;text-decoration:none;font-weight:600;margin:16px 0;">
                        Reset password
                    </a>
                    <p style="color:#888;font-size:13px;">This link expires in 1 hour. If you didn't request this, you can safely ignore this email.</p>
                </div>
            """
        })

        # Always return success — never reveal whether the email exists
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("FORGOT PASSWORD ERROR:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    token = request.json.get('token')
    new_password = request.json.get('password')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check token exists and hasn't expired
        cur.execute(
            "SELECT email FROM password_resets WHERE token = %s AND expires_at > NOW()",
            (token,)
        )
        row = cur.fetchone()

        if not row:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "message": "This link is invalid or has expired."}), 400

        email = row[0]

        # Update the user's password
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (new_password, email)
        )

        # Delete the used token so it can't be reused
        cur.execute("DELETE FROM password_resets WHERE token = %s", (token,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success", "message": "Password updated successfully."}), 200

    except Exception as e:
        print("RESET PASSWORD ERROR:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/test-send-money', methods=['GET'])
def test_send_money():
    return jsonify({"message": "send money route area exists"})

@app.route('/api/test-accounts-route')
def test_accounts_route():
    return jsonify({"message": "accounts route exists"})

@app.route('/')
def home():
    return "Bank backend is running"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)