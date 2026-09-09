import jwt
import pymysql
from functools import wraps
from flask import request, jsonify, g
from config import settings

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            port=settings.DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"detail": "Could not validate credentials"}), 401
        
        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get("sub")
            if user_id is None:
                return jsonify({"detail": "Could not validate credentials"}), 401
        except jwt.PyJWTError:
            return jsonify({"detail": "Could not validate credentials"}), 401

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT id, name, email, role FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user is None:
                return jsonify({"detail": "Could not validate credentials"}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated

def require_role(allowed_roles: list[str]):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if g.current_user["role"] not in allowed_roles:
                return jsonify({"detail": "You do not have permission to perform this action"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator