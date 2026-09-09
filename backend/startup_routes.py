from flask import Blueprint, render_template, request, session, redirect, url_for
from backend.db import query_db

startup_bp = Blueprint('startup', __name__, url_prefix='/startup')

@startup_bp.route('/')
def dashboard():
    startup_id = session.get('user_id', 2)
    my_applications = query_db("SELECT * FROM applications WHERE startup_id = ? ORDER BY submitted_at DESC", (startup_id,))
    published_challenges = query_db("SELECT * FROM challenges WHERE status = 'Published' ORDER BY created_at DESC LIMIT 5")
    my_pilot = query_db("SELECT * FROM pilots WHERE startup_id = ? ORDER BY start_date DESC LIMIT 1", (startup_id,), one=True)
    
    return render_template(
        'startup/dashboard.html',
        applications=my_applications,
        challenges=published_challenges,
        pilot=my_pilot
    )

@startup_bp.route('/challenges')
def challenges():
    search = request.args.get('search', '').strip()
    if search:
        ch_list = query_db("SELECT * FROM challenges WHERE status = 'Published' AND (title LIKE ? OR department LIKE ?) ORDER BY created_at DESC", (f"%{search}%", f"%{search}%"))
    else:
        ch_list = query_db("SELECT * FROM challenges WHERE status = 'Published' ORDER BY created_at DESC")
    return render_template('startup/challenges.html', challenges=ch_list)

@startup_bp.route('/challenges/<int:challenge_id>')
def challenge_details(challenge_id):
    ch = query_db("SELECT * FROM challenges WHERE challenge_id = ?", (challenge_id,), one=True)
    return render_template('startup/challenge_details.html', challenge=ch)

@startup_bp.route('/apply/<int:challenge_id>')
def apply(challenge_id):
    ch = query_db("SELECT * FROM challenges WHERE challenge_id = ?", (challenge_id,), one=True)
    return render_template('startup/apply.html', challenge=ch)

@startup_bp.route('/applications')
def applications():
    startup_id = session.get('user_id', 2)
    apps = query_db("SELECT * FROM applications WHERE startup_id = ? ORDER BY submitted_at DESC", (startup_id,))
    return render_template('startup/applications.html', applications=apps)

@startup_bp.route('/applications/<int:application_id>')
def application_details(application_id):
    app_rec = query_db("SELECT * FROM applications WHERE application_id = ?", (application_id,), one=True)
    return render_template('startup/application_details.html', application=app_rec)

@startup_bp.route('/pilot')
def pilot():
    startup_id = session.get('user_id', 2)
    pilots_list = query_db("SELECT * FROM pilots WHERE startup_id = ?", (startup_id,))
    return render_template('startup/pilot.html', pilots=pilots_list)

@startup_bp.route('/milestones')
def milestones():
    startup_id = session.get('user_id', 2)
    pilot_rec = query_db("SELECT * FROM pilots WHERE startup_id = ? ORDER BY start_date DESC LIMIT 1", (startup_id,), one=True)
    ms_list = []
    if pilot_rec:
        ms_list = query_db("SELECT * FROM milestones WHERE pilot_id = ? ORDER BY due_date ASC", (pilot_rec['pilot_id'],))
    return render_template('startup/milestones.html', pilot=pilot_rec, milestones=ms_list)

@startup_bp.route('/profile')
def profile():
    user_id = session.get('user_id', 2)
    user_data = query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), one=True)
    return render_template('startup/profile.html', user=user_data)
