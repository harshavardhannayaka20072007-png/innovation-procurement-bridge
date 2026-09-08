from flask import Blueprint, request, jsonify

from database.connection import get_db_connection


challenges_bp = Blueprint(
    "challenges",
    __name__,
    url_prefix="/challenges"
)


# CREATE CHALLENGE
@challenges_bp.route("/", methods=["POST"])
def create_challenge():

    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    department = data.get("department")
    requirements = data.get("requirements")
    deadline = data.get("deadline")

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO challenges
        (title, description, department, requirements, deadline, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        title,
        description,
        department,
        requirements,
        deadline,
        "Draft"
    ))

    connection.commit()

    challenge_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Challenge created successfully",
        "challenge_id": challenge_id
    }), 201


# VIEW ALL CHALLENGES
@challenges_bp.route("/", methods=["GET"])
def get_challenges():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM challenges")

    challenges = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(challenges)


# EDIT CHALLENGE
@challenges_bp.route("/<int:challenge_id>", methods=["PUT"])
def update_challenge(challenge_id):

    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    department = data.get("department")
    requirements = data.get("requirements")
    deadline = data.get("deadline")

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE challenges
        SET title = %s,
            description = %s,
            department = %s,
            requirements = %s,
            deadline = %s
        WHERE challenge_id = %s
    """

    cursor.execute(query, (
        title,
        description,
        department,
        requirements,
        deadline,
        challenge_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Challenge updated successfully"
    })


# PUBLISH CHALLENGE
@challenges_bp.route("/<int:challenge_id>/publish", methods=["PUT"])
def publish_challenge(challenge_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE challenges
        SET status = %s
        WHERE challenge_id = %s
    """

    cursor.execute(query, (
        "Published",
        challenge_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Challenge published successfully"
    })