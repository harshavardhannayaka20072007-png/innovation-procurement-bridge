"""Small session-based access helpers for the server-rendered portal."""
from functools import wraps

from flask import flash, redirect, session, url_for


def require_roles(*roles):
    """Require a signed-in user with one of the supplied portal roles."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get('role') not in roles:
                flash('Please sign in with the appropriate portal account to continue.', 'warning')
                return redirect(url_for('auth.login'))
            return view(*args, **kwargs)
        return wrapped
    return decorator
