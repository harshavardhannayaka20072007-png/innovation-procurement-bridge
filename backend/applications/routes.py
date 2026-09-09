from flask import Blueprint, request, jsonify, session

from database.connection import get_db_connection
from backend.auth.dependencies import require_role


applications_bp = Blueprint(
    "applications",
    __name__,
    url_prefix="/applications"
)


# Submit an application
@applications_bp.route("/", methods=["POST"])
@require_role(["Startup"])
def apply_to_challenge():

    data = request.get_json()

    if not data:
        return jsonify({
            "detail": "JSON data required"
        }), 400

    challenge_id = data.get("challenge_id")
    solution = data.get("solution")
    technology = data.get("technology")
    timeline = data.get("timeline")

    if not challenge_id:
        return jsonify({
            "detail": "challenge_id is required"
        }), 400

    startup_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check whether the challenge exists and is published
        cursor.execute(
            """
            SELECT challenge_id, status
            FROM challenges
            WHERE challenge_id = %s
            """,
            (challenge_id,)
        )

        challenge = cursor.fetchone()

        if not challenge:
            return jsonify({
                "detail": "Challenge not found"
            }), 404

        if challenge["status"] != "Published":
            return jsonify({
                "detail": "Challenge is not published"
            }), 400

        # Prevent duplicate applications
        cursor.execute(
            """
            SELECT application_id
            FROM applications
            WHERE challenge_id = %s
              AND startup_id = %s
            """,
            (challenge_id, startup_id)
        )

        existing_application = cursor.fetchone()

        if existing_application:
            return jsonify({
                "detail": "Startup has already applied to this challenge",
                "application_id": existing_application["application_id"]
            }), 400

        # Create application
        cursor.execute(
            """
            INSERT INTO applications
            (
                challenge_id,
                startup_id,
                solution,
                technology,
                timeline,
                status
            )
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

        return jsonify({
            "message": "Application submitted successfully",
            "application_id": cursor.lastrowid
        }), 201

    finally:
        cursor.close()
        conn.close()


# Get applications for a challenge
@applications_bp.route(
    "/challenge/<int:challenge_id>",
    methods=["GET"]
)
@require_role(["Government", "Evaluator"])
def get_applications(challenge_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                a.application_id,
                a.challenge_id,
                a.startup_id,
                a.solution,
                a.technology,
                a.timeline,
                a.status
            FROM applications a
            WHERE a.challenge_id = %s
            ORDER BY a.application_id DESC
            """,
            (challenge_id,)
        )

        applications = cursor.fetchall()

        return jsonify(applications), 200

    finally:
        cursor.close()
        conn.close()