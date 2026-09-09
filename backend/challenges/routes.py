from flask import Blueprint, request, jsonify
from database.connection import get_db_connection
from backend.auth.dependencies import require_role


challenges_bp = Blueprint("challenges", __name__, url_prefix="/challenges")


@challenges_bp.route("/", methods=["POST"])
@require_role(["Government"])
def create_challenge():
    data = request.get_json()

    if not data:
        return jsonify({"detail": "JSON data required"}), 400

    title = data.get("title")
    description = data.get("description")
    department = data.get("department")
    requirements = data.get("requirements")
    deadline = data.get("deadline")

    if not title:
        return jsonify({"detail": "Title is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO challenges
            (title, description, department, requirements, deadline)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (title, description, department, requirements, deadline)
        )

        conn.commit()

        return jsonify({
            "message": "Challenge created successfully",
            "challenge_id": cursor.lastrowid
        }), 201

    finally:
        cursor.close()
        conn.close()


@challenges_bp.route("/", methods=["GET"])
@require_role(["Government", "Startup", "Evaluator"])
def get_challenges():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                challenge_id,
                title,
                description,
                department,
                requirements,
                deadline,
                status
            FROM challenges
            ORDER BY challenge_id DESC
            """
        )

        challenges = cursor.fetchall()

        return jsonify(challenges), 200

    finally:
        cursor.close()
        conn.close()


@challenges_bp.route("/<int:challenge_id>", methods=["PUT"])
@require_role(["Government"])
def update_challenge(challenge_id):
    data = request.get_json()

    if not data:
        return jsonify({"detail": "JSON data required"}), 400

    allowed_fields = [
        "title",
        "description",
        "department",
        "requirements",
        "deadline",
        "status"
    ]

    fields = []
    values = []

    for field in allowed_fields:
        if field in data:
            fields.append(f"{field} = %s")
            values.append(data[field])

    if not fields:
        return jsonify({"detail": "No valid fields provided"}), 400

    values.append(challenge_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"""
            UPDATE challenges
            SET {", ".join(fields)}
            WHERE challenge_id = %s
            """,
            tuple(values)
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "detail": "Challenge not found"
            }), 404

        return jsonify({
            "message": "Challenge updated successfully"
        }), 200

    finally:
        cursor.close()
        conn.close()


@challenges_bp.route("/<int:challenge_id>/publish", methods=["PUT"])
@require_role(["Government"])
def publish_challenge(challenge_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE challenges
            SET status = 'Published'
            WHERE challenge_id = %s
            """,
            (challenge_id,)
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "detail": "Challenge not found"
            }), 404

        return jsonify({
            "message": "Challenge published successfully"
        }), 200

    finally:
        cursor.close()
        conn.close()
