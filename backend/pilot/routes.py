from flask import Blueprint, request, jsonify

from database.connection import get_db_connection
from backend.auth.dependencies import require_role


pilot_bp = Blueprint(
    "pilot",
    __name__,
    url_prefix="/pilots"
)


@pilot_bp.route("/", methods=["POST"])
@require_role(["Government"])
def create_pilot():

    data = request.get_json()

    if not data:
        return jsonify({
            "detail": "JSON data required"
        }), 400

    application_id = data.get("application_id")
    objective = data.get("objective")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not application_id:
        return jsonify({
            "detail": "application_id is required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check that the application exists
        cursor.execute(
            """
            SELECT application_id
            FROM applications
            WHERE application_id = %s
            """,
            (application_id,)
        )

        application = cursor.fetchone()

        if not application:
            return jsonify({
                "detail": "Application not found"
            }), 404

        # Prevent more than one pilot for the same application
        cursor.execute(
            """
            SELECT pilot_id
            FROM pilots
            WHERE application_id = %s
            """,
            (application_id,)
        )

        existing_pilot = cursor.fetchone()

        if existing_pilot:
            return jsonify({
                "detail": "A pilot already exists for this application",
                "pilot_id": existing_pilot["pilot_id"]
            }), 400

        cursor.execute(
            """
            INSERT INTO pilots
            (
                application_id,
                objective,
                start_date,
                end_date,
                status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                application_id,
                objective,
                start_date,
                end_date,
                "Planned"
            )
        )

        conn.commit()

        return jsonify({
            "message": "Pilot created successfully",
            "pilot_id": cursor.lastrowid
        }), 201

    finally:
        cursor.close()
        conn.close()


@pilot_bp.route("/", methods=["GET"])
@require_role(["Government", "Startup", "Evaluator"])
def get_pilots():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                pilot_id,
                application_id,
                objective,
                start_date,
                end_date,
                status
            FROM pilots
            ORDER BY pilot_id DESC
            """
        )

        pilots = cursor.fetchall()

        return jsonify(pilots), 200

    finally:
        cursor.close()
        conn.close()


@pilot_bp.route("/<int:pilot_id>", methods=["GET"])
@require_role(["Government", "Startup", "Evaluator"])
def get_pilot(pilot_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                pilot_id,
                application_id,
                objective,
                start_date,
                end_date,
                status
            FROM pilots
            WHERE pilot_id = %s
            """,
            (pilot_id,)
        )

        pilot = cursor.fetchone()

        if not pilot:
            return jsonify({
                "detail": "Pilot not found"
            }), 404

        return jsonify(pilot), 200

    finally:
        cursor.close()
        conn.close()