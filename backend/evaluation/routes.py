from flask import Blueprint, request, redirect, url_for, session, flash
from backend.auth.session import require_roles
from backend.db import get_db, query_db
from backend.ledger import record_event

evaluation_bp = Blueprint('evaluation', __name__)

@evaluation_bp.route('/submit', methods=['POST'])
@require_roles('evaluator')
def submit_evaluation():
    application_id = request.form.get('application_id', type=int)
    application = query_db("SELECT application_id FROM applications WHERE application_id = ?", (application_id,), one=True) if application_id else None
    if not application:
        flash('The application you tried to evaluate no longer exists.', 'danger')
        return redirect(url_for('evaluator.dashboard'))

    fields = ('eligibility_score', 'technology_score', 'feasibility_score', 'timeline_score', 'experience_score')
    try:
        scores = [int(request.form.get(field, '')) for field in fields]
    except (TypeError, ValueError):
        flash('Enter a whole-number score for every criterion.', 'danger')
        return redirect(url_for('evaluator.application_review', application_id=application_id))
    if any(score < 0 or score > 20 for score in scores):
        flash('Each criterion must be scored from 0 to 20.', 'danger')
        return redirect(url_for('evaluator.application_review', application_id=application_id))

    eligibility, technology, feasibility, timeline, experience = scores
    comments = request.form.get('comments', '').strip()
    if len(comments) > 2000:
        flash('Comments must be 2,000 characters or fewer.', 'danger')
        return redirect(url_for('evaluator.application_review', application_id=application_id))
    evaluator_id = session['user_id']
    total = sum(scores)
    existing = query_db("SELECT evaluation_id FROM evaluations WHERE application_id = ? AND evaluator_id = ? ORDER BY created_at DESC LIMIT 1", (application_id, evaluator_id), one=True)
    # Save the evaluator record and the visible application score as one SQLite
    # transaction: a partial score can never be shown if the other write fails.
    db = get_db()
    try:
        if existing:
            db.execute("""UPDATE evaluations SET eligibility_score = ?, technology_score = ?, feasibility_score = ?,
                       timeline_score = ?, experience_score = ?, total_score = ?, comments = ?, created_at = CURRENT_TIMESTAMP
                       WHERE evaluation_id = ?""", (eligibility, technology, feasibility, timeline, experience, total, comments, existing['evaluation_id']))
        else:
            db.execute("""INSERT INTO evaluations (application_id, evaluator_id, eligibility_score, technology_score,
                       feasibility_score, timeline_score, experience_score, total_score, comments)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (application_id, evaluator_id, eligibility, technology, feasibility, timeline, experience, total, comments))
        db.execute(
            """UPDATE applications
               SET eligibility_score = ?, technology_score = ?, feasibility_score = ?,
                   timeline_score = ?, experience_score = ?, total_score = ?,
                   status = CASE WHEN status = 'Submitted' THEN 'Under Review' ELSE status END
               WHERE application_id = ?""",
            (eligibility, technology, feasibility, timeline, experience, total, application_id)
        )
        db.commit()
    except Exception:
        db.rollback()
        flash('The readiness score could not be saved. No changes were made.', 'danger')
        return redirect(url_for('evaluator.application_review', application_id=application_id))

    record_event('READINESS_SCORE_SAVED', 'application', application_id, session, {
        'total_score': total, 'evaluator_id': evaluator_id
    })

    flash(f"Readiness score saved: {total}/100.", "success")
    return redirect(url_for('evaluator.dashboard'))
