from flask import Blueprint, request, jsonify
from database.connection import get_db_connection

decision_bp = Blueprint(
    "decision",
    __name__,
    url_prefix="/decisions"
)


@decision_bp.route("/", methods=["POST"])
def create_decision():
    data = request.get_json()

    pilot_id = data.get("pilot_id")
    decision = data.get("decision")
    remarks = data.get("remarks")

    if not pilot_id or not decision:
        return jsonify({
            "error": "pilot_id and decision are required"
        }), 400

    decision = decision.upper()

    if decision not in ["SCALE", "IMPROVE", "STOP"]:
        return jsonify({
            "error": "Decision must be SCALE, IMPROVE, or STOP"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO decisions
        (pilot_id, decision, remarks)
        VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (pilot_id, decision, remarks)
    )

    conn.commit()

    decision_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Decision recorded successfully",
        "decision_id": decision_id,
        "decision": decision
    }), 201
@decision_bp.route("/pilot/<int:pilot_id>", methods=["GET"])
def get_decisions(pilot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM decisions
        WHERE pilot_id = %s
        ORDER BY decision_id DESC
    """, (pilot_id,))

    decisions = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(decisions), 200