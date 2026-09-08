from flask import Blueprint, request, jsonify
from database.connection import get_db_connection

performance_bp = Blueprint(
    "performance",
    __name__,
    url_prefix="/performance"
)


@performance_bp.route("/", methods=["POST"])
def create_performance():
    data = request.get_json()

    pilot_id = data.get("pilot_id")
    kpi_name = data.get("kpi_name")
    target_value = data.get("target_value")
    actual_value = data.get("actual_value")
    unit = data.get("unit")
    remarks = data.get("remarks")

    if not pilot_id or not kpi_name:
        return jsonify({
            "error": "pilot_id and kpi_name are required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO performance
        (pilot_id, kpi_name, target_value, actual_value, unit, remarks)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
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

    performance_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Performance KPI recorded successfully",
        "performance_id": performance_id
    }), 201
@performance_bp.route("/pilot/<int:pilot_id>", methods=["GET"])
def get_performance(pilot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM performance
        WHERE pilot_id = %s
        ORDER BY performance_id DESC
    """, (pilot_id,))

    performance = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(performance), 200