from flask import Blueprint, jsonify
from database.connection import get_db_connection

scoring_bp = Blueprint(
    "scoring",
    __name__,
    url_prefix="/scoring"
)


@scoring_bp.route("/<int:application_id>", methods=["POST"])
def calculate_score(application_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get application
    cursor.execute(
        """
        SELECT *
        FROM applications
        WHERE application_id = %s
        """,
        (application_id,)
    )

    application = cursor.fetchone()

    if not application:
        cursor.close()
        conn.close()

        return jsonify({
            "error": "Application not found"
        }), 404

    # Scoring criteria

    # 1. Eligibility
    eligibility_score = 20 if (
        application["solution"] and
        application["technology"] and
        application["timeline"]
    ) else 0

    # 2. Technology Fit
    technology_score = 20 if application["technology"] else 0

    # 3. Feasibility
    feasibility_score = 20 if application["solution"] else 0

    # 4. Timeline
    timeline_score = 20 if application["timeline"] else 0

    # 5. Experience
    # Basic MVP scoring
    experience_score = 20 if application["startup_id"] else 0

    # Total
    total_score = (
        eligibility_score +
        technology_score +
        feasibility_score +
        timeline_score +
        experience_score
    )

    # Store score
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
            eligibility_score,
            technology_score,
            feasibility_score,
            timeline_score,
            experience_score,
            total_score
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Score calculated successfully",
        "application_id": application_id,
        "eligibility_score": eligibility_score,
        "technology_score": technology_score,
        "feasibility_score": feasibility_score,
        "timeline_score": timeline_score,
        "experience_score": experience_score,
        "total_score": total_score
    }), 201