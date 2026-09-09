from flask import Blueprint, request, redirect, url_for, flash
from backend.db import query_db, execute_db

milestones_bp = Blueprint('milestones', __name__)

@milestones_bp.route('/submit', methods=['POST'])
def submit_milestone_evidence():
    milestone_id = request.form.get('milestone_id', type=int)
    evidence_file = request.form.get('evidence_file', 'uploaded_proof.pdf')
    
    execute_db(
        "UPDATE milestones SET status = 'Submitted', evidence_file = ? WHERE milestone_id = ?",
        (evidence_file, milestone_id)
    )
    flash("Milestone proof submitted for evaluator review!", "success")
    return redirect(url_for('startup.milestones'))

@milestones_bp.route('/<int:milestone_id>/review', methods=['POST'])
def review_milestone(milestone_id):
    status = request.form.get('status') # 'Approved' or 'Rejected'
    execute_db("UPDATE milestones SET status = ? WHERE milestone_id = ?", (status, milestone_id))
    
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
