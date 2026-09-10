from flask import Blueprint, request, render_template, redirect, url_for, session, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from backend.db import query_db, execute_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and session.get('user_id'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()[:254]
        password = request.form.get('password', '').strip()[:128]

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            session['department'] = user['department']
            session['company_name'] = user['company_name']

            flash(f"Welcome back, {user['username']}!", 'success')
            if user['role'] == 'government':
                return redirect(url_for('government.dashboard'))
            elif user['role'] == 'startup':
                return redirect(url_for('startup.dashboard'))
            elif user['role'] == 'evaluator':
                return redirect(url_for('evaluator.dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('index'))

        flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    """Demo login endpoint — disabled in this build."""
    abort(404)

@auth_bp.route('/register', methods=['POST'])
def register():
    username = (request.form.get('username') or '').strip()[:100]
    email = (request.form.get('email') or '').strip()[:254]
    password = (request.form.get('password') or '').strip()[:128]
    company_name = (request.form.get('company_name') or '').strip()[:150]

    if not username or not email or not password:
        flash('All fields are required.', 'danger')
        return redirect(url_for('auth.login'))

    # Self-registration is only allowed for startups.
    # Government, evaluator, and admin accounts must be created by an admin.
    role = 'startup'
    department = None

    if query_db("SELECT user_id FROM users WHERE email = ? OR username = ?", (email, username), one=True):
        flash('Email or username already exists.', 'danger')
        return redirect(url_for('auth.login'))

    pw_hash = generate_password_hash(password)
    user_id = execute_db(
        'INSERT INTO users (username, email, password_hash, role, department, company_name) VALUES (?, ?, ?, ?, ?, ?)',
        (username, email, pw_hash, role, department, company_name)
    )

    session['user_id'] = user_id
    session['username'] = username
    session['email'] = email
    session['role'] = role
    session['department'] = department
    session['company_name'] = company_name

    flash('Startup account registered successfully!', 'success')
    return redirect(url_for('startup.dashboard'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
