from flask import Blueprint, request, jsonify, redirect, url_for, session, flash
from backend.db import query_db, execute_db

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/', methods=['POST'])
def submit_application():
    challenge_id = request.form.get('challenge_id')
    proposal = request.form.get('proposal')
    description = request.form.get('description', '')
    
    challenge = query_db("SELECT * FROM challenges WHERE challenge_id = ?", (challenge_id,), one=True)
    if not challenge:
        flash("Challenge not found.", "danger")
        return redirect(url_for('startup.challenges'))
        
    startup_id = session.get('user_id', 2)
    startup_name = session.get('company_name') or session.get('username') or 'Startup Applicant'
    
    application_id = execute_db(
        """INSERT INTO applications 
           (challenge_id, startup_id, startup_name, challenge_title, description, proposal, status)
           VALUES (?, ?, ?, ?, ?, ?, 'Submitted')""",
        (challenge_id, startup_id, startup_name, challenge['title'], description, proposal)
    )
    
    flash("Application submitted successfully!", "success")
    return redirect(url_for('startup.applications'))

@applications_bp.route('/<int:application_id>/status', methods=['POST', 'PUT'])
def update_status(application_id):
    if request.is_json:
        data = request.get_json()
        new_status = data.get('status')
    else:
        new_status = request.form.get('status')

    app_record = query_db("SELECT * FROM applications WHERE application_id = ?", (application_id,), one=True)
    if not app_record:
        if request.is_json:
            return jsonify({'error': 'Application not found'}), 404
        flash('Application not found', 'danger')
        return redirect(url_for('government.application_list'))

    execute_db("UPDATE applications SET status = ? WHERE application_id = ?", (new_status, application_id))

    # If approved for pilot, auto-create pilot record if one doesn't exist yet
    if new_status == 'Approved for Pilot':
        existing_pilot = query_db("SELECT pilot_id FROM pilots WHERE application_id = ?", (application_id,), one=True)
        if not existing_pilot:
            execute_db(
                """INSERT INTO pilots (application_id, challenge_id, startup_id, startup_name, challenge_title, status, milestone_progress)
                   VALUES (?, ?, ?, ?, ?, 'Active', 0)""",
                (application_id, app_record['challenge_id'], app_record['startup_id'], app_record['startup_name'], app_record['challenge_title'])
            )

    if request.is_json:
        return jsonify({'message': f'Status updated to {new_status}'}), 200

    flash(f'Application status updated to {new_status}', 'success')
    return redirect(url_for('government.application_details', application_id=application_id))
