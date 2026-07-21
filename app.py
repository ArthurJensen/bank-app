import os
import secrets

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, first_name FROM users WHERE email = %s AND password_hash = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return jsonify({"status": "success", "message": f"Welcome back, {user[1]}!", "user_id": user[0]}), 200
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
    conn = cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (first_name, email, password_hash, balance) VALUES (%s, %s, %s, %s) RETURNING id", (first_name, email, password, 10000))
        new_user_id = cur.fetchone()[0]
        cur.execute("INSERT INTO accounts (user_id, account_type, account_name, balance) VALUES (%s, %s, %s, %s) RETURNING id, user_id, account_type, account_name, balance", (new_user_id, "checking", "Everyday Checking", 1000))
        new_account = cur.fetchone()
        conn.commit()
        return jsonify({"status": "success", "message": "Account created successfully!", "user_id": new_user_id, "account": {"id": new_account[0], "user_id": new_account[1], "account_type": new_account[2], "account_name": new_account[3], "balance": str(new_account[4])}}), 201
    except psycopg2.errors.UniqueViolation:
        if conn: conn.rollback()
        return jsonify({"status": "error", "message": "Email already exists."}), 400
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()


@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            token = secrets.token_urlsafe(32)
            cur.execute("UPDATE users SET reset_token = %s, reset_token_expiry = NOW() + INTERVAL '60 minutes' WHERE email = %s", (token, email))
            conn.commit()
            reset_link = f"https://bank-app-owi0.onrender.com/reset-password.html?token={token}"

            import resend
            resend.api_key = os.getenv("RESEND_API_KEY")
            resend.Emails.send({
                "from": "Meridian Trust <onboarding@resend.dev>",
                "to": email,
                "subject": "Reset your Meridian Trust password",
                "html": f'''<div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#131A23;color:#EDE6D6;border-radius:6px;">
  <p style="font-size:11px;letter-spacing:0.1em;text-transform:uppercase;color:#C9A56E;">Meridian Trust</p>
  <h2 style="font-family:Georgia,serif;font-size:22px;margin:16px 0 10px;">Reset your password</h2>
  <p style="font-size:15px;color:#E2DAC7;line-height:1.6;margin-bottom:24px;">Click the button below to set a new password. This link expires in <strong>60 minutes</strong>.</p>
  <a href="{reset_link}" style="display:inline-block;background:#B08D57;color:#131A23;padding:13px 26px;border-radius:3px;font-size:15px;font-weight:600;text-decoration:none;">Reset my password</a>
  <p style="margin-top:28px;font-size:12px;color:rgba(237,230,214,0.4);">If you didn't request this, ignore this email.</p>
</div>'''
            })
            print(f"RESET EMAIL SENT TO: {email}")
        cur.close()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print("FORGOT PASSWORD ERROR:", e)
        return jsonify({"status": "success"}), 200


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    password = data.get('password')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE reset_token = %s AND reset_token_expiry > NOW()", (token,))
        user = cur.fetchone()
        if not user:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "message": "Token expired or invalid."}), 400
        cur.execute("UPDATE users SET password_hash = %s, reset_token = NULL, reset_token_expiry = NULL WHERE id = %s", (password, user[0]))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Password updated."}), 200
    except Exception as e:
        print("RESET PASSWORD ERROR:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT first_name, balance FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return jsonify({"status": "success", "first_name": user[0], "balance": str(user[1])}), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/user/<int:user_id>/accounts', methods=['GET'])
def get_user_accounts(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, account_type, account_name, balance FROM accounts WHERE user_id = %s ORDER BY id", (user_id,))
        accounts = cur.fetchall()
        cur.close()
        conn.close()
        account_list = [{"id": a[0], "account_type": a[1], "account_name": a[2], "balance": float(a[3])} for a in accounts]
        total = sum(a["balance"] for a in account_list)
        return jsonify({"status": "success", "accounts": account_list, "total_accounts_balance": total}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "Could not load accounts"}), 500


@app.route('/api/create-account', methods=['POST'])
def create_account():
    data = request.json
    user_id = data.get('user_id')
    account_type = data.get('account_type')
    account_name = data.get('account_name')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO accounts (user_id, account_type, account_name, balance) VALUES (%s, %s, %s, %s) RETURNING id", (user_id, account_type, account_name, 0))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        num = f"47{new_id:07d}"
        formatted = f"{num[:4]} {num[4:7]} {num[7:]}"
        return jsonify({"status": "success", "account_id": new_id, "account_number": formatted}), 201
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
        cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, sender_id))
        cur.execute("UPDATE users SET balance = balance + %s WHERE email = %s", (amount, recipient_email))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Money sent successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/')
def home():
    return "Bank backend is running"

@app.route('/api/test-send-money', methods=['GET'])
def test_send_money():
    return jsonify({"message": "send money route exists"})

@app.route('/api/test-accounts-route')
def test_accounts_route():
    return jsonify({"message": "accounts route exists"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
