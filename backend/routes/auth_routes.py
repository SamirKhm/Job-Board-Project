from flask import Blueprint, request, render_template, redirect, url_for, session
import bcrypt
import uuid   # ✅ ADD THIS
from db import mysql

auth_bp = Blueprint('auth', __name__)

# ---------------- LOGIN ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, name, email, password, role FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            user_id, name, email_db, stored_password, role = user

            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                session['user_id'] = user_id   # ✅ UUID stored
                session['role'] = role

                if role == 'candidate':
                    return redirect('/candidate-dashboard')
                else:
                    return redirect('/employer-dashboard')
            else:
                return "Invalid password!"
        else:
            return "User not found!"

    return render_template('login.html')


# ---------------- REGISTER ----------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        cur = mysql.connection.cursor()

        # Check existing user
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            return "Email already exists!"

        # ✅ Generate UUID
        user_id = str(uuid.uuid4())

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # ✅ Insert with user_id
        cur.execute(
            "INSERT INTO users (user_id, name, email, password, role) VALUES (%s, %s, %s, %s, %s)",
            (user_id, name, email, hashed_password, role)
        )

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('auth.login'))

    return render_template('registration.html')


# ---------------- LOGOUT ----------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))