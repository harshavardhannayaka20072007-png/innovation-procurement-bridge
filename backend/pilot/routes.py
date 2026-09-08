from flask import Blueprint, request, jsonify
from database.connection import get_db_connection

pilot_bp = Blueprint("pilot", __name__, url_prefix="/pilots")


@pilot_bp.route("/", methods=["POST"])
def create_pilot():
    data = request.get_json()

    application_id = data.get("application_id")
    objective = data.get("objective")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not application_id:
        return jsonify({"error": "application_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO pilots
        (application_id, objective, start_date, end_date)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (application_id, objective, start_date, end_date)
    )

    conn.commit()

    pilot_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Pilot created successfully",
        "pilot_id": pilot_id
    }), 201

@pilot_bp.route("/", methods=["GET"])
def get_pilots():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM pilots
        ORDER BY pilot_id DESC
    """)

    pilots = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(pilots), 200


@pilot_bp.route("/<int:pilot_id>", methods=["GET"])
def get_pilot(pilot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM pilots
        WHERE pilot_id = %s
    """, (pilot_id,))

    pilot = cursor.fetchone()

    cursor.close()
    conn.close()

    if not pilot:
        return jsonify({"error": "Pilot not found"}), 404

    return jsonify(pilot), 200