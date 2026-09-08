from flask import Blueprint, request, jsonify
from database.connection import get_db_connection

applications_bp = Blueprint(
    "applications",
    __name__,
    url_prefix="/applications"
)


# Submit an application
@applications_bp.route("/", methods=["POST"])
def apply_to_challenge():

    data = request.get_json()

    challenge_id = data.get("challenge_id")
    startup_id = data.get("startup_id")
    solution = data.get("solution")
    technology = data.get("technology")
    timeline = data.get("timeline")

    if not challenge_id or not startup_id:
        return jsonify({
            "error": "challenge_id and startup_id are required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check challenge
    cursor.execute(
        "SELECT status FROM challenges WHERE challenge_id = %s",
        (challenge_id,)
    )

    challenge = cursor.fetchone()

    if not challenge:
        cursor.close()
        conn.close()
        return jsonify({
            "error": "Challenge not found"
        }), 404

    if challenge["status"] != "Published":
        cursor.close()
        conn.close()
        return jsonify({
            "error": "Challenge is not published"
        }), 400

    # Insert application
    cursor.execute(
        """
        INSERT INTO applications
        (challenge_id, startup_id, solution, technology, timeline, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            challenge_id,
            startup_id,
            solution,
            technology,
            timeline,
            "Submitted"
        )
    )

    conn.commit()

    application_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Application submitted successfully",
        "application_id": application_id
    }), 201


# Get applications for a challenge
@applications_bp.route("/challenge/<int:challenge_id>", methods=["GET"])
def get_applications(challenge_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM applications
        WHERE challenge_id = %s
        """,
        (challenge_id,)
    )

    applications = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(applications), 200