from flask import Blueprint, request, jsonify

from database.connection import get_db_connection
from backend.auth.dependencies import require_role


milestone_bp = Blueprint(
    "milestone",
    __name__,
    url_prefix="/milestones"
)


@milestone_bp.route("/", methods=["POST"])
@require_role(["Government"])
def create_milestone():

    data = request.get_json()

    if not data:
        return jsonify({
            "detail": "JSON data required"
        }), 400

    pilot_id = data.get("pilot_id")
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")

    if not pilot_id or not title:
        return jsonify({
            "detail": "pilot_id and title are required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check that the pilot exists
        cursor.execute(
            """
            SELECT pilot_id
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

        cursor.execute(
            """
            INSERT INTO milestones
            (
                pilot_id,
                title,
                description,
                due_date,
                status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                pilot_id,
                title,
                description,
                due_date,
                "Pending"
            )
        )

        conn.commit()

        return jsonify({
            "message": "Milestone created successfully",
            "milestone_id": cursor.lastrowid
        }), 201

    finally:
        cursor.close()
        conn.close()


@milestone_bp.route("/pilot/<int:pilot_id>", methods=["GET"])
@require_role(["Government", "Startup", "Evaluator"])
def get_milestones(pilot_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check that the pilot exists
        cursor.execute(
            """
            SELECT pilot_id
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

        cursor.execute(
            """
            SELECT
                milestone_id,
                pilot_id,
                title,
                description,
                due_date,
                status
            FROM milestones
            WHERE pilot_id = %s
            ORDER BY milestone_id DESC
            """,
            (pilot_id,)
        )

        milestones = cursor.fetchall()

        return jsonify(milestones), 200

    finally:
        cursor.close()
        conn.close()