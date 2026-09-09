from flask import Blueprint, request, jsonify

from database.connection import get_db_connection
from backend.auth.dependencies import require_role


evidence_bp = Blueprint(
    "evidence",
    __name__,
    url_prefix="/evidence"
)


@evidence_bp.route("/", methods=["POST"])
@require_role(["Startup"])
def submit_evidence():

    data = request.get_json()

    if not data:
        return jsonify({
            "detail": "JSON data required"
        }), 400

    milestone_id = data.get("milestone_id")
    file_name = data.get("file_name")
    file_path = data.get("file_path")
    description = data.get("description")

    if not milestone_id:
        return jsonify({
            "detail": "milestone_id is required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check that the milestone exists
        cursor.execute(
            """
            SELECT milestone_id
            FROM milestones
            WHERE milestone_id = %s
            """,
            (milestone_id,)
        )

        milestone = cursor.fetchone()

        if not milestone:
            return jsonify({
                "detail": "Milestone not found"
            }), 404

        cursor.execute(
            """
            INSERT INTO evidence
            (
                milestone_id,
                file_name,
                file_path,
                description
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                milestone_id,
                file_name,
                file_path,
                description
            )
        )

        conn.commit()

        return jsonify({
            "message": "Evidence submitted successfully",
            "evidence_id": cursor.lastrowid
        }), 201

    finally:
        cursor.close()
        conn.close()


@evidence_bp.route("/milestone/<int:milestone_id>", methods=["GET"])
@require_role(["Government", "Startup", "Evaluator"])
def get_evidence(milestone_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                evidence_id,
                milestone_id,
                file_name,
                file_path,
                description
            FROM evidence
            WHERE milestone_id = %s
            ORDER BY evidence_id DESC
            """,
            (milestone_id,)
        )

        evidence = cursor.fetchall()

        return jsonify(evidence), 200

    finally:
        cursor.close()
        conn.close()