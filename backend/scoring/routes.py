from flask import Blueprint, request, jsonify

from database.connection import get_db_connection
from backend.auth.dependencies import require_role


scoring_bp = Blueprint(
    "scoring",
    __name__,
    url_prefix="/scoring"
)


def calculate_completeness_score(application):
    score = 0

    if application.get("solution"):
        score += 20

    if application.get("technology"):
        score += 20

    if application.get("timeline"):
        score += 20

    if application.get("challenge_id"):
        score += 20

    if application.get("startup_id"):
        score += 20

    return score


@scoring_bp.route("/<int:application_id>", methods=["POST"])
@require_role(["Government", "Evaluator"])
def calculate_score(application_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                application_id,
                challenge_id,
                startup_id,
                solution,
                technology,
                timeline
            FROM applications
            WHERE application_id = %s
            """,
            (application_id,)
        )

        application = cursor.fetchone()

        if not application:
            return jsonify({
                "detail": "Application not found"
            }), 404

        total_score = calculate_completeness_score(application)

        cursor.execute(
            """
            SELECT score_id
            FROM scores
            WHERE application_id = %s
            """,
            (application_id,)
        )

        existing_score = cursor.fetchone()

        score_values = (
            20 if application.get("challenge_id") else 0,
            20 if application.get("technology") else 0,
            20 if application.get("solution") else 0,
            20 if application.get("timeline") else 0,
            20 if application.get("startup_id") else 0,
            total_score,
            application_id
        )

        if existing_score:
            cursor.execute(
                """
                UPDATE scores
                SET
                    eligibility_score = %s,
                    technology_score = %s,
                    feasibility_score = %s,
                    timeline_score = %s,
                    experience_score = %s,
                    total_score = %s
                WHERE application_id = %s
                """,
                score_values
            )

            conn.commit()

            return jsonify({
                "message": "Score updated successfully",
                "application_id": application_id,
                "total_score": total_score
            }), 200

        cursor.execute(
            """
            INSERT INTO scores
            (
                application_id,
                eligibility_score,
                technology_score,
                feasibility_score,
                timeline_score,
                experience_score,
                total_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                application_id,
                20 if application.get("challenge_id") else 0,
                20 if application.get("technology") else 0,
                20 if application.get("solution") else 0,
                20 if application.get("timeline") else 0,
                20 if application.get("startup_id") else 0,
                total_score
            )
        )

        conn.commit()

        return jsonify({
            "message": "Score calculated successfully",
            "application_id": application_id,
            "total_score": total_score
        }), 201

    finally:
        cursor.close()
        conn.close()


@scoring_bp.route("/evaluator", methods=["POST"])
@require_role(["Evaluator"])
def evaluator_score():

    data = request.get_json()

    if not data:
        return jsonify({
            "detail": "JSON data required"
        }), 400

    application_id = data.get("application_id")

    if not application_id:
        return jsonify({
            "detail": "application_id is required"
        }), 400

    score_fields = [
        "eligibility_score",
        "technology_score",
        "feasibility_score",
        "timeline_score",
        "experience_score"
    ]

    scores = {}

    for field in score_fields:

        value = data.get(field)

        if value is None:
            return jsonify({
                "detail": f"{field} is required"
            }), 400

        try:
            value = int(value)
        except (TypeError, ValueError):
            return jsonify({
                "detail": f"{field} must be an integer"
            }), 400

        if value < 0 or value > 20:
            return jsonify({
                "detail": f"{field} must be between 0 and 20"
            }), 400

        scores[field] = value

    total_score = sum(scores.values())

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT application_id
            FROM applications
            WHERE application_id = %s
            """,
            (application_id,)
        )

        application = cursor.fetchone()

        if not application:
            return jsonify({
                "detail": "Application not found"
            }), 404

        cursor.execute(
            """
            SELECT score_id
            FROM scores
            WHERE application_id = %s
            """,
            (application_id,)
        )

        existing_score = cursor.fetchone()

        if existing_score:

            cursor.execute(
                """
                UPDATE scores
                SET
                    eligibility_score = %s,
                    technology_score = %s,
                    feasibility_score = %s,
                    timeline_score = %s,
                    experience_score = %s,
                    total_score = %s
                WHERE application_id = %s
                """,
                (
                    scores["eligibility_score"],
                    scores["technology_score"],
                    scores["feasibility_score"],
                    scores["timeline_score"],
                    scores["experience_score"],
                    total_score,
                    application_id
                )
            )

        else:

            cursor.execute(
                """
                INSERT INTO scores
                (
                    application_id,
                    eligibility_score,
                    technology_score,
                    feasibility_score,
                    timeline_score,
                    experience_score,
                    total_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    application_id,
                    scores["eligibility_score"],
                    scores["technology_score"],
                    scores["feasibility_score"],
                    scores["timeline_score"],
                    scores["experience_score"],
                    total_score
                )
            )

        conn.commit()

        return jsonify({
            "message": "Evaluator score saved successfully",
            "application_id": application_id,
            "total_score": total_score
        }), 200

    finally:
        cursor.close()
        conn.close()


@scoring_bp.route("/<int:application_id>", methods=["GET"])
@require_role(["Government", "Evaluator"])
def get_score(application_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                score_id,
                application_id,
                eligibility_score,
                technology_score,
                feasibility_score,
                timeline_score,
                experience_score,
                total_score
            FROM scores
            WHERE application_id = %s
            """,
            (application_id,)
        )

        score = cursor.fetchone()

        if not score:
            return jsonify({
                "detail": "Score not found"
            }), 404

        return jsonify(score), 200

    finally:
        cursor.close()
        conn.close()