from flask import Blueprint, request, jsonify, redirect, url_for, session, flash
from backend.db import query_db, execute_db

evaluation_bp = Blueprint('evaluation', __name__)

@evaluation_bp.route('/submit', methods=['POST'])
def submit_evaluation():
    application_id = request.form.get('application_id', type=int)
    eligibility = int(request.form.get('eligibility_score', 0))
    technology = int(request.form.get('technology_score', 0))
    feasibility = int(request.form.get('feasibility_score', 0))
    timeline = int(request.form.get('timeline_score', 0))
    experience = int(request.form.get('experience_score', 0))
    comments = request.form.get('comments', '')

    evaluator_id = session.get('user_id', 4)
    total = eligibility + technology + feasibility + timeline + experience

    execute_db(
        """INSERT INTO evaluations 
           (application_id, evaluator_id, eligibility_score, technology_score, feasibility_score, timeline_score, experience_score, total_score, comments)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (application_id, evaluator_id, eligibility, technology, feasibility, timeline, experience, total, comments)
    )

    # Update application table with total and individual scores
    execute_db(
        """UPDATE applications 
           SET eligibility_score = ?, technology_score = ?, feasibility_score = ?, 
               timeline_score = ?, experience_score = ?, total_score = ?, status = 'Under Review'
           WHERE application_id = ?""",
        (eligibility, technology, feasibility, timeline, experience, total, application_id)
    )

    flash(f"Evaluation submitted successfully! Readiness Score: {total}/100", "success")
    return redirect(url_for('evaluator.dashboard'))
