from flask import Blueprint, request, jsonify
from database.connection import get_db_connection

evidence_bp = Blueprint("evidence", __name__, url_prefix="/evidence")


@evidence_bp.route("/", methods=["POST"])
def submit_evidence():
    data = request.get_json()

    milestone_id = data.get("milestone_id")
    file_name = data.get("file_name")
    file_path = data.get("file_path")
    description = data.get("description")

    if not milestone_id:
        return jsonify({
            "error": "milestone_id is required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO evidence
        (milestone_id, file_name, file_path, description)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (milestone_id, file_name, file_path, description)
    )

    conn.commit()

    evidence_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Evidence submitted successfully",
        "evidence_id": evidence_id
    }), 201
@evidence_bp.route("/milestone/<int:milestone_id>", methods=["GET"])
def get_evidence(milestone_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM evidence
        WHERE milestone_id = %s
        ORDER BY evidence_id DESC
    """, (milestone_id,))

    evidence = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(evidence), 200