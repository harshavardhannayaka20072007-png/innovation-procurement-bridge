"""Build small, role-authorized summaries from live portal data."""
from backend.db import query_db


def _count(sql, args=()):
    return query_db(sql, args, one=True)['total']


def build_user_context(role, user_id):
    """Return only the data this role can safely use in chatbot answers."""
    context = {
        'role': role,
        'open_challenges': _count("SELECT COUNT(*) AS total FROM challenges WHERE status = 'Published'"),
    }
    if role == 'startup':
        context.update({
            'applications': _count('SELECT COUNT(*) AS total FROM applications WHERE startup_id = ?', (user_id,)),
            'pilots': query_db('''SELECT challenge_title, status, milestone_progress FROM pilots
                                   WHERE startup_id = ? ORDER BY start_date DESC LIMIT 3''', (user_id,)),
            'milestones_pending': _count('''SELECT COUNT(*) AS total FROM milestones m
                                             JOIN pilots p ON p.pilot_id = m.pilot_id
                                             WHERE p.startup_id = ? AND m.status IN ('Pending', 'Rejected')''', (user_id,)),
        })
    elif role == 'evaluator':
        context.update({
            'applications_pending': _count("SELECT COUNT(*) AS total FROM applications WHERE status IN ('Submitted', 'Under Review')"),
            'milestones_submitted': _count("SELECT COUNT(*) AS total FROM milestones WHERE status = 'Submitted'"),
        })
    else:  # government and admin have programme-wide operational access
        context.update({
            'challenges': _count('SELECT COUNT(*) AS total FROM challenges'),
            'applications': _count('SELECT COUNT(*) AS total FROM applications'),
            'active_pilots': _count("SELECT COUNT(*) AS total FROM pilots WHERE status IN ('Active', 'Near Completion')"),
            'milestones_submitted': _count("SELECT COUNT(*) AS total FROM milestones WHERE status = 'Submitted'"),
            'audit_records': _count('SELECT COUNT(*) AS total FROM audit_records'),
        })
    return context
