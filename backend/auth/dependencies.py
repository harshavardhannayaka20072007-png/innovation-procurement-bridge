from functools import wraps
from flask import session, jsonify, redirect, url_for, request

def login_required(f):
    """Decorator to require session-based authentication for Flask routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({"detail": "Authentication required"}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def require_role(allowed_roles):
    """Decorator to enforce Role-Based Access Control using Flask session."""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            user_role = session.get('role')
            if user_role not in allowed_roles:
                if request.is_json:
                    return jsonify({"detail": "Permission denied"}), 403
                return jsonify({"detail": "You do not have permission to access this page"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator