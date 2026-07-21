# Meridian Trust — Full-Stack Bank Application

A full-stack, realistic banking web application built to practice modern web development, REST API design, and database integration. 

This project simulates a functional online banking portal where users can register for an account, log securely into their profiles, and view a dynamic dashboard populated with their unique database records.

## 🚀 Live Demo
* **Frontend:** https://arthurjensen.github.io/bank-app/
* **Backend API:** Hosted on Render (Spins down after 15 minutes of inactivity)

---

## 🛠️ Tech Stack

**Frontend (Client-Side)**
* **HTML5 / CSS3:** Custom, responsive UI with a professional banking aesthetic (no external CSS frameworks).
* **Vanilla JavaScript:** Handles dynamic DOM manipulation, form validation, password strength checking, and asynchronous API requests (`fetch`).
* **Hosting:** GitHub Pages

**Backend (Server-Side)**
* **Python 3:** Core server logic.
* **Flask:** Lightweight WSGI web application framework.
* **Flask-CORS:** Handles Cross-Origin Resource Sharing to securely connect the GitHub Pages frontend to the Render backend.
* **Gunicorn:** Python WSGI HTTP Server for production deployment.
* **Hosting:** Render

**Database**
* **PostgreSQL (Neon):** Serverless cloud database.
* **psycopg2:** PostgreSQL database adapter for Python.

---

## ✨ Key Features

* **User Authentication:** Secure login endpoint that verifies user credentials against the cloud database.
* **Account Registration:** Signup flow that creates new user records and handles duplicate email validation.
* **Dynamic Dashboard:** Upon login, the client securely stores the session ID and fetches the user's specific greeting and formatted financial balances via REST API.
* **Interactive UI/UX:** Real-time password strength meter, custom CSS animations, and realistic banking ledger design.
* **Cloud-Native Architecture:** Fully decoupled frontend and backend communicating securely over the public internet.

---

## 📂 Project Structure

```text
├── index.html               # Landing page highlighting features and bank info
├── login.html               # User authentication interface
├── open-checking.html    # Registration page with form validation
├── dashboard.html           # Dynamic dashboard rendering secure user data
├── css/                     # Folder containing component and global styling
├── app.py                   # Main Flask backend application and API routes
├── requirements.txt         # Python dependencies for Render deployment
└── .env                     # Local environment variables (ignored in Git)
```

## 📈 Future Improvements (Roadmap)
* **Implement password hashing** - (e.g., bcrypt) for production-grade security.

* **Add JWT (JSON Web Tokens) or secure session cookies instead of using localStorage for authentication.**

* **Build endpoints to simulate real-time money transfers between accounts.**