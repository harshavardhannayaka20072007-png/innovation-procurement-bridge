from flask import Blueprint, request, jsonify

from database.connection import get_db_connection
from backend.auth.dependencies import require_role


decision_bp = Blueprint(
    "decision",
    __name__,
    url_prefix="/decisions"
)


@decision_bp.route("/", methods=["POST"])
@require_role(["Government", "Evaluator"])
def create_decision():

    data = request.get_json()

    if not data:
        return jsonify({
            "detail": "JSON data required"
        }), 400

    pilot_id = data.get("pilot_id")
    decision = data.get("decision")
    remarks = data.get("remarks")

    if not pilot_id or not decision:
        return jsonify({
            "detail": "pilot_id and decision are required"
        }), 400

    decision = str(decision).upper().strip()

    if decision not in ["SCALE", "IMPROVE", "STOP"]:
        return jsonify({
            "detail": "Decision must be SCALE, IMPROVE, or STOP"
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
            INSERT INTO decisions
            (
                pilot_id,
                decision,
                remarks
            )
            VALUES (%s, %s, %s)
            """,
            (
                pilot_id,
                decision,
                remarks
            )
        )

        conn.commit()

        return jsonify({
            "message": "Decision recorded successfully",
            "decision_id": cursor.lastrowid,
            "decision": decision
        }), 201

    finally:
        cursor.close()
        conn.close()


@decision_bp.route("/pilot/<int:pilot_id>", methods=["GET"])
@require_role(["Government", "Startup", "Evaluator"])
def get_decisions(pilot_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                decision_id,
                pilot_id,
                decision,
                remarks
            FROM decisions
            WHERE pilot_id = %s
            ORDER BY decision_id DESC
            """,
            (pilot_id,)
        )

        decisions = cursor.fetchall()

        return jsonify(decisions), 200

    finally:
        cursor.close()
        conn.close()