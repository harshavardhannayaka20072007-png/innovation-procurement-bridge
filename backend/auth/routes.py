from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from backend.db import query_db, execute_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and session.get('user_id'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role_override = request.form.get('role_override')

        user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
        
        # If user exists or fast demo login
        if user:
            # Check password hash or simple fallback
            valid_pw = check_password_hash(user['password_hash'], password) or password in ['gov123', 'startup123', 'eval123', 'admin123', 'password']
            if valid_pw:
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['email'] = user['email']
                session['role'] = user['role']
                session['department'] = user['department']
                session['company_name'] = user['company_name']
                
                flash(f"Welcome back, {user['username']}!", "success")
                
                if user['role'] == 'government':
                    return redirect(url_for('government.dashboard'))
                elif user['role'] == 'startup':
                    return redirect(url_for('startup.dashboard'))
                elif user['role'] == 'evaluator':
                    return redirect(url_for('evaluator.dashboard'))
                elif user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('index'))
        
        flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')

@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    """Quick demo login helper for testing each role easily."""
    if role not in {'government', 'startup', 'evaluator', 'admin'}:
        return redirect(url_for('auth.login'))
    if session.get('user_id'):
        flash('Log out before choosing a different demo account.', 'warning')
        return redirect(url_for('index'))
    user = query_db("SELECT * FROM users WHERE role = ? LIMIT 1", (role,), one=True)
    if user:
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['role'] = user['role']
        session['department'] = user['department']
        session['company_name'] = user['company_name']
        flash(f"Logged in as Demo {role.capitalize()} User", "info")
        
        if role == 'government':
            return redirect(url_for('government.dashboard'))
        elif role == 'startup':
            return redirect(url_for('startup.dashboard'))
        elif role == 'evaluator':
            return redirect(url_for('evaluator.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))
            
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'startup')
    company_name = request.form.get('company_name')
    department = request.form.get('department')
    
    if query_db("SELECT user_id FROM users WHERE email = ? OR username = ?", (email, username), one=True):
        flash("Email or Username already exists.", "danger")
        return redirect(url_for('auth.login'))
        
    pw_hash = generate_password_hash(password)
    user_id = execute_db(
        "INSERT INTO users (username, email, password_hash, role, department, company_name) VALUES (?, ?, ?, ?, ?, ?)",
        (username, email, pw_hash, role, department, company_name)
    )
    
    session['user_id'] = user_id
    session['username'] = username
    session['email'] = email
    session['role'] = role
    session['department'] = department
    session['company_name'] = company_name
    
    flash("Account registered successfully!", "success")
    if role == 'government':
        return redirect(url_for('government.dashboard'))
    elif role == 'startup':
        return redirect(url_for('startup.dashboard'))
    elif role == 'evaluator':
        return redirect(url_for('evaluator.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
        
    return redirect(url_for('index'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
