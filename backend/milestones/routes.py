import os
import uuid

from flask import Blueprint, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from backend.auth.session import require_roles
from backend.db import query_db, execute_db
from backend.ledger import record_event
from config import Config

milestones_bp = Blueprint('milestones', __name__)

@milestones_bp.route('/submit', methods=['POST'])
@require_roles('startup')
def submit_milestone_evidence():
    milestone_id = request.form.get('milestone_id', type=int)
    milestone = query_db('''SELECT m.*, p.startup_id FROM milestones m
                            JOIN pilots p ON p.pilot_id = m.pilot_id WHERE m.milestone_id = ?''', (milestone_id,), one=True)
    if not milestone or milestone['startup_id'] != session['user_id']:
        flash('You cannot submit evidence for this milestone.', 'danger')
        return redirect(url_for('startup.milestones'))

    uploaded_file = request.files.get('evidence_document')
    if not uploaded_file or not uploaded_file.filename:
        flash('Choose an evidence document before submitting.', 'warning')
        return redirect(url_for('startup.milestones'))
    original_name = secure_filename(uploaded_file.filename)
    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.csv', '.txt'}
    if os.path.splitext(original_name)[1].lower() not in allowed_extensions:
        flash('Use a PDF, image, CSV, or text evidence file.', 'warning')
        return redirect(url_for('startup.milestones'))
    # Flask's request limit is a safety net; enforce the smaller evidence limit too.
    uploaded_file.stream.seek(0, os.SEEK_END)
    file_size = uploaded_file.stream.tell()
    uploaded_file.stream.seek(0)
    if file_size > Config.MAX_EVIDENCE_FILE_SIZE:
        flash('Evidence files must be 10 MB or smaller.', 'warning')
        return redirect(url_for('startup.milestones'))
    # A generated name prevents one upload from overwriting another file with the
    # same client-supplied name.
    evidence_file = f'milestone_{milestone_id}_{uuid.uuid4().hex}_{original_name}'
    evidence_dir = os.path.join(Config.UPLOAD_FOLDER, 'evidence')
    os.makedirs(evidence_dir, exist_ok=True)
    uploaded_file.save(os.path.join(evidence_dir, evidence_file))
    
    execute_db(
        "UPDATE milestones SET status = 'Submitted', evidence_file = ? WHERE milestone_id = ?",
        (evidence_file, milestone_id)
    )
    record_event('MILESTONE_EVIDENCE_SUBMITTED', 'milestone', milestone_id, session, {
        'title': milestone['title'], 'evidence_file': evidence_file, 'pilot_id': milestone['pilot_id']
    })
    flash("Milestone proof submitted for evaluator review!", "success")
    return redirect(url_for('startup.milestones'))

@milestones_bp.route('/<int:milestone_id>/review', methods=['POST'])
@require_roles('evaluator')
def review_milestone(milestone_id):
    status = request.form.get('status')
    if status not in {'Approved', 'Rejected'}:
        flash('Invalid milestone decision.', 'danger')
        return redirect(url_for('evaluator.milestone_review'))
    execute_db("UPDATE milestones SET status = ? WHERE milestone_id = ?", (status, milestone_id))
    record_event('MILESTONE_REVIEWED', 'milestone', milestone_id, session, {
        'status': status
    })
    
    # Recalculate progress for pilot
    milestone = query_db("SELECT pilot_id FROM milestones WHERE milestone_id = ?", (milestone_id,), one=True)
    if milestone:
        pilot_id = milestone['pilot_id']
        total = query_db("SELECT COUNT(*) as cnt FROM milestones WHERE pilot_id = ?", (pilot_id,), one=True)['cnt']
        approved = query_db("SELECT COUNT(*) as cnt FROM milestones WHERE pilot_id = ? AND status = 'Approved'", (pilot_id,), one=True)['cnt']
        
        if total > 0:
            progress = int((approved / total) * 100)
            execute_db("UPDATE pilots SET milestone_progress = ? WHERE pilot_id = ?", (progress, pilot_id))
            
    flash(f"Milestone status updated to {status}!", "success")
    return redirect(url_for('evaluator.milestone_review'))
