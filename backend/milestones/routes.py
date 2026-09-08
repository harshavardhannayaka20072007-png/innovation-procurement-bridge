from flask import Blueprint, request, jsonify
from database.connection import get_db_connection

milestone_bp = Blueprint("milestone", __name__, url_prefix="/milestones")


@milestone_bp.route("/", methods=["POST"])
def create_milestone():
    data = request.get_json()

    pilot_id = data.get("pilot_id")
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")

    if not pilot_id or not title:
        return jsonify({
            "error": "pilot_id and title are required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO milestones
        (pilot_id, title, description, due_date)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (pilot_id, title, description, due_date)
    )

    conn.commit()

    milestone_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Milestone created successfully",
        "milestone_id": milestone_id
    }), 201

@milestone_bp.route("/pilot/<int:pilot_id>", methods=["GET"])
def get_milestones(pilot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM milestones
        WHERE pilot_id = %s
        ORDER BY milestone_id DESC
    """, (pilot_id,))

    milestones = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(milestones), 200