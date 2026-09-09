from flask import Blueprint, jsonify, request, session, url_for

from backend.db import query_db

assistant_bp = Blueprint('assistant', __name__)


def _milestone_guidance(role, user_id):
    if role == 'startup':
        rows = query_db('''SELECT m.title, m.status, m.due_date FROM milestones m
                           JOIN pilots p ON p.pilot_id = m.pilot_id WHERE p.startup_id = ? ORDER BY m.due_date''', (user_id,))
        submitted = sum(row['status'] == 'Submitted' for row in rows)
        pending = sum(row['status'] in ('Pending', 'Rejected') for row in rows)
        return f'You have {len(rows)} pilot milestones: {submitted} awaiting verification and {pending} needing action.', url_for('startup.milestones')
    if role == 'evaluator':
        pending = query_db("SELECT COUNT(*) AS total FROM milestones WHERE status = 'Submitted'", one=True)['total']
        return f'There are {pending} submitted milestone proofs awaiting committee verification.', url_for('evaluator.milestone_review')
    pending = query_db("SELECT COUNT(*) AS total FROM milestones WHERE status = 'Submitted'", one=True)['total']
    return f'The programme has {pending} submitted milestone proofs pending verification.', url_for('government.pilots')


@assistant_bp.route('/ask', methods=['POST'])
def ask():
    if not session.get('user_id'):
        return jsonify({'answer': 'Please sign in before using the portal guide.'}), 401

    message = (request.get_json(silent=True) or {}).get('message', '').strip().lower()
    role = session['role']
    user_id = session['user_id']
    if not message:
        return jsonify({'answer': 'Ask me about challenges, applications, pilots, milestones, scores, or the audit ledger.'})

    if any(word in message for word in ('milestone', 'evidence', 'proof', 'upload')):
        answer, destination = _milestone_guidance(role, user_id)
        return jsonify({'answer': answer, 'destination': destination, 'action_label': 'Open milestones'})
    if any(word in message for word in ('pilot', 'progress', 'field')):
        if role == 'startup':
            pilot = query_db('SELECT challenge_title, milestone_progress, status FROM pilots WHERE startup_id = ? ORDER BY start_date DESC LIMIT 1', (user_id,), one=True)
            answer = f"Your current pilot is {pilot['challenge_title']} at {pilot['milestone_progress']}% progress ({pilot['status']})." if pilot else 'You do not have an active pilot yet.'
            return jsonify({'answer': answer, 'destination': url_for('startup.pilot'), 'action_label': 'Open pilot'})
        count = query_db("SELECT COUNT(*) AS total FROM pilots WHERE status IN ('Active', 'Near Completion')", one=True)['total']
        return jsonify({'answer': f'There are {count} active or near-completion pilots being monitored.', 'destination': url_for('government.pilots'), 'action_label': 'View pilots'})
    if any(word in message for word in ('score', 'evaluate', 'evaluation', 'application', 'proposal')):
        if role == 'startup':
            count = query_db('SELECT COUNT(*) AS total FROM applications WHERE startup_id = ?', (user_id,), one=True)['total']
            return jsonify({'answer': f'You have {count} recorded application(s). Status and readiness scores are available in My Applications.', 'destination': url_for('startup.applications'), 'action_label': 'View applications'})
        if role == 'evaluator':
            count = query_db("SELECT COUNT(*) AS total FROM applications WHERE status IN ('Submitted', 'Under Review', 'Shortlisted')", one=True)['total']
            return jsonify({'answer': f'{count} proposal(s) are available for scoring or score review.', 'destination': url_for('evaluator.dashboard'), 'action_label': 'Open evaluation queue'})
        count = query_db('SELECT COUNT(*) AS total FROM applications', one=True)['total']
        return jsonify({'answer': f'The programme has {count} recorded applications. You can inspect their status and readiness scores.', 'destination': url_for('government.application_list'), 'action_label': 'View applications'})
    if any(word in message for word in ('ledger', 'blockchain', 'audit', 'secure', 'security')):
        count = query_db('SELECT COUNT(*) AS total FROM audit_records', one=True)['total']
        return jsonify({'answer': f'The tamper-evident audit ledger currently contains {count} sealed procurement record(s). Ethereum anchoring activates when an operator configures its RPC, contract, and wallet settings.', 'destination': url_for('audit.ledger'), 'action_label': 'Open audit ledger'})

    return jsonify({'answer': 'I can guide you using the live portal record. Try asking about milestones, pilot progress, applications, evaluation scores, or the audit ledger.'})
