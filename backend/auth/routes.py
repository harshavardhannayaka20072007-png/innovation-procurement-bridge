import hmac
import os
import re
import secrets
import sqlite3
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Blueprint, current_app, request, render_template, redirect, url_for, session, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from backend.db import query_db, execute_db

auth_bp = Blueprint('auth', __name__)
EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
MOBILE_RE = re.compile(r'^\+?[1-9]\d{7,14}$')


def _start_session(user):
    """Set only the server-authorized identity attributes in the session."""
    session.clear()
    session['user_id'] = user['user_id']
    session['username'] = user['username']
    session['email'] = user['email']
    session['role'] = user['role']
    session['department'] = user['department']
    session['company_name'] = user['company_name']


def _send_reset_otp(email, otp):
    """Send an OTP only through configured SMTP; fail closed when absent."""
    config = current_app.config
    required = ('SMTP_HOST', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_FROM')
    if not all(config.get(key) for key in required):
        return False
    message = EmailMessage()
    message['Subject'] = 'Innovation Procurement Bridge password reset code'
    message['From'] = config['SMTP_FROM']
    message['To'] = email
    message.set_content(f'Your password-reset code is {otp}. It expires in 10 minutes. Do not share it.')
    with smtplib.SMTP(config['SMTP_HOST'], config['SMTP_PORT'], timeout=10) as smtp:
        smtp.starttls()
        smtp.login(config['SMTP_USERNAME'], config['SMTP_PASSWORD'])
        smtp.send_message(message)
    return True


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and session.get('user_id'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if user and check_password_hash(user['password_hash'], password):
            _start_session(user)

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
    """Allow demo access only when an operator sets and supplies DEMO_SECRET."""
    configured_secret = os.environ.get('DEMO_SECRET')
    supplied_secret = request.args.get('key', '')
    if not configured_secret or not hmac.compare_digest(supplied_secret, configured_secret):
        abort(403)
    if role not in {'government', 'startup', 'evaluator', 'admin'}:
        abort(404)
    user = query_db('SELECT * FROM users WHERE role = ? ORDER BY user_id LIMIT 1', (role,), one=True)
    if not user:
        abort(404)
    _start_session(user)
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['POST'])
def register():
    username = (request.form.get('username') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    password = request.form.get('password') or ''
    company_name = (request.form.get('company_name') or '').strip()[:150]
    mobile_number = (request.form.get('mobile_number') or '').strip()

    if not username or not email or not password or not company_name:
        flash('All fields are required.', 'danger')
        return redirect(url_for('auth.login'))
    if len(username) > 100 or len(email) > 254 or not EMAIL_RE.fullmatch(email):
        flash('Enter a valid name and email address.', 'danger')
        return redirect(url_for('auth.login'))
    if len(password) < 12 or len(password) > 128:
        flash('Password must contain 12 to 128 characters.', 'danger')
        return redirect(url_for('auth.login'))
    if mobile_number and not MOBILE_RE.fullmatch(mobile_number):
        flash('Enter a mobile number in international format, for example +919876543210.', 'danger')
        return redirect(url_for('auth.login'))

    # Self-registration is only allowed for startups.
    # Government, evaluator, and admin accounts must be created by an admin.
    role = 'startup'
    department = None

    if query_db("SELECT user_id FROM users WHERE email = ? OR username = ? OR mobile_number = ?", (email, username, mobile_number or None), one=True):
        flash('Email, username, or mobile number already exists.', 'danger')
        return redirect(url_for('auth.login'))

    pw_hash = generate_password_hash(password)
    try:
        user_id = execute_db(
            'INSERT INTO users (username, email, password_hash, role, department, company_name, mobile_number) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (username, email, pw_hash, role, department, company_name, mobile_number or None)
        )
    except sqlite3.IntegrityError:
        # The database constraints also protect against concurrent registrations.
        flash('Email, username, or mobile number already exists.', 'danger')
        return redirect(url_for('auth.login'))

    _start_session({'user_id': user_id, 'username': username, 'email': email, 'role': role,
                    'department': department, 'company_name': company_name})

    flash('Startup account registered successfully!', 'success')
    return redirect(url_for('startup.dashboard'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        user = query_db('SELECT user_id, email FROM users WHERE email = ?', (email,), one=True)
        # Same response for all requests prevents account enumeration.
        if user:
            otp = f'{secrets.randbelow(1_000_000):06d}'
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=current_app.config['OTP_TTL_SECONDS'])
            execute_db('UPDATE password_reset_otps SET consumed_at = CURRENT_TIMESTAMP WHERE user_id = ? AND consumed_at IS NULL', (user['user_id'],))
            execute_db('INSERT INTO password_reset_otps (user_id, otp_hash, expires_at) VALUES (?, ?, ?)',
                       (user['user_id'], generate_password_hash(otp), expires_at.isoformat()))
            try:
                delivered = _send_reset_otp(user['email'], otp)
            except (OSError, smtplib.SMTPException):
                delivered = False
            if not delivered:
                # Invalidate a code that could not be delivered; it must never be usable.
                execute_db('UPDATE password_reset_otps SET consumed_at = CURRENT_TIMESTAMP WHERE user_id = ? AND consumed_at IS NULL', (user['user_id'],))
        flash('If an account exists, a reset code will be sent to its registered email.', 'info')
        return redirect(url_for('auth.reset_password'))
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        otp = (request.form.get('otp') or '').strip()
        password = request.form.get('password') or ''
        user = query_db('SELECT user_id FROM users WHERE email = ?', (email,), one=True)
        reset = query_db('''SELECT * FROM password_reset_otps WHERE user_id = ? AND consumed_at IS NULL
                            ORDER BY reset_id DESC LIMIT 1''', (user['user_id'],), one=True) if user else None
        valid = False
        if reset and len(password) >= 12 and len(password) <= 128 and reset['attempts'] < current_app.config['OTP_MAX_ATTEMPTS']:
            expires_at = datetime.fromisoformat(reset['expires_at']).replace(tzinfo=timezone.utc) if '+' not in reset['expires_at'] else datetime.fromisoformat(reset['expires_at'])
            valid = expires_at > datetime.now(timezone.utc) and check_password_hash(reset['otp_hash'], otp)
            execute_db('UPDATE password_reset_otps SET attempts = attempts + 1 WHERE reset_id = ?', (reset['reset_id'],))
        if not valid:
            flash('The code is invalid or expired. Request a new one.', 'danger')
            return redirect(url_for('auth.reset_password'))
        execute_db('UPDATE users SET password_hash = ? WHERE user_id = ?', (generate_password_hash(password), user['user_id']))
        execute_db('UPDATE password_reset_otps SET consumed_at = CURRENT_TIMESTAMP WHERE reset_id = ?', (reset['reset_id'],))
        flash('Password changed. You can now sign in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html')


@auth_bp.route('/linkedin/start')
def linkedin_start():
    """Start startup-only LinkedIn OIDC registration when credentials exist."""
    if not current_app.config['LINKEDIN_CLIENT_ID'] or not current_app.config['LINKEDIN_CLIENT_SECRET']:
        abort(503, 'LinkedIn sign-in has not been configured.')
    state = secrets.token_urlsafe(32)
    session['linkedin_oauth_state'] = state
    params = urlencode({'response_type': 'code', 'client_id': current_app.config['LINKEDIN_CLIENT_ID'],
                        'redirect_uri': url_for('auth.linkedin_callback', _external=True),
                        'state': state, 'scope': 'openid profile email'})
    return redirect(f'https://www.linkedin.com/oauth/v2/authorization?{params}')


@auth_bp.route('/linkedin/callback')
def linkedin_callback():
    if not hmac.compare_digest(request.args.get('state', ''), session.pop('linkedin_oauth_state', '')):
        abort(400, 'Invalid LinkedIn sign-in state.')
    code = request.args.get('code')
    if not code:
        abort(400, 'LinkedIn did not return an authorization code.')
    token_data = urlencode({'grant_type': 'authorization_code', 'code': code,
                            'redirect_uri': url_for('auth.linkedin_callback', _external=True),
                            'client_id': current_app.config['LINKEDIN_CLIENT_ID'],
                            'client_secret': current_app.config['LINKEDIN_CLIENT_SECRET']}).encode()
    try:
        with urlopen(Request('https://www.linkedin.com/oauth/v2/accessToken', token_data,
                             {'Content-Type': 'application/x-www-form-urlencoded'}), timeout=10) as response:
            import json
            access_token = json.loads(response.read())['access_token']
        with urlopen(Request('https://api.linkedin.com/v2/userinfo', headers={'Authorization': f'Bearer {access_token}'}), timeout=10) as response:
            import json
            profile = json.loads(response.read())
    except Exception:
        abort(502, 'LinkedIn sign-in could not be completed. Please try again.')
    email = (profile.get('email') or '').strip().lower()
    if not EMAIL_RE.fullmatch(email):
        abort(400, 'LinkedIn did not provide a verified email address.')
    user = query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)
    if user and user['role'] != 'startup':
        abort(403, 'This email belongs to a non-startup account.')
    if not user:
        display_name = (profile.get('name') or email.split('@')[0]).strip()[:100]
        user_id = execute_db('INSERT INTO users (username, email, password_hash, role, company_name) VALUES (?, ?, ?, ?, ?)',
                             (display_name, email, generate_password_hash(secrets.token_urlsafe(32)), 'startup', display_name))
        user = query_db('SELECT * FROM users WHERE user_id = ?', (user_id,), one=True)
    _start_session(user)
    flash('LinkedIn account connected. Please complete your startup profile.', 'success')
    return redirect(url_for('startup.profile'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
