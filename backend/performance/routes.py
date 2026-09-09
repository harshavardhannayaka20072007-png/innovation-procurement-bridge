from flask import Blueprint, request, jsonify

from database.connection import get_db_connection
from backend.auth.dependencies import require_role


performance_bp = Blueprint(
    "performance",
    __name__,
    url_prefix="/performance"
)


@performance_bp.route("/", methods=["POST"])
@require_role(["Government"])
def create_performance():

    data = request.get_json()

    if not data:
        return jsonify({
            "detail": "JSON data required"
        }), 400

    pilot_id = data.get("pilot_id")
    kpi_name = data.get("kpi_name")
    target_value = data.get("target_value")
    actual_value = data.get("actual_value")
    unit = data.get("unit")
    remarks = data.get("remarks")

    if not pilot_id or not kpi_name:
        return jsonify({
            "detail": "pilot_id and kpi_name are required"
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
            INSERT INTO performance
            (
                pilot_id,
                kpi_name,
                target_value,
                actual_value,
                unit,
                remarks
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                pilot_id,
                kpi_name,
                target_value,
                actual_value,
                unit,
                remarks
            )
        )

        conn.commit()

        return jsonify({
            "message": "Performance KPI recorded successfully",
            "performance_id": cursor.lastrowid
        }), 201

    finally:
        cursor.close()
        conn.close()


@performance_bp.route("/pilot/<int:pilot_id>", methods=["GET"])
@require_role(["Government", "Startup", "Evaluator"])
def get_performance(pilot_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                performance_id,
                pilot_id,
                kpi_name,
                target_value,
                actual_value,
                unit,
                remarks
            FROM performance
            WHERE pilot_id = %s
            ORDER BY performance_id DESC
            """,
            (pilot_id,)
        )

        performance = cursor.fetchall()

        return jsonify(performance), 200

    finally:
        cursor.close()
        conn.close()