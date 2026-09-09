from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.connection import get_db_connection


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() if request.is_json else request.form

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not name or not email or not password or not role:
        return jsonify({"detail": "Missing required fields"}), 400

    allowed_roles = ["Government", "Startup", "Evaluator"]

    if role not in allowed_roles:
        return jsonify({
            "detail": "Invalid user role or public registration not allowed"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return jsonify({
                "detail": "Email already registered"
            }), 400

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, password_hash, role)
        )

        conn.commit()

        return jsonify({
            "message": "User registered successfully"
        }), 201

    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json() if request.is_json else request.form

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "detail": "Email and password required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        if not user or not check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "detail": "Invalid email or password"
            }), 401

        session.clear()

        session["user_id"] = user["id"]
        session["name"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        if request.is_json:
            return jsonify({
                "message": "Login successful",
                "role": user["role"],
                "user_id": user["id"]
            }), 200

        role_dashboards = {
            "Government": "government.dashboard",
            "Startup": "startup.dashboard",
            "Evaluator": "evaluator.dashboard",
            "Admin": "admin.dashboard"
        }

        target_route = role_dashboards.get(
            user["role"],
            "auth.login"
        )

        return redirect(url_for(target_route))

    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()

    if request.is_json:
        return jsonify({
            "message": "Logged out successfully"
        }), 200

    return redirect(url_for("auth.login"))
