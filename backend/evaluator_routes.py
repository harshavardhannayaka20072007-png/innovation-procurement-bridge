from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from backend.db import query_db
from backend.auth.session import require_roles

evaluator_bp = Blueprint('evaluator', __name__, url_prefix='/evaluator')

@evaluator_bp.route('/')
@require_roles('evaluator')
def dashboard():
    pending_apps = query_db("SELECT * FROM applications WHERE status IN ('Submitted', 'Under Review', 'Shortlisted') ORDER BY submitted_at DESC")
    evaluated_apps = query_db("SELECT * FROM applications WHERE total_score IS NOT NULL ORDER BY total_score DESC")
    submitted_milestones = query_db("SELECT m.*, p.startup_name, p.challenge_title FROM milestones m JOIN pilots p ON m.pilot_id = p.pilot_id WHERE m.status = 'Submitted'")
    
    return render_template(
        'evaluator/dashboard.html',
        pending_applications=pending_apps,
        evaluated_applications=evaluated_apps,
        submitted_milestones=submitted_milestones
    )

@evaluator_bp.route('/application-review/<int:application_id>')
@require_roles('evaluator')
def application_review(application_id):
    app_rec = query_db("SELECT * FROM applications WHERE application_id = ?", (application_id,), one=True)
    if not app_rec:
        flash('That application could not be found.', 'warning')
        return redirect(url_for('evaluator.dashboard'))
    ch = query_db("SELECT * FROM challenges WHERE challenge_id = ?", (app_rec['challenge_id'],), one=True)
    previous_evaluation = query_db("SELECT * FROM evaluations WHERE application_id = ? AND evaluator_id = ? ORDER BY created_at DESC LIMIT 1", (application_id, session['user_id']), one=True)
    return render_template('evaluator/application_review.html', application=app_rec, challenge=ch, previous_evaluation=previous_evaluation)

@evaluator_bp.route('/milestone-review')
@require_roles('evaluator')
def milestone_review():
    milestones_list = query_db("SELECT m.*, p.startup_name, p.challenge_title FROM milestones m JOIN pilots p ON m.pilot_id = p.pilot_id ORDER BY m.due_date ASC")
    return render_template('evaluator/milestone_review.html', milestones=milestones_list)

@evaluator_bp.route('/performance-review')
@require_roles('evaluator')
def performance_review():
    records = query_db("SELECT perf.*, p.startup_name, p.challenge_title FROM performance perf JOIN pilots p ON perf.pilot_id = p.pilot_id ORDER BY perf.created_at DESC")
    return render_template('evaluator/performance_review.html', performance_records=records)

@evaluator_bp.route('/recommendation')
@require_roles('evaluator')
def recommendation():
    pilots_list = query_db("SELECT * FROM pilots WHERE status IN ('Active', 'Near Completion', 'Completed')")
    return render_template('evaluator/recommendation.html', pilots=pilots_list)
