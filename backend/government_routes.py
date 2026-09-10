from flask import Blueprint, render_template, request, session, redirect, url_for
from backend.db import query_db
from backend.auth.session import require_roles

government_bp = Blueprint('government', __name__, url_prefix='/government')

@government_bp.route('/')
@require_roles('government')
def dashboard():
    challenges_count = query_db("SELECT COUNT(*) as count FROM challenges", one=True)['count']
    closing_soon_count = query_db("SELECT COUNT(*) as count FROM challenges WHERE deadline >= DATE('now') AND status = 'Published'", one=True)['count']
    applications_count = query_db("SELECT COUNT(*) as count FROM applications", one=True)['count']
    under_review_count = query_db("SELECT COUNT(*) as count FROM applications WHERE status IN ('Submitted', 'Under Review')", one=True)['count']
    pilots_count = query_db("SELECT COUNT(*) as count FROM pilots WHERE status = 'Active'", one=True)['count']
    near_completion_count = query_db("SELECT COUNT(*) as count FROM pilots WHERE milestone_progress >= 75", one=True)['count']

    return render_template(
        'government/dashboard.html',
        challenges_count=challenges_count,
        closing_soon_count=closing_soon_count,
        applications_count=applications_count,
        under_review_count=under_review_count,
        pilots_count=pilots_count,
        near_completion_count=near_completion_count
    )

@government_bp.route('/create-challenge')
@require_roles('government')
def create_challenge():
    return render_template('government/create_challenge.html')

@government_bp.route('/challenges')
@require_roles('government')
def challenges():
    search = request.args.get('search', '').strip()
    if search:
        query = """
            SELECT c.*, COUNT(a.application_id) as application_count 
            FROM challenges c 
            LEFT JOIN applications a ON c.challenge_id = a.challenge_id
            WHERE c.title LIKE ? OR c.department LIKE ?
            GROUP BY c.challenge_id
            ORDER BY c.created_at DESC
        """
        challenges_list = query_db(query, (f"%{search}%", f"%{search}%"))
    else:
        query = """
            SELECT c.*, COUNT(a.application_id) as application_count 
            FROM challenges c 
            LEFT JOIN applications a ON c.challenge_id = a.challenge_id
            GROUP BY c.challenge_id
            ORDER BY c.created_at DESC
        """
        challenges_list = query_db(query)

    return render_template('government/challenges.html', challenges=challenges_list)

@government_bp.route('/applications')
@require_roles('government')
def application_list():
    challenge_id = request.args.get('challenge_id', type=int)
    search = request.args.get('search', '').strip()
    
    query = "SELECT * FROM applications WHERE 1=1"
    params = []
    
    if challenge_id:
        query += " AND challenge_id = ?"
        params.append(challenge_id)
        
    if search:
        query += " AND (startup_name LIKE ? OR challenge_title LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
        
    query += " ORDER BY submitted_at DESC"
    apps = query_db(query, tuple(params))
    
    return render_template('government/application_list.html', applications=apps)

@government_bp.route('/applications/<int:application_id>')
@require_roles('government')
def application_details(application_id):
    app_record = query_db("SELECT * FROM applications WHERE application_id = ?", (application_id,), one=True)
    return render_template('government/application_details.html', application=app_record)

@government_bp.route('/pilots')
@require_roles('government')
def pilots():
    pilots_list = query_db("SELECT * FROM pilots ORDER BY start_date DESC")
    return render_template('government/pilots.html', pilots=pilots_list)

@government_bp.route('/performance')
@require_roles('government')
def performance():
    pilot_id = request.args.get('pilot_id', type=int)
    if pilot_id:
        records = query_db("SELECT * FROM performance WHERE pilot_id = ? ORDER BY created_at DESC", (pilot_id,))
    else:
        records = query_db("SELECT * FROM performance ORDER BY created_at DESC")
    return render_template('government/performance.html', performance_records=records)

@government_bp.route('/ranking')
@require_roles('government')
def startup_ranking():
    apps = query_db("SELECT * FROM applications WHERE total_score IS NOT NULL ORDER BY total_score DESC")
    return render_template('government/startup_ranking.html', applications=apps)
