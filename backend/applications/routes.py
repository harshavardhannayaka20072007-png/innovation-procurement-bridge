import sqlite3

from flask import Blueprint, request, jsonify, redirect, url_for, session, flash
from backend.db import query_db, execute_db
from backend.auth.session import require_roles
from backend.ledger import record_event

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/', methods=['POST'])
@require_roles('startup')
def submit_application():
    challenge_id = request.form.get('challenge_id')
    proposal = (request.form.get('proposal') or '').strip()
    description = (request.form.get('description') or '').strip()

    if not challenge_id or not proposal:
        flash('Proposal text is required.', 'danger')
        return redirect(url_for('startup.challenges'))
    # Reject oversize values rather than silently truncating a legal submission.
    if len(proposal) > 5000 or len(description) > 2000:
        flash('Proposal must be at most 5,000 characters and the summary at most 2,000.', 'danger')
        return redirect(url_for('startup.challenges'))

    challenge = query_db("SELECT * FROM challenges WHERE challenge_id = ? AND status = 'Published'", (challenge_id,), one=True)
    if not challenge:
        flash('Challenge not found or is no longer accepting applications.', 'danger')
        return redirect(url_for('startup.challenges'))

    startup_id = session['user_id']

    # Prevent duplicate applications
    existing = query_db(
        'SELECT application_id FROM applications WHERE challenge_id = ? AND startup_id = ?',
        (challenge_id, startup_id), one=True
    )
    if existing:
        flash('You have already submitted an application for this challenge.', 'warning')
        return redirect(url_for('startup.applications'))

    startup_name = session.get('company_name') or session.get('username') or 'Startup Applicant'

    try:
        application_id = execute_db(
            """INSERT INTO applications
               (challenge_id, startup_id, startup_name, challenge_title, description, proposal, status)
               VALUES (?, ?, ?, ?, ?, ?, 'Submitted')""",
            (challenge_id, startup_id, startup_name, challenge['title'], description, proposal)
        )
    except sqlite3.IntegrityError:
        # The unique DB index is the final guard against two concurrent requests.
        flash('You have already submitted an application for this challenge.', 'warning')
        return redirect(url_for('startup.applications'))
    record_event('APPLICATION_SUBMITTED', 'application', application_id, session, {
        'challenge_id': challenge_id, 'challenge_title': challenge['title'], 'startup_name': startup_name
    })
    
    flash("Application submitted successfully!", "success")
    return redirect(url_for('startup.applications'))

@applications_bp.route('/<int:application_id>/status', methods=['POST', 'PUT'])
@require_roles('government')
def update_status(application_id):
    if request.is_json:
        data = request.get_json()
        new_status = data.get('status')
    else:
        new_status = request.form.get('status')

    VALID_STATUSES = {'Submitted', 'Under Review', 'Shortlisted', 'Approved for Pilot', 'Rejected'}

    app_record = query_db('SELECT * FROM applications WHERE application_id = ?', (application_id,), one=True)
    if not app_record:
        if request.is_json:
            return jsonify({'error': 'Application not found'}), 404
        flash('Application not found', 'danger')
        return redirect(url_for('government.application_list'))

    if new_status not in VALID_STATUSES:
        if request.is_json:
            return jsonify({'error': 'Invalid status value.'}), 400
        flash('Invalid status value.', 'danger')
        return redirect(url_for('government.application_details', application_id=application_id))

    execute_db('UPDATE applications SET status = ? WHERE application_id = ?', (new_status, application_id))

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
